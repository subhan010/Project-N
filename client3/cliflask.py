from flask import Flask, request, jsonify, redirect,url_for
from flask_socketio import SocketIO, emit
import socket
import threading
import json

app = Flask(__name__)
socketio = SocketIO(app)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clients = {}

# Background thread to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            if msg:
                print(msg)
            else:
                break
        except:
            break

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    phone_number = data['phone_number']
    username = data['username']
    public_key = data['public_key']
    
    client_data = {
        "phone_number": phone_number,
        "username": username,
        "public_key": public_key
    }
    
    client_socket = clients[phone_number]
    client_socket.send(json.dumps(client_data).encode('utf-8'))

    return jsonify({"message": "User signed up successfully!"})

@app.route('/connect', methods=['POST'])
def connect():
    data = request.get_json()
    client_id = data['client_id']
    global client_socket
    
    client_socket.connect(('127.0.0.1', 5555))
    
    clients[client_id] = client_socket

    client_socket.send(client_id.encode('utf-8'))
    msg = client_socket.recv(1024).decode('utf-8')

    if msg == "/signup":
        client_data = {
        "phone_number": "132233",
        "username": "hello",
        "public_key": "test123"
    }
        
        client_socket = clients["132233"]
        client_socket.send(json.dumps(client_data).encode('utf-8'))
        

        # Server requests the client to sign up
        # return redirect(url_for('signup', client_id=client_id))
    # else:
    #     # Proceed normally, starting a thread to handle incoming messages
    #     print("h")
    #     receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    #     receive_thread.start()
    #     return "Connected to server"

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    return jsonify({"message": f"Connected to server as {client_id}"})

@app.route('/api/send_message', methods=['POST'])
def api_send_message():
    data = request.get_json()
    global client_socket
    target_id = data.get('target_id')
    message = data.get('message')
    
    if not target_id or not message:
        return jsonify({"error": "target_id and message are required"}), 400
    
    msg=json.dumps({
            "target_id": target_id,
            "message": message
           
        })
    client_socket.send(msg.encode('utf-8'))
    return 

    
    # # Check if the target client is connected
    # if target_id in clients:
    #     socketio.emit('new_message', {'message': message}, room=clients[target_id])
    #     return jsonify({"status": "Message sent successfully!"}), 200
    # else:
    #     return jsonify({"error": "Target client not connected"}), 404


# if __name__ == "__main__":
#     app.run(port=5001,debug=True)
if __name__ == "__main__":
    socketio.run(app, port=5001, debug=True)