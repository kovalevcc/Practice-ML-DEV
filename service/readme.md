pip install -r requirements.txt

Запуск:
uvicorn main:app --reload --port 8000 &
streamlit run app.py &
celery -A celery_worker.celery_app worker --loglevel=info &
