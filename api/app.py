from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os
import requests
import time

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT')
}

def init_db():
    max_retries = 10
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT DEFAULT 'todo',
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            conn.commit()
            cur.close()
            conn.close()
            print("Base de données initialisée")
            return
        except psycopg2.OperationalError as e:
            print(f"Tentative {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute('SELECT id, title, status, created_at FROM tasks ORDER BY created_at DESC')
    tasks = [{
        'id': row[0],
        'title': row[1],
        'status': row[2],
        'created_at': row[3].isoformat() if row[3] else None
    } for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Le titre est obligatoire'}), 400
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (title, status) VALUES (%s, %s) RETURNING id, title, status, created_at',
                (data['title'], 'todo'))
    row = cur.fetchone()
    task = {
        'id': row[0],
        'title': row[1],
        'status': row[2],
        'created_at': row[3].isoformat() if row[3] else None
    }
    conn.commit()
    cur.close()
    conn.close()
    requests.post('http://logger:5001/log', json={'task': task}, timeout=2)
    return jsonify(task), 201

@app.route('/tasks/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Le statut est obligatoire'}), 400
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute('UPDATE tasks SET status = %s WHERE id = %s RETURNING id, title, status, created_at',
                (data['status'], task_id))
    row = cur.fetchone()
    if not row:
        return jsonify({'error': 'Tâche non trouvée'}), 404
    task = {
        'id': row[0],
        'title': row[1],
        'status': row[2],
        'created_at': row[3].isoformat() if row[3] else None
    }
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(task), 200

init_db()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
