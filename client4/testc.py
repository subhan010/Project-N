from flask import Flask, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import socket
import threading
import json
import sqlite3
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64

from encrypt_aes_rsa import(
    generate_rsa_key_pair,
    encrypt_aes_key,
    decrypt_aes_key,
    generate_aes_key,
    encrypt_msg,
    decrypt_msg
)

clients = {}
privatekey=''
publickey=''

if not os.path.exists("private_key.pem") or not os.path.exists("public_key.pem"):
    privatekey, publickey=generate_rsa_key_pair()
    with open("private_key.pem", "wb") as private_file:
        private_file.write(
            privatekey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(b"kkrhaitiyar")
        )
    )


    with open("public_key.pem", "wb") as public_file:
        public_file.write(
            publickey.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
else:
    with open("private_key.pem", "rb") as private_file:
        privatekey = serialization.load_pem_private_key(
        private_file.read(),
        password=b"kkrhaitiyar",
        backend=default_backend()
    )
        
    with open("public_key.pem", "rb") as public_file:
        publickey = serialization.load_pem_public_key(
        public_file.read(),
        backend=default_backend()
    )



    

app = Flask(__name__)
socketio = SocketIO(app)
conn = sqlite3.connect('chat_application.db', check_same_thread=False)

cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS chats (
                    phonenumber TEXT PRIMARY KEY,
                    chatfilelocation TEXT NOT NULL,
               rsakey TEXT NULL,
               aeskey TEXT  NULL)''')


cursor.execute('''CREATE TABLE IF NOT EXISTS keys (
                    phonenumber TEXT PRIMARY KEY,
                    publickey TEXT NOT NULL,
               privatekey TEXT NULL)''')






def user_in_local_db(id):
    print("db check ",id)
    phonenumber = id
    chatfilelocation = f'{phonenumber}/chats.txt'  


    if not os.path.exists(chatfilelocation):
        with open(chatfilelocation, 'w') as file:
            file.write('')  
            cursor.execute('''INSERT INTO chats (phonenumber, chatfilelocation) 
                  VALUES (?, ?)''', (phonenumber, chatfilelocation))
            conn.commit()

def key_present(id):
    print("check key")
    # conn = connect()
    cursor = conn.cursor()
    query = "SELECT * FROM keys WHERE phonenumber = ?"
    cursor.execute(query, (id,))
    user = cursor.fetchone()
    # conn.close()
    return user

def add_publickey(id, publickey):
    print("add key")
    # conn = connect()
    cursor = conn.cursor()
    query = "INSERT INTO users (phone_number, publickey) VALUES (%s, %s, %s)"
    cursor.execute(query, (id, publickey, privatekey))
    conn.commit()
    # conn.close()


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def get_public_key(id):
    print("test2")
    key=json.dumps({
    "ttp":"key",
      "target_id":id,
      "key":""
    })
    client_socket.send(key.encode('utf-8'))
def send_public_key_to_server(id):
    print("test43")
    pkey=None
    with open("public_key.pem", "rb") as public_file:
        rsa_public = public_file.read()
        public_key_string = rsa_public.decode('utf-8')
        pkey=json.dumps({
            "ttp":"rsakey",
            "id":id,
            "key":public_key_string

        })
    client_socket.send(pkey.encode('utf-8'))

def send_key_to_client(key,id):
    print("ttes")
    kkey=json.dumps({
        "ttp":"aeskey",
        "id":id,
        "key":key,
        "senderid":"338899"

    })
    client_socket.send(kkey.encode('utf-8'))


    




# Background thread to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            dmsg=json.loads(msg)
            print(dmsg)
            if msg == "/signup":
                print("Server requested signup. Redirecting to sign up.")
            elif dmsg['ttp']=="message":
                smsg=json.loads(msg)
                user_in_local_db(smsg['sender'])
                
                print("Test receiver")
                print("hellow ",dmsg['target_id'])
                sender=dmsg['sender']
               
                if sender not in clients:
                    print("eenter")
                    with open(f"{sender}/aes_key.pem", "r") as file:
                        lines = file.readlines()
                        key_data = "".join(line.strip() for line in lines if "BEGIN" not in line and "END" not in line)
                        aes_key = base64.b64decode(key_data)
                        
                        clients[sender]=aes_key
                        
                
                print(type(clients[sender]))
                print("enc",dmsg['message'])
                decmsg=base64.b64decode(dmsg['message'])
                print(decmsg)
                tye=decrypt_msg(decmsg,clients[sender])
                
                with open(f"{smsg['sender']}/chats.txt", 'a') as file:
                    file.write(tye.decode('utf-8')+'\n')
                client_socket.send("ack".encode('utf-8'))
                

            elif dmsg["ttp"]=="key":
                print(dmsg)
                
                with open(f"{dmsg['target_id']}/public_key.pem", "w") as file:
                    file.write(dmsg['key'][0])
                    aes_key = base64.b64decode(dmsg['key'][0])
                    clients[dmsg['target_id']]=aes_key
                print("keyreceived")
            elif dmsg['ttp']=="aeskey":
               
                if not os.path.exists(f'{dmsg["id"]}/aes_key.pem'):
                    if not os.path.exists(f'{dmsg["id"]}'):
                        os.makedirs(f'{dmsg["id"]}')

                    
                    privatekey=None
                    with open(f"private_key.pem", "rb") as file:
                        privatekey = serialization.load_pem_private_key(
                                    file.read(),
                                    password=b"kkrhaitiyar"  
                                )
                    print(dmsg["key"])
                    deckey=base64.b64decode(dmsg["key"])
                    print(deckey)
                    
                    decryptedkey=decrypt_aes_key(deckey,privatekey)
                    decoded_key = base64.b64encode(decryptedkey).decode('utf-8')
                    with open(f"{dmsg["id"]}/aes_key.pem", "w") as file:
                        file.write("-----BEGIN AES KEY-----\n")
                        file.write(decoded_key)
                        file.write("\n-----END AES KEY-----\n")


                

                # socketio.emit('new_message', msg)  # Emit message to the frontend
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

    # Connect to the server
    global client_socket
    client_socket.connect(('0.tcp.in.ngrok.io', 14586))
    #client_socket.connect(('127.0.0.1', 5555))

    # Store the client's socket for future communication
    clients[client_id] = client_socket

    # Send client ID to the server
    print("connect", client_socket)
    client_socket.send(client_id.encode('utf-8'))

    # Wait for the server's response (either normal connection or sign-up request)
    msg = client_socket.recv(1024).decode('utf-8')

    if msg == "/signup":
        client_data = {
        "phone_number": "338899",
        "username": "hello",
        "public_key": "test123"
        }
        
        client_socket = clients["338899"]
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


@app.route('/updatekey', methods=['POST'])
def updatekey():
    
    data = request.get_json()
    id=data.get('id')
    send_public_key_to_server(id)
    return "done"

@app.route('/api/send_message', methods=['POST'])
def api_send_message():
    data = request.get_json()
    global client_socket
    target_id = data.get('target_id')
    message = data.get('message')
    ttp = data.get('ttp')
    if not os.path.exists(f'{target_id}'):
        os.makedirs(f'{target_id}')
    

    if not os.path.exists(f'{target_id}/public_key.pem'):
        get_public_key(target_id)
        
    
    if not os.path.exists(f'{target_id}/aes_key.pem'):
        privatekey=generate_aes_key()
        print(privatekey)
        encoded_key = base64.b64encode(privatekey).decode('utf-8')
        with open(f"{target_id}/aes_key.pem", "w") as file:
            file.write("-----BEGIN AES KEY-----\n")
            file.write(encoded_key)
            file.write("\n-----END AES KEY-----\n")
    
    
    
    if target_id not in clients:
        public_key=None
        with open(f'{target_id}/public_key.pem', "rb") as file:
            public_key = serialization.load_pem_public_key(
            file.read()
                )
        
        with open(f'{target_id}/aes_key.pem', "r") as file:
            lines = file.readlines()
            key_data = "".join(line.strip() for line in lines if "BEGIN" not in line and "END" not in line)
            aes_key = base64.b64decode(key_data)
            clients[target_id]=aes_key
       

        encrypted_key = encrypt_aes_key(aes_key,public_key)
        
        enckey=base64.b64encode(encrypted_key).decode('utf-8')
        send_key_to_client(enckey,target_id)

        



    
   
    if not target_id or not message:
        return jsonify({"error": "target_id and message are required"}), 400
    
    with open(f"{target_id}/chats.txt", 'a') as file:
        file.write(message+'\n')

    encmsg=encrypt_msg(clients[target_id],message)
    print("encrypted,",encmsg)
    # decmsg=decrypt_msg(encmsg,clients[target_id])
    # print("decrypted",decmsg)
    encmsg=base64.b64encode(encmsg).decode('utf-8')
    print("encomsg,",encmsg)
    msg=json.dumps({
            "target_id": target_id,
            "message": encmsg,
            "ttp":"message",
            "sender":"338899"
           
        })
    print(client_socket)
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
    socketio.run(app,port=5003, debug=True)