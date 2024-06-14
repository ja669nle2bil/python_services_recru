from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask, BackgroundTasks
from celery_conff import build_celery, celery
from tasks import async_add_to_db
import sqlite3
import uvicorn
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


if not os.path.exists("static"):
    os.makedirs("static")


@app.get("/loaderio-40889867d5cafe6362643ef69af0ce2d.txt")
async def verify_loader_io():
    return FileResponse("static/loaderio-40889867d5cafe6362643ef69af0ce2d.txt")



@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit")
async def submit(name: str = Form(...), email: str = Form(...)):
    conn = sqlite3.connect('mydb.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL)''')

    cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))

    conn.commit()
    conn.close()

    return RedirectResponse("/", status_code=303)

@app.get("/async", response_class=HTMLResponse)
async def async_index(request: Request):
    return templates.TemplateResponse("async_form.html", {"request": request})

@app.post("/async_submit")
async def async_submit(name: str = Form(...), email: str = Form(...)):
    task = async_add_to_db.apply_async(args=[name, email])
    return JSONResponse({}, status_code=202, headers={'Location': f"/status/{task.id}"})

@app.get("/status/{task_id}")
async def taskstatus(task_id: str):
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
        repsonse = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),
        }
    return JSONResponse(response)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
