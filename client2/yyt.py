# app.py
from flask import Flask
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Sample endpoint to trigger file updates
@app.route('/update-files')
def update_files():
    # Here you would check for file changes, for example, using os.listdir
    updated_files = os.listdir("chats")
    socketio.emit('file_update', {'files': updated_files})
    return "Files updated"

# Start the SocketIO server
if __name__ == '__main__':
    socketio.run(app)