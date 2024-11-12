import json
import os
from flask import Flask, jsonify, Response, stream_with_context
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route('/file-updates')
def file_updates():
    def generate():
        while True:
            tt=os.listdir('chats')
            # Simulate a file update with a dynamic message every few seconds
            yield json.dumps({"hekki": tt})+"\n\n"#f"data: {{tt}}\n\n"
            time.sleep(5)
    return Response(stream_with_context(generate()), content_type='text/event-stream')

if __name__ == "__main__":
    app.run()



    #     # Track initial file list
    #     initial_files = set(os.listdir('chats'))
    #     print(initial_files)
    #     while True:
    #         # Check for new files
    #         current_files = set(os.listdir('chats'))
    #         if current_files != initial_files:
    #             # Send the updated file list if there's a change
    #             yield f"data: {json.dumps(list(current_files))}\n\n"
    #             initial_files = current_files
    #         time.sleep(3)  # Check every 3 seconds

    # return Response(file_change_stream(), content_type='text/event-stream')