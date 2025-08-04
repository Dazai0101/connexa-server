import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, send
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'connexa-super-secret'

# CORS support for both SocketIO and HTTP
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def home():
    return render_template('index.html')

@socketio.on('message')
def handle_message(msg):
    print(f"[Server] Message: {msg}")
    send(msg, broadcast=True)

if __name__ == '__main__':
    print("🌐 Connexa web server live on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000)
