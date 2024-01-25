import os
import streamlit as st
from database import SessionLocal, Base
from crud import get_billing_account, get_user_by_email, deduct_points, create_prediction, get_prediction_cost,create_user
from tasks import make_prediction_task
from auth import verify_password
from schemas import *
from sqlalchemy import create_engine
from database import Base
import requests

def save_uploaded_file(uploaded_file):
    try:
        with open(os.path.join('tempDir', uploaded_file.name), 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return os.path.join('tempDir', uploaded_file.name)
    except Exception as e:
        # Handle file save error
        st.error('Failed to save file.')
        return None



def get_user_points(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("http://localhost:8000/billing/points", headers=headers)
    if response.status_code == 200:
        return response.json()["Points"]
    else:
        st.error("Failed to retrieve points.")
        return None


# Initialize the Streamlit app
st.title('ML Prediction Service')

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button('Login'):
    response = requests.post("http://localhost:8000/auth/login", data={"username": email, "password": password})
    if response.status_code == 200:
        access_token = response.json()["access_token"]
        st.session_state['access_token'] = access_token  # Store the access token in session_state
        st.sidebar.success('Logged in successfully!')
        # Get user balance after successful login
        headers = {"Authorization": f"Bearer {access_token}"}
        balance_response = requests.get("http://localhost:8000/billing/points", headers=headers)
        if balance_response.status_code == 200:
            balance = balance_response.json()["Points"]
            st.sidebar.write(f"Balance: {balance} points")
    else:
        st.sidebar.error('Invalid email or password')

with st.sidebar:
    st.subheader("Register")
    new_name = st.text_input("Name", key="new_name")
    new_email = st.text_input("Email", key="new_email")
    new_password = st.text_input("Password", type="password", key="new_password")
    if st.button('Register'):
        user_data = UserCreate(Name=new_name, Email=new_email, Password=new_password)
        with SessionLocal() as db:
            user = create_user(db, user_data)
            if user:
                st.success('Registered successfully!')
            else:
                st.error('Registration failed.')

model_choice = st.selectbox('Choose a model', ['model 1', 'model 2','model 3'])
st.write("Upload a file for prediction")

file = st.file_uploader("Upload File")

if st.button('Make Prediction'):
    if 'access_token' in st.session_state:
        if file is not None:
            file_bytes = file.getvalue()

            headers = {
                "Authorization": f"Bearer {st.session_state['access_token']}"
            }

            data = {
                "model_name": model_choice
            }

            response = requests.post(
                "http://localhost:8000/prediction",
                headers=headers,
                files={"file": (file.name, file_bytes)},
                data=data
            )

            if response.status_code == 200:
                st.write('Prediction is being processed...')
                prediction_filename = response.json()["file_name"]
                st.session_state['prediction_filename'] = prediction_filename 
            else:
                st.error('Error making prediction. Response code: ' + str(response.status_code))
        else:
            st.error('Please upload a file to make a prediction.')
    else:
        st.error('Please login to make a prediction.')
        

if 'task_id' in st.session_state:
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    response = requests.get(f"http://localhost:8000/prediction/results?task_id={st.session_state['task_id']}", headers=headers)
    if response.status_code == 200:
        prediction_result = response.json()["PredictionResult"]
        st.write('Prediction result:', prediction_result)
    else:
        st.write('Prediction is still being processed, please wait.')
