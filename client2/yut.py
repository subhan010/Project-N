from flask import Flask, jsonify,  make_response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/file-content', methods=['GET'])
def get_file_content():

    try:
        with open('test.txt', 'r') as file:
            content = file.read()
        # Create the response and add cache control headers
        response = make_response(jsonify({'content': content}))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'  # For compatibility with older HTTP/1.0 clients
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    # try:
    #     with open('test.txt', 'r') as file:
    #         content = file.read()
    #     return jsonify({'content': content})
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)