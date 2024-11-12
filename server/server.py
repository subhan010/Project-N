import base64
import socket
import threading
import json
from db import connect
import bcrypt


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
    print("enterd")
    try:
        conn = connect()
        cursor = conn.cursor()
        query = "INSERT INTO users (phone_number,username,password_hash) VALUES (%s, %s, %s)"
        cursor.execute(query, (client_data['phonenumber'], client_data['username'], base64.b64decode(client_data['password_hash'])))
        conn.commit()
    except Exception as e:
        print(e)
    
    finally:
        
        conn.close()


def update_rsa_key(client_id,key):
    conn = connect()
    cursor = conn.cursor()
    update_query = "UPDATE users SET public_key = %s WHERE phone_number = %s"
    cursor.execute(update_query, (key, client_id))
    conn.commit()



def get_pulic_key(client_id):
    conn = connect()
    cursor = conn.cursor()
    query = "SELECT public_key FROM users WHERE phone_number = %s"
    cursor.execute(query, (client_id,))
    user = cursor.fetchone()
    conn.close()
    return user




def handle_client(client_socket):
    while True:
        
        try:
        
            msg = client_socket.recv(1024).decode('utf-8')
            print("server side ",msg)
           
            dmsg=json.loads(msg)
            print(dmsg)
            client_id=dmsg['phonenumber']
            print(dmsg['ttp'])
           
            # print(dmsg['ttp']=="key")
            # arget_socket.send("MSISMESSAGE".encode('utf-8'))
            if dmsg['ttp'] == "message":
                #dmsg=json.loads(msg)
                #target_id=dmsg['target_id']
                #message=dmsg['message']
                #target_id, message = msg.split(':', 1)
                target_id=dmsg['target_id']
                
                if target_id in clients:
                    target_socket = clients[target_id]
                    
                    target_socket.send(msg.encode('utf-8'))
                else:
                    client_socket.send(f"Client {target_id} not found.".encode('utf-8'))
            
            elif dmsg['ttp'] =="signup":
                
                up=check_user_in_db(dmsg['phonenumber'])
                if( not up):
                    add_user_to_db(dmsg)
                    client_socket.send("User registered".encode('utf-8'))
                client_socket.send("User already present".encode('utf-8'))
            
            
            elif dmsg['ttp'] == "login":
                print("jhlel")
                up=check_user_in_db(dmsg["phonenumber"])
                if (up):
                    tt=bytes(up[5])
                    if(bcrypt.checkpw((dmsg['password']).encode('utf-8'),tt)):
                        client_socket.send("Pass".encode('utf-8'))
                    else:
                        client_socket.send("Fail".encode('utf-8'))
                    




            elif dmsg['ttp'] == "key":
                print("test3")
                #dmsg['message']="key exchnage"
                dmsg['key']=get_pulic_key(dmsg['target_id'])
                print(dmsg)
                dmsg=json.dumps(dmsg)
                client_socket.send(dmsg.encode('utf-8'))
            elif dmsg['ttp'] == "rsakey":
                print("server rsa")
                update_rsa_key(dmsg['id'],dmsg['key'])
            elif dmsg['ttp']== "aeskey":
                print("send aes")
                target_socket=clients[dmsg['id']]
                ty=json.dumps({
                    "key":dmsg['key'],
                    "ttp":"aeskey",
                    "id":dmsg['senderid']
                }
                    
                )
                target_socket.send(ty.encode('utf-8'))
 


            else:
           
                del clients[client_id]
                break
        except:
          
            print("Error")
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

        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()






       
        # client_id = client_socket.recv(1024).decode('utf-8')
        # user=check_user_in_db(client_id)

        # if user:
        #     print("User found")
        #     clients[client_id]=client_socket
        #     client_socket.send("Connected".encode('utf-8'))
        #     # client_thread = threading.Thread(target=handle_client, args=(client_socket, client_id))
        #     # client_thread.start()
        # else:
        #     print("user not found")
        #     #client_socket.send("User not found.Sign up first".encode('utf-8'))
        #     client_socket.send("/signup".encode('utf-8'))
            
        #     # Receive signup data from the client
        #     signup_data = client_socket.recv(1024).decode('utf-8')
        #     client_data = json.loads(signup_data)
        #     print(client_data)
            
        #     # Add the new user to the database
        #     add_user_to_db(client_data)

        #     # Add the client to the clients list and start the thread
        #     clients[client_data['phone_number']] = client_socket
        #     client_socket.send("User created".encode('utf-8'))

            
        #     # signup_data=client_socket.recv(1024).decode('utf-8')
        #     # client_data=json.loads(signup_data)
        #     # add_user_to_db(client_data)
        #     # clients[client_data['client_id']]=client_socket

        # print(clients)
        # client_thread = threading.Thread(target=handle_client, args=(client_socket, client_id))
        # client_thread.start()

if __name__ == "__main__":
    main()