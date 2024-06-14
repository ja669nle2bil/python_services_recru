from celery_conff import build_celery
from flask import Flask
import sqlite3
import time

app = Flask(__name__)

# Configuring Celery
app.config['broker_url'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'

celery = build_celery(app)


@celery.task(bind=True)
def async_add_to_db(self, name, email):
    time.sleep(5)  # Simulate a long-running task

    # Connect to the database
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       email TEXT NOT NULL)''')

    # Insert the data into the database
    cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    return {'status': 'Task completed!'}
