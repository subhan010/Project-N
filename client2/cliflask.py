from flask import Flask, render_template, redirect, url_for, request, flash
import socket

app = Flask(__name__)


# Global variable to store client socket
client_socket = None

@app.route('/')
def home():
    return render_template('home.html')  # Main page

@app.route('/connect', methods=['POST'])
def connect():
    global client_socket
    client_id = request.form['client_id']
    
    # Connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('server_ip', 5555))
    client_socket.send(client_id.encode('utf-8'))

    # Receive response from server
    response = client_socket.recv(1024).decode('utf-8')
    
    if response == "User not found. Please sign up.":
        flash("User not found. Please sign up.")
        return redirect(url_for('signup'))  # Redirect to signup page
    else:
        # Proceed with the chat functionality (not shown)
        return render_template('chat.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')  # Render signup form

@app.route('/create_account', methods=['POST'])
def create_account():
    global client_socket
    
    # Get the signup data from form
    client_id = request.form['client_id']
    username = request.form['username']
    password = request.form['password']
    
    # Prepare data to send to the server
    client_data = {
        'client_id': client_id,
        'username': username,
        'password': password
    }
    
    # Send signup data to the server (assuming server expects JSON)
    import json
    client_socket.send(json.dumps(client_data).encode('utf-8'))

    # Redirect to the chat page after signup
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)