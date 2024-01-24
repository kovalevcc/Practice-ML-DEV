from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'Users'

    UserID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Name = Column(String)
    Email = Column(String, unique=True, index=True)
    PasswordHash = Column(String)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    billing_accounts = relationship('BillingAccount', back_populates='user')
    predictions = relationship('Prediction', back_populates='user')

class BillingAccount(Base):
    __tablename__ = 'BillingAccounts'

    BillingID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('Users.UserID'))
    Points = Column(Integer, default=0)
    UpdatedAt = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='billing_accounts')
    billing_history = relationship('BillingHistory', back_populates='billing_account')

class Prediction(Base):
    __tablename__ = 'Predictions'

    PredictionID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey('Users.UserID'))
    ModelUsed = Column(String)
    InputDataHash = Column(String)
    PredictionResult = Column(Text)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='predictions')

class ModelInfo(Base):
    __tablename__ = 'ModelInfo'

    ModelName = Column(String, primary_key=True, index=True)
    Description = Column(Text)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

class BillingHistory(Base):
    __tablename__ = 'BillingHistory'

    BillingHistoryID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    BillingID = Column(Integer, ForeignKey('BillingAccounts.BillingID'))
    PointsChanged = Column(Integer)
    Reason = Column(String)
    ChangedAt = Column(DateTime, default=datetime.utcnow)

    billing_account = relationship('BillingAccount', back_populates='billing_history')