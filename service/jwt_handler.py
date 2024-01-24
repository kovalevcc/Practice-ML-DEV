import jwt
from datetime import datetime, timedelta
from config import Config

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Default to 15 minutes
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_access_token(token: str):
    try:
        decoded_data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return decoded_data if decoded_data["exp"] >= datetime.utcnow() else None
    except jwt.PyJWTError:
        return None