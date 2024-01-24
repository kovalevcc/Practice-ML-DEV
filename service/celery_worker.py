from celery import Celery
import os

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

celery_app = Celery(
    'worker',
    backend='redis://localhost:6379/0',
    broker='redis://localhost:6379/0'
)

celery_app.conf.task_routes = {'tasks.make_prediction_task': {'queue': 'predictions'}}