import os
import streamlit as st
from database import SessionLocal, Base
from crud import get_user_by_email, deduct_points, create_prediction, get_prediction_cost,create_user
from tasks import make_prediction_task
from auth import verify_password
from schemas import *
from sqlalchemy import create_engine
from sqlalchemy import create_engine
from database import Base

def save_uploaded_file(uploaded_file):
    try:
        with open(os.path.join('tempDir', uploaded_file.name), 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return os.path.join('tempDir', uploaded_file.name)
    except Exception as e:
        # Handle file save error
        st.error('Failed to save file.')
        return None


# def initialize_database():
#     DATABASE_URL = "sqlite:///db/database.db"  # Replace with your database URL

#     # Extract directory path from database URL
#     db_directory = os.path.dirname(DATABASE_URL.split("///")[1])

#     # Create the directory if it does not exist
#     if not os.path.exists(db_directory):
#         os.makedirs(db_directory)

#     # Create the database tables
#     engine = create_engine(DATABASE_URL)
#     Base.metadata.create_all(engine)
#     print("Database initialized successfully.")

# # Call the initialization at the start of your Streamlit app
# initialize_database()


# Initialize the Streamlit app
st.title('ML Prediction Service')

# User authentication with JWT
from auth import authenticate_user

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button('Login'):
    with SessionLocal() as db:
        access_token = authenticate_user(db, email, password)
        if access_token:
            st.session_state['access_token'] = access_token
            st.sidebar.success('Logged in successfully!')
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
if file is not None:
    file_path = save_uploaded_file(file)


# Make prediction
if st.button('Make Prediction'):
    if 'user_id' in st.session_state:
        if file is not None:
            file_path = save_uploaded_file(file)
            if file_path:
                with SessionLocal() as db:
                    cost = get_prediction_cost(model_choice)
                    if deduct_points(db, st.session_state['user_id'], cost):
                        task = make_prediction_task.delay(st.session_state['user_id'], model_choice, file_path)
                        st.session_state['task_id'] = task.id
                        st.write('Prediction is being processed...')
                        st.write(f'Task ID: {task.id}')
                    else:
                        st.error('Insufficient points for this prediction.')
        else:
            st.error('Please upload a file to make a prediction.')
    else:
        st.error('Please login to make a prediction.')

# Display prediction results
if 'task_id' in st.session_state:
    with SessionLocal() as db:
        prediction = create_prediction(db, st.session_state['user_id'], model_choice, input_data)
        if prediction:
            st.write('Prediction result:', prediction.PredictionResult)
        else:
            st.write('Prediction is still being processed, please wait.')
