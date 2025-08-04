# connexa-server/app.py

import os
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, send
from database import init_db, register_user, login_user
from encryption import decrypt_message  # 🔒 Decryption patch added

# App setup
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = 'connexa-super-secret-key'
CORS(app)

# SocketIO setup
socketio = SocketIO(app, cors_allowed_origins="*")

# DB init
DB_PATH = "data/connexa_users.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
init_db(DB_PATH)

# ──────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required.'}), 400

    if not username.endswith('.connexa'):
        username += '.connexa'

    success, message = register_user(DB_PATH, username, password)
    return jsonify({'success': success, 'message': message}), (200 if success else 400)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required.'}), 400

    success = login_user(DB_PATH, username, password)
    return jsonify({'success': success, 'message': 'Login successful.' if success else 'Invalid credentials.'}), (200 if success else 401)

# ──────────────────────────────────────────────
# SOCKET.IO
# ──────────────────────────────────────────────

@socketio.on('message')
def handle_message(data):
    if isinstance(data, str):
        try:
            data = data.encode()
        except:
            pass

    decrypted = decrypt_message(data)
    print(f"[Server] 🔓 Decrypted: {decrypted}")
    send(decrypted, broadcast=True)

# ──────────────────────────────────────────────
# START
# ──────────────────────────────────────────────

if __name__ == '__main__':
    print("🌐 Connexa Server is running on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000)
