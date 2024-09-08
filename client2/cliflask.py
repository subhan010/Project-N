from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import socket
import threading

app = Flask(__name__)
socketio = SocketIO(app)

clients = {}

# Background thread to receive messages from server
def receive_messages(client_socket):
    while True:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            if msg:
                print(msg)
                socketio.emit('new_message', msg)  # Emit the message to the frontend
            else:
                break
        except:
            break

# Flask route to serve the chat page
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to connect to the server
@app.route('/connect', methods=['POST'])
def connect():
    client_id = request.form['client_id']

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 5555))
    
    clients[client_id] = client_socket  # Store client sockets
    
    client_socket.send(client_id.encode('utf-8'))

    # Start the thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    return "Connected to server"

# Flask-SocketIO route to send messages to the server
@socketio.on('send_message')
def handle_message(data):
    target_id = data['target_id']
    message = data['message']
    
    if target_id in clients:
        client_socket = clients[target_id]
        client_socket.send(message.encode('utf-8'))
        emit('message_sent', f"Message sent to {target_id}")
    else:
        emit('error', "Client not connected")


if __name__ == "__main__":
    socketio.run(app, debug=True)