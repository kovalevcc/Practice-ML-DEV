from celery_worker import celery_app
from ml_models import predict
from database import SessionLocal
from crud import create_prediction

@celery_app.task(bind=True)
def make_prediction_task(self, user_id: int, model_name: str, file_path: str):
    with open(file_path, 'r') as file:
        input_data = file.read()
    prediction_result = predict(model_name, input_data)
    with SessionLocal() as db:
        create_prediction(db, user_id, model_name, input_data, prediction_result)
    return {"task_id": self.request.id, "prediction_result": prediction_result}