from flask import Flask, jsonify, Response, stream_with_context
import time

app = Flask(__name__)

@app.route('/file-updates')
def file_updates():
    def generate():
        while True:
            # Simulate a file update with a dynamic message every few seconds
            yield f"data: {{'file': 'new_file.txt'}}\n\n"
            time.sleep(5)
    return Response(stream_with_context(generate()), content_type='text/event-stream')

if __name__ == "__main__":
    app.run()  