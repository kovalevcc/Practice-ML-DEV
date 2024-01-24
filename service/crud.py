from sqlalchemy.orm import Session
import models, schemas
from hashlib import sha256

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.Email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    from auth import get_password_hash
    hashed_password = get_password_hash(user.Password)
    db_user = models.User(Name=user.Name, Email=user.Email, PasswordHash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_billing_account(db: Session, user_id: int):
    return db.query(models.BillingAccount).filter(models.BillingAccount.UserID == user_id).first()

def create_billing_account(db: Session, billing_account: schemas.BillingAccountCreate):
    db_billing_account = models.BillingAccount(**billing_account.dict())
    db.add(db_billing_account)
    db.commit()
    db.refresh(db_billing_account)
    return db_billing_account

def deduct_points(db: Session, user_id: int, points: int):
    billing_account = get_billing_account(db, user_id)
    if billing_account and billing_account.Points >= points:
        billing_account.Points -= points
        db.add(billing_account)
        db.commit()
        return True
    return False

def create_prediction(db: Session, user_id: int, model_used: str, input_data: str):
    input_data_hash = sha256(input_data.encode('utf-8')).hexdigest()
    db_prediction = models.Prediction(UserID=user_id, ModelUsed=model_used, InputDataHash=input_data_hash)
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def get_prediction_cost(model_name: str):
    model_costs = {'Model 1': 10, 'Model 2': 20, 'Model 3': 25}
    return model_costs.get(model_name, 0)