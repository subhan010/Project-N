import socket
import threading


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


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 5555))


    client_id = input("Enter your client ID: ")
    client_socket.send(client_id.encode('utf-8'))

  
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    while True:
       
        msg = input("Enter message (target_id:message): ")
        client_socket.send(msg.encode('utf-8'))

if __name__ == "__main__":
    main()