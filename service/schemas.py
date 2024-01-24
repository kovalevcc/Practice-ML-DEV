from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    Name: str
    Email: str

class UserCreate(UserBase):
    Password: str

class User(UserBase):
    UserID: int
    CreatedAt: datetime

    class Config:
        orm_mode = True

class BillingAccountBase(BaseModel):
    UserID: int

class BillingAccountCreate(BillingAccountBase):
    Points: Optional[int] = 0

class BillingAccount(BillingAccountBase):
    BillingID: int
    UpdatedAt: datetime

    class Config:
        orm_mode = True

class PredictionBase(BaseModel):
    UserID: int
    ModelUsed: str
    InputDataHash: str

class PredictionCreate(PredictionBase):
    PredictionResult: str

class Prediction(PredictionBase):
    PredictionID: int
    CreatedAt: datetime

    class Config:
        orm_mode = True

class ModelInfoBase(BaseModel):
    ModelName: str

class ModelInfoCreate(ModelInfoBase):
    Description: str

class ModelInfo(ModelInfoBase):
    CreatedAt: datetime

    class Config:
        orm_mode = True

class BillingHistoryBase(BaseModel):
    BillingID: int
    PointsChanged: int
    Reason: str

class BillingHistoryCreate(BillingHistoryBase):
    pass

class BillingHistory(BillingHistoryBase):
    BillingHistoryID: int
    ChangedAt: datetime

    class Config:
        orm_mode = True