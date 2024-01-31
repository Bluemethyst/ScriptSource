try:
    from flask import Flask, request, jsonify, render_template, redirect, url_for
    from apscheduler.schedulers.background import BackgroundScheduler
except ImportError:
    import subprocess
    import time as t
    subprocess.run("pip install Flask")
    t.sleep(10)
    subprocess.run("pip install APScheduler")
    t.sleep(10)
    from flask import Flask, request, jsonify, render_template, redirect, url_for
    from apscheduler.schedulers.background import BackgroundScheduler
from time import time, strftime, localtime
import random
import string
import sqlite3
import datetime


app = Flask(__name__)
pastes = {}

def generate_unique_id():
    return ''.join(random.choices(string.ascii_uppercase, k=5))

def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect('pastes.db') # Creates a database named pastes.db if it doesn't exist
        print(sqlite3.version)
    except Exception as e:
        print(e)
    finally:
        if conn:
            return conn

def create_table(conn):
    try:
        sql = '''CREATE TABLE IF NOT EXISTS pastes (
                    id text PRIMARY KEY,
                    content text NOT NULL,
                    epoch_created_at real NOT NULL,
                    created_at text NOT NULL
                );'''
        c = conn.cursor()
        c.execute(sql)
    except Exception as e:
        print(e)


# Web Interface Routes
@app.route('/', methods=['GET'])
def homepage():
    conn = create_connection()
    create_table(conn)
    return render_template('index.html')

@app.route('/paste', methods=['POST'])
def create_paste():
    content = request.form.get('content')
    unique_id = generate_unique_id()
    while unique_id in pastes:
        unique_id = generate_unique_id()
    timestamp = time()
    pastes[unique_id] = {'content': content, 'epoch_created_at': timestamp, 'created_at': strftime('%Y-%m-%d %H:%M:%S', localtime(timestamp))}
    conn = create_connection()
    with conn:
        sql = '''INSERT INTO pastes(id,content,epoch_created_at,created_at) VALUES(?,?,?,?)'''
        cur = conn.cursor()
        cur.execute(sql, (unique_id, content, timestamp, strftime('%Y-%m-%d %H:%M:%S', localtime(timestamp))))
    return redirect(url_for('get_paste', id=unique_id))


@app.route('/<id>', methods=['GET'])
def get_paste(id):
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM pastes WHERE id=?", (id,))
        row = cur.fetchone()
    if row:
        return render_template('paste.html', content=row[1], epoch_created_at=row[2], id=id)
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
    conn = create_connection()
    with conn:
        sql = '''INSERT INTO pastes(id,content,epoch_created_at,created_at) VALUES(?,?,?,?)'''
        cur = conn.cursor()
        cur.execute(sql, (unique_id, content, timestamp, strftime('%Y-%m-%d %H:%M:%S', localtime(timestamp))))
    return jsonify({'message': 'Paste created successfully', 'id': unique_id}), 201

@app.route('/api/<id>', methods=['GET'])
def api_get_paste(id):
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM pastes WHERE id=?", (id,))
        row = cur.fetchone()
    if row:
        return jsonify({'content': row[1], 'epoch_created_at': row[2], 'created_at': row[3]})
    else:
        return jsonify({'error': 'Paste not found'}), 404

def cleanup():
    conn = create_connection()
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM pastes")
        rows = cur.fetchall()
    for row in rows:
        timestamp = datetime.datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
        if (datetime.datetime.now() - timestamp).total_seconds() > 48*60*60:
            cur.execute("DELETE FROM pastes WHERE id=?", (row[0],))
    print('Cleanup completed')

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(cleanup, 'interval', hours=2)
    scheduler.start()

    app.run(debug=True)