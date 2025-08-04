import os
import sqlite3
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, send
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'connexa-super-secret'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

DB_PATH = "users.db"

# ✅ No need to create directory — DB lives in root
if not os.path.exists(DB_PATH):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        return jsonify({"status": "success", "message": "Registered", "connexa_username": f"{username}.connexa"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Username already exists"}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        if user:
            return jsonify({"status": "success", "connexa_username": f"{username}.connexa"})
        else:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@socketio.on('message')
def handle_message(msg):
    print(f"[Server] Message: {msg}")
    send(msg, broadcast=True)

if __name__ == '__main__':
    print("🌐 Connexa Server Online")
    socketio.run(app, host='0.0.0.0', port=5000)

