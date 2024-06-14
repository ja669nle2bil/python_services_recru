from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import sqlite3
from celery_conff import build_celery
from tasks import async_add_to_db
import time

app = Flask(__name__)


# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['broker_url'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'

celery = build_celery(app)

@app.route("/loaderio-365232a6a07e4495824a89ca823135a3.html/")
def verify_loaderiox():
    return send_from_directory('.', 'loaderio-365232a6a07e4495824a89ca823135a3.txt')

@app.route("/loaderio-365232a6a07e4495824a89ca823135a3/")
def verify_loaderio():
    return send_from_directory('.', 'loaderio-365232a6a07e4495824a89ca823135a3.txt')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        conn = sqlite3.connect('mydatabase.db')
        cursor = conn.cursor()

        # other way of using conn.execute()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL,
                           email TEXT NOT NULL)''')


        cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))


        conn.commit()
        conn.close()


        return redirect('/')


# async form.
@app.route('/async')
def async_index():
    return render_template('async_form.html')

@app.route('/async_submit', methods=['POST'])
def async_submit():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        task = async_add_to_db.apply_async(args=[name, email])
        return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

# @celery.task(bind=True)
# def async_add_to_db(self, name, email):
#     time.sleep(5)
#
#     conn = sqlite3.connect('mydatabase.db')
#     cursor = conn.cursor()
#
#     cursor.execute('''CREATE TABLE IF NOT EXISTS users
#                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                        name TEXT NOT NULL,
#                        email TEXT NOT NULL)''')
#
#     cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
#
#     conn.commit()
#     conn.close()
#
#     return {'status': 'Task completed!'}

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = async_add_to_db.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),
        }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
