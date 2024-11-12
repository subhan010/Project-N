from flask import Flask, jsonify, make_response
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable SocketIO

@app.route('/')
def index():
    return jsonify({"message": "SocketIO server is running."})

@socketio.on('request_file_content')
def handle_file_content_request():
    try:
        with open('test.txt', 'r') as file:
            content = file.read()
        # Send the file content to the client with a 'file_content' event
        emit('file_content', {'content': content})
    except Exception as e:
        emit('error', {'error': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True)