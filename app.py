from flask import Flask, request, jsonify, render_template, redirect, url_for
from time import time, strftime, localtime
import random
import string

app = Flask(__name__)
pastes = {}

def generate_unique_id():
    return ''.join(random.choices(string.ascii_uppercase, k=5))

# Web Interface Routes
@app.route('/', methods=['GET'])
def homepage():
    return render_template('index.html')

@app.route('/paste', methods=['POST'])
def create_paste():
    content = request.form.get('content')
    unique_id = generate_unique_id()
    while unique_id in pastes:
        unique_id = generate_unique_id()
    timestamp = time()
    pastes[unique_id] = {'content': content, 'epoch_created_at': timestamp, 'created_at': strftime('%Y-%m-%d %H:%M:%S', localtime(timestamp))}
    return redirect(url_for('get_paste', id=unique_id))

@app.route('/<id>', methods=['GET'])
def get_paste(id):
    paste = pastes.get(id)
    if paste:
        return render_template('paste.html', content=paste['content'])
    else:
        return 'Paste not found', 404

# API Routes
@app.route('/api/paste', methods=['POST'])
def api_create_paste():
    content = request.json.get('content')
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    unique_id = generate_unique_id()
    while unique_id in pastes:
        unique_id = generate_unique_id()
    timestamp = time()
    pastes[unique_id] = {'content': content, 'epoch_created_at': timestamp, 'created_at': strftime('%Y-%m-%d %H:%M:%S', localtime(timestamp))}
    return jsonify({'message': 'Paste created successfully', 'id': unique_id}), 201

@app.route('/api/<id>', methods=['GET'])
def api_get_paste(id):
    paste = pastes.get(id)
    if paste:
        return jsonify({'content': paste['content'], 'epoch_created_at': paste['epoch_created_at'], 'created_at': paste['created_at']})
    else:
        return jsonify({'error': 'Paste not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)