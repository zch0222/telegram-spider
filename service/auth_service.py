from dao.user_dao import UserDAO
from fastapi import Depends, HTTPException, status
import bcrypt
from datetime import datetime, timedelta
import jwt
import os
from model.res_data import ResData

# JWT Configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-should-be-in-env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

class AuthService:
    def __init__(self, dao: UserDAO = Depends()):
        self.dao = dao

    def verify_password(self, plain_password, hashed_password):
        # bcrypt.checkpw requires bytes
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_password, hashed_password)

    def get_password_hash(self, password):
        # bcrypt.hashpw requires bytes
        if isinstance(password, str):
            password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        return hashed.decode('utf-8')

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def login(self, username, password):
        user = self.dao.get_user_by_username(username)
        if not user:
            return None
        
        if not self.verify_password(password, user["password"]):
            return None
            
        access_token = self.create_access_token(data={"sub": user["username"], "user_id": user["id"]})
        return access_token

    def register(self, username, password):
        existing_user = self.dao.get_user_by_username(username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        hashed_password = self.get_password_hash(password)
        self.dao.create_user(username, hashed_password)
        return True

    def change_password(self, user_id, old_password, new_password):
        user = self.dao.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if not self.verify_password(old_password, user["password"]):
            raise HTTPException(status_code=400, detail="Incorrect old password")
            
        hashed_password = self.get_password_hash(new_password)
        self.dao.update_password(user_id, hashed_password)
        return True

    def get_current_user_from_token(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            if username is None:
                return None
            return {"username": username, "id": user_id}
        except jwt.PyJWTError:
            return None
