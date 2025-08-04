import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, send
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'connexa-super-secret'

# Enable CORS for cross-origin client access
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# === DB SETUP ===
DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

init_db()

# === ROUTES ===

@app.route("/")
def home():
    return render_template("index.html")  # basic server status page

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Missing fields"}), 400

    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone():
            return jsonify({"success": False, "message": "User already exists"}), 409
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return jsonify({"success": True, "message": "Registered successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Missing fields"}), 400

    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        if result and result[0] == password:
            return jsonify({"success": True, "message": "Login successful"}), 200
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

# === SOCKET.IO ===

@socketio.on('message')
def handle_message(msg):
    print(f"[Server] Message: {msg}")
    send(msg, broadcast=True)

# === MAIN ===

if __name__ == '__main__':
    print("🌐 Connexa web server live on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000)
