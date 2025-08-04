
# connexa-server/app.py

import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, send, emit, join_room
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'connexa-super-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

DB_PATH = "users.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )''')

init_db()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = data.get("username")
    pw = data.get("password")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (user,))
        row = cursor.fetchone()
        if row and row[0] == pw:
            return jsonify(success=True, message="Login successful", username=user + ".connexa")
        return jsonify(success=False, message="Invalid credentials")

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = data.get("username")
    pw = data.get("password")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=?", (user,))
        if cursor.fetchone():
            return jsonify(success=False, message="Username already taken.")
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pw))
        conn.commit()
        return jsonify(success=True, message="Account created", username=user + ".connexa")

@socketio.on("join_room")
def handle_join(data):
    username = data.get("username")
    room = data.get("room")
    join_room(room)
    send(f"{username} joined the chat.", room=room)

@socketio.on("send_message")
def handle_send(data):
    room = data.get("room")
    msg = data.get("message")
    sender = data.get("sender")
    emit("receive_message", {"sender": sender, "message": msg}, room=room)

if __name__ == "__main__":
    print("🌐 Connexa Server Online")
    socketio.run(app, host="0.0.0.0", port=5000)
