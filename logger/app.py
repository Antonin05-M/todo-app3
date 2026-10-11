from flask import Flask, request
import datetime
app = Flask(__name__)
@app.route('/log', methods=['POST'])
def log():
    data = request.json
    timestamp = datetime.datetime.now().isoformat()
    status_emoji = {"todo": "⚪", "in_progress": "🟡", "done": "✅"}.get(data['task']['status'], "⚪")
    print(f"[{timestamp}] {status_emoji} Tâche: {data['task']['title']} (ID: {data['task']['id']}, Statut: {data['task']['status']})")
    return '', 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
