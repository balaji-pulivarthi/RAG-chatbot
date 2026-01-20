import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import bcrypt  # <--- Using standard bcrypt directly

# --- CONFIGURATION ---
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_jwt_key_change_this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- SECURITY TOOLS ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- HELPER FUNCTIONS ---
def get_password_hash(password: str) -> str:
    """Hashes a password using bcrypt."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks if a password matches the hash."""
    pwd_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)

# --- MOCK USER DATABASE ---
# We now use the new get_password_hash function directly
USERS_DB = {
    "finance_user": {
        "password": get_password_hash("finance123"),
        "role": "Finance"
    },
    "hr_user": {
        "password": get_password_hash("hr123"),
        "role": "HR"
    },
    "eng_user": {
        "password": get_password_hash("eng123"),
        "role": "Engineering"
    },
    "marketing_user": {
        "password": get_password_hash("mark123"),
        "role": "Marketing"
    },
    "admin": {
        "password": get_password_hash("admin123"),
        "role": "C-Level"
    }
}

# --- DATA MODELS ---
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class UserData(BaseModel):
    username: str
    role: str

# --- JWT LOGIC ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        return UserData(username=username, role=role)
    except JWTError:
        raise credentials_exception