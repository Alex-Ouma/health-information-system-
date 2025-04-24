from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

# Database initialization
def init_db():
    with sqlite3.connect('health_system.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS programs
                    (id TEXT PRIMARY KEY, name TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS clients
                    (id TEXT PRIMARY KEY, name TEXT, dob TEXT, gender TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS enrollments
                    (client_id TEXT, program_id TEXT,
                     FOREIGN KEY(client_id) REFERENCES clients(id),
                     FOREIGN KEY(program_id) REFERENCES programs(id))''')
        conn.commit()

# Create health program
@app.route('/api/programs', methods=['POST'])
def create_program():
    data = request.get_json()
    program_id = str(uuid.uuid4())
    with sqlite3.connect('health_system.db') as conn:
        c = conn.cursor()
        c.execute('INSERT INTO programs (id, name) VALUES (?, ?)',
                 (program_id, data['name']))
        conn.commit()
    return jsonify({'message': 'Program created successfully', 'id': program_id})

# Get all programs
@app.route('/api/programs', methods=['GET'])
def get_programs():
    with sqlite3.connect('health_system.db') as conn:
        c = conn.cursor()
        c.execute('SELECT id, name FROM programs')
        programs = [{'id': row[0], 'name': row[1]} for row in c.fetchall()]
    return jsonify(programs)

# Register client
@app.route('/api/clients', methods=['POST'])
def register_client():
    data = request.get_json()
    client_id = str(uuid.uuid4())
    with sqlite3.connect('health_system.db') as conn:
        c = conn.cursor()
        c.execute('INSERT INTO clients (id, name, dob, gender) VALUES (?, ?, ?, ?)',
                 (client_id, data['name'], data['dob'], data['gender']))
        conn.commit()
    return jsonify({'message': 'Client registered successfully', 'id': client_id})

# Enroll client in program
@app.route('/api/enrollments', methods=['POST'])
def enroll_client():
    data = request.get_json()
    with sqlite3.connect('health_system.db') as conn:
        c = conn.cursor()
        c.execute('INSERT INTO enrollments (client_id, program_id) VALUES (?, ?)',
                 (data['clientId'], data['programId']))
        conn.commit()
    return jsonify({'message': 'Client enrolled successfully'})

# Search clients
@app.route('/api/clients', methods=['GET'])
def search_clients():
    search_query = request.args.get('search', '')
    with sqlite3.connect('health_system.db') as conn:
        c = conn.cursor()
        query = '''SELECT id, name, dob, gender FROM clients
                  WHERE name LIKE ? OR id LIKE ?'''
        c.execute(query, (f'%{search_query}%', f'%{search_query}%'))
        clients = [{'id': row[0], 'name': row[1], 'dob': row[2], 'gender': row[3]}
                  for row in c.fetchall()]
    return jsonify(clients)

# Get client profile
@app.route('/api/clients/<client_id>', methods=['GET'])
def get_client_profile(client_id):
    with sqlite3.connect('health_system.db') as conn:
        c = conn.cursor()
        # Get client details
        c.execute('SELECT id, name, dob, gender FROM clients WHERE id = ?', (client_id,))
        client = c.fetchone()
        if not client:
            return jsonify({'error': 'Client not found'}), 404

        # Get enrolled programs
        c.execute('''SELECT p.id, p.name FROM programs p
                    JOIN enrollments e ON p.id = e.program_id
                    WHERE e.client_id = ?''', (client_id,))
        programs = [{'id': row[0], 'name': row[1]} for row in c.fetchall()]

        return jsonify({
            'id': client[0],
            'name': client[1],
            'dob': client[2],
            'gender': client[3],
            'programs': programs
        })

if __name__ == '__main__':
    init_db()
    app.run(debug=True)