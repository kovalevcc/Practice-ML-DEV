from celery_worker import celery_app
from ml_models import predict
from database import SessionLocal
from crud import create_prediction

@celery_app.task
def make_prediction_task(user_id: int, model_name: str, input_data: str):
    prediction_result = predict(model_name, input_data)
    with SessionLocal() as db:
        create_prediction(db, user_id, model_name, input_data, prediction_result)
    return prediction_result