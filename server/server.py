import socket
import threading
import json
from config.db import connect


clients = {}

def check_user_in_db(client_id):
    conn = connect()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE client_id = %s"
    cursor.execute(query, (client_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_user_to_db(client_data):
    conn = connect()
    cursor = conn.cursor()
    query = "INSERT INTO users (client_id, username, password) VALUES (%s, %s, %s)"
    cursor.execute(query, (client_data['client_id'], client_data['username'], client_data['password']))
    conn.commit()
    conn.close()




def handle_client(client_socket, client_id):
    while True:
        try:
        
            msg = client_socket.recv(1024).decode('utf-8')
            if msg:
               
                target_id, message = msg.split(':', 1)

                
                if target_id in clients:
                    target_socket = clients[target_id]
                    
                    target_socket.send(f"From {client_id}: {message}".encode('utf-8'))
                else:
                    client_socket.send(f"Client {target_id} not found.".encode('utf-8'))
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

       
        client_id = client_socket.recv(1024).decode('utf-8')
        user=check_user_in_db(client_id)

        if user:
            print("User found")
            clients[client_id]=client_socket
        else:
            client_socket.send("User not found.Sign up first")
            signup_data=client_socket.recv(1024).decode('utf-8')
            client_data=json.loads(signup_data)
            add_user_to_db(client_data)
            clients[client_data['client_id']]=client_socket

       
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_id))
        client_thread.start()

if __name__ == "__main__":
    main()