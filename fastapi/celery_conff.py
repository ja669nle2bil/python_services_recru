from celery import Celery
def build_celery():     #rebuild over fastapi.
    celery = Celery(
        "app",
        # backend=app.config['CELERY_RESULT_BACKEND'],
        # broker=app.config['CELERY_BROKER_URL']
        # backend=['result_backend'],
        # broker=['broker_url']
        backend="redis://localhost:6379/0",
        broker="redis://localhost:6379/0"
    )
    celery.conf.broker_connection_retry_on_startup = True #warn fix
    celery.conf.update({"result_backend":"redis://localhost:6379/0"})
    return celery

celery = build_celery()
