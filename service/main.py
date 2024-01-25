from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal, engine
from models import Base
from crud import create_user, get_user_by_email, deduct_points, create_prediction, get_billing_account 
from schemas import UserCreate, User, BillingAccount, PredictionCreate, Prediction, BillingHistory
from auth import authenticate_user, get_password_hash
from jwt_handler import decode_access_token
from inference import process_data
import shutil
import models
import os

from fastapi.responses import FileResponse
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if token_data is None:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data["sub"])
    if user is None:
        raise credentials_exception
    return user

@app.post("/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.Email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user, "token_type": "bearer"}

@app.get("/billing/points")
async def view_points(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    billing_account = db.query(models.BillingAccount).filter(models.BillingAccount.UserID == current_user.UserID).first()
    if not billing_account:
        raise HTTPException(status_code=404, detail="Billing account not found")
    return billing_account

@app.post("/billing/points")
async def deduct_service_points(points: int = Form(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if deduct_points(db, current_user.UserID, points):
        return {"msg": "Points deducted successfully"}
    else:
        raise HTTPException(status_code=400, detail="Insufficient points")


@app.post("/prediction")
async def make_prediction(file: UploadFile = File(...), model_name: str = Form(...)):
    print(f"Received model name: {model_name}")
    os.makedirs('temp', exist_ok=True)

    file_location = f"temp/{file.filename}"
    with open(file_location, "wb") as file_object:
        shutil.copyfileobj(file.file, file_object)

    try:
        # Call your process_data function
        output_file_name = process_data(file_location, model_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {e}")

    return {"message": "Prediction completed", "file_name": output_file_name}

@app.get("/prediction/results/{filename}", response_class=FileResponse)
async def download_prediction_results(filename: str):
    file_path = f"temp/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='text/csv', filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")
    pass

Base.metadata.create_all(bind=engine)