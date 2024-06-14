from celery_conff import celery, build_celery
import sqlite3
import time
from celery_conff import celery
#
# app = Flask(__name__)
#
# # Configuring Celery
# app.config['broker_url'] = 'redis://localhost:6379/0'
# app.config['result_backend'] = 'redis://localhost:6379/0'
#
# celery = build_celery(app)
@celery.task(bind=True)
def async_add_to_db(self, name, email):
    time.sleep(5)


    conn = sqlite3.connect('mydb.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       email TEXT NOT NULL)''')


    cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))


    conn.commit()
    conn.close()

    return {'status': 'Task completed!'}
