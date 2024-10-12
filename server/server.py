import socket
import threading
import json
from db import connect
import time


clients = {}

def check_user_in_db(client_id):
    conn = connect()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE phone_number = %s"
    cursor.execute(query, (client_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_user_to_db(client_data):
    conn = connect()
    cursor = conn.cursor()
    query = "INSERT INTO users (phone_number, username, public_key) VALUES (%s, %s, %s)"
    cursor.execute(query, (client_data['phone_number'], client_data['username'], client_data['public_key']))
    conn.commit()
    conn.close()

def update_public_key(phone_number,public_key):
    conn = connect()
    cursor = conn.cursor()
    query = "UPDATE users SET public_key = %s WHERE phone_number = %s"
    cursor.execute(query, (public_key, phone_number))
    conn.commit()
    conn.close()

def get_public_key(client_id):
    conn = connect()
    cursor = conn.cursor()
    query = "SELECT public_key FROM users WHERE phone_number = %s"
    cursor.execute(query, (client_id,))
    user = cursor.fetchone()
    conn.close()
    return user[0]


def handle_client(client_socket, client_id):
    while True:
        try:
        
            msg = client_socket.recv(1024).decode('utf-8')
            msg=json.loads(msg) 
            print(msg)
            if msg['type']=='sendmsg':
               
                target_id, message = msg.split(':', 1)

                target_id=msg['target']
                target_socket=clients[target_id]
                if target_id in clients:
                    target_socket = clients[target_id]
                    
                    target_socket.send(f"From {client_id}: {message}".encode('utf-8'))
                else:
                    client_socket.send(f"Client {target_id} not found.".encode('utf-8'))

            elif msg['type']=='keyshare':
                key=get_public_key(msg['target'])
                #client_socket = clients['target']
                print("Hellow type is workig in keyshare")
                print(clients[msg['target']])
                print("hellow")
                target_socket=clients[msg['target']]
                target_socket.send(key.encode('utf-8'))


            else:
           
                del clients[client_id]
                break
        except:
          
            del clients[client_id]
            break

    client_socket.close()





def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555))
    server.listen(5)
    print("Server started on port 5555...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr} has been established.")
        
       
        iclient_data = client_socket.recv(1024).decode('utf-8')
        cli_data=json.loads(iclient_data)
        client_id=cli_data['client_id']
        user=check_user_in_db(client_id)

        if user:
            print("User found")
            clients[client_id]=client_socket
            update_public_key(client_id,cli_data['public_key'])
            client_socket.send("Connected".encode('utf-8'))
            # client_thread = threading.Thread(target=handle_client, args=(client_socket, client_id))
            # client_thread.start()
        else:
            print("user not found")
            #client_socket.send("User not found.Sign up first".encode('utf-8'))
            client_socket.send("/signup".encode('utf-8'))
            
            # Receive signup data from the client
            signup_data = client_socket.recv(1024).decode('utf-8')
            client_data = json.loads(signup_data)
            print(client_data)
            
            # Add the new user to the database
            add_user_to_db(client_data)

            # Add the client to the clients list and start the thread
            clients[client_data['phone_number']] = client_socket
            client_socket.send("User created".encode('utf-8'))

            
            # signup_data=client_socket.recv(1024).decode('utf-8')
            # client_data=json.loads(signup_data)
            # add_user_to_db(client_data)
            # clients[client_data['client_id']]=client_socket

        print(clients)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_id))
        client_thread.start()

if __name__ == "__main__":
    main()