import socket
import threading


clients = {}


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
        clients[client_id] = client_socket

       
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_id))
        client_thread.start()

if __name__ == "__main__":
    main()