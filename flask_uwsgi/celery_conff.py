from celery import Celery
def build_celery(app):
    celery = Celery(
        app.import_name,
        # backend=app.config['CELERY_RESULT_BACKEND'],
        # broker=app.config['CELERY_BROKER_URL']
        backend=app.config['result_backend'],
        broker=app.config['broker_url']
    )
    celery.conf.broker_connection_retry_on_startup = True #warn fix
    celery.conf.update(app.config)
    return celery
