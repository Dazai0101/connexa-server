import os
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, send
from database import init_db, register_user, login_user

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'connexa-super-secret'

socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database
DB_PATH = "data/connexa_users.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
init_db(DB_PATH)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required.'}), 400

    if not username.endswith('.connexa'):
        username += '.connexa'

    success, message = register_user(DB_PATH, username, password)
    return jsonify({'success': success, 'message': message})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required.'}), 400

    success = login_user(DB_PATH, username, password)
    if success:
        return jsonify({'success': True, 'message': 'Login successful.'})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

@socketio.on('message')
def handle_message(msg):
    print(f"[Server] Message: {msg}")
    send(msg, broadcast=True)

if __name__ == '__main__':
    print("🌐 Connexa Server Online")
    socketio.run(app, host='0.0.0.0', port=5000)

