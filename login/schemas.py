from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginCredentials(BaseModel):
    username: str
    password: str

class TokenLogin(BaseModel):
    token: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    email: str
    role: str

class UserInfo(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
