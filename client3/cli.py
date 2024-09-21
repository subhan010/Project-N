from flask import Flask, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import socket
import threading
import json
import sqlite3
import os

app = Flask(__name__)
socketio = SocketIO(app)
conn = sqlite3.connect('chat_application.db')

cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS chats (
                    phonenumber TEXT PRIMARY KEY,
                    chatfilelocation TEXT NOT NULL)''')






client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clients = {}

# Background thread to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            if msg == "/signup":
                print("Server requested signup. Redirecting to sign up.")
            elif msg:
                print(f"Received: {msg}")
                socketio.emit('new_message', msg)  # Emit message to the frontend
            else:
                break
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# Flask route to connect to the server
@app.route('/connect', methods=['POST'])
def connect():
    data = request.get_json()
    client_id = data['client_id']

    phonenumber = client_id
    chatfilelocation = f'{phonenumber}_chat.txt'  

   
    if not os.path.exists(chatfilelocation):
        with open(chatfilelocation, 'w') as file:
            file.write('')  
            cursor.execute('''INSERT INTO user_chats (phonenumber, chatfilelocation) 
                  VALUES (?, ?)''', (phonenumber, chatfilelocation))
            conn.commit()
   


    
    # Connect to the server
    global client_socket
    client_socket.connect(('127.0.0.1', 5555))

    # Store the client's socket for future communication
    clients[client_id] = client_socket

    # Send client ID to the server
    print("connect", client_socket)
    client_socket.send(client_id.encode('utf-8'))

    # Wait for the server's response (either normal connection or sign-up request)
    msg = client_socket.recv(1024).decode('utf-8')

    if msg == "/signup":
        client_data = {
        "phone_number": "122",
        "username": "hello",
        "public_key": "test123"
        }
        
        client_socket = clients["112233"]
        client_socket.send(json.dumps(client_data).encode('utf-8'))
        client_socket.recv(1024).decode('utf-8')
        # Redirect to sign-up route if server requests sign-up
       # return redirect(url_for('signup', client_id="112233"))
  
        # Start thread to handle incoming messages
    
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()
    return jsonify({"message": "Connected to server"})

# Flask route to handle user sign-up
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    phone_number = data['phone_number']
    username = data['username']
    public_key = data['public_key']
    
    # Check if the client is already connected
    if phone_number in clients:
        client_socket = clients[phone_number]

        # Prepare sign-up data as a JSON object
        signup_data = json.dumps({
            "phone_number": phone_number,
            "username": username,
            "public_key": public_key
        })

        # Send sign-up data to the server
        client_socket.send(signup_data.encode('utf-8'))

        return jsonify({"message": "User signed up successfully!"})
    else:
        return jsonify({"error": "Client not connected"}), 400

# Flask-SocketIO route to handle sending messages


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
    print("sendmsg", client_socket)
    client_socket.send(msg.encode('utf-8'))
    return "send"
    # Check if the target client is connected
    
    # if target_id in clients:
    #     socketio.emit('new_message', {'message': message}, room=clients[target_id])
    #     return jsonify({"status": "Message sent successfully!"}), 200
    # else:
    #     return jsonify({"error": "Target client not connected"}), 404

@socketio.on('send_message')
def handle_message(data):
    target_id = data['target_id']
    message = data['message']

    # Find the client and send the message
    if target_id in clients:
        client_socket = clients[target_id]
        client_socket.send(message.encode('utf-8'))
        emit('message_sent', f"Message sent to {target_id}")
    else:
        emit('error', "Target client not connected")

if __name__ == "__main__":
    socketio.run(app, debug=True)