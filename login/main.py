from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from .models import users_auth_db, active_tokens
from .schemas import LoginCredentials, TokenLogin, LoginResponse, UserInfo
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

# Add parent directory to path to import jwt_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jwt_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI(
    title="Login & Authentication API",
    description="Authentication service with JWT-based authentication",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React UI
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Helper function to verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Helper function to create JWT token
def create_jwt_token(user_id: int, username: str, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Helper function to decode and validate JWT token
def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 1. Login with credentials (username + password)
@app.post("/login/credentials", response_model=LoginResponse)
def login_with_credentials(credentials: LoginCredentials):
    """
    Login using username and password.
    Returns a JWT access token for subsequent requests.
    """
    # Find user by username
    user = None
    for u in users_auth_db:
        if u["username"] == credentials.username:
            user = u
            break

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate JWT access token
    access_token = create_jwt_token(user["id"], user["username"], user["role"])

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user["id"],
        username=user["username"],
        email=user["email"],
        role=user["role"]
    )

# 2. Login with token (validate existing JWT token)
@app.post("/login/token", response_model=LoginResponse)
def login_with_token(token_data: TokenLogin):
    """
    Validate an existing JWT token and return user information.
    """
    # Decode and validate JWT token
    payload = decode_jwt_token(token_data.token)

    user_id = payload.get("user_id")

    # Find user by ID
    user = None
    for u in users_auth_db:
        if u["id"] == user_id:
            user = u
            break

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return LoginResponse(
        access_token=token_data.token,
        token_type="bearer",
        user_id=user["id"],
        username=user["username"],
        email=user["email"],
        role=user["role"]
    )

# 3. Get current user info (protected endpoint)
@app.get("/me", response_model=UserInfo)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get information about the currently authenticated user.
    Requires JWT Bearer token in Authorization header.
    """
    token = credentials.credentials

    # Decode and validate JWT token
    payload = decode_jwt_token(token)
    user_id = payload.get("user_id")

    # Find user by ID
    user = None
    for u in users_auth_db:
        if u["id"] == user_id:
            user = u
            break

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserInfo(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        role=user["role"]
    )

# 4. Logout (with JWT, just inform client to discard token)
@app.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout endpoint. With JWT, the client should discard the token.
    Server validates the token is valid before confirming logout.
    """
    token = credentials.credentials

    # Validate token before logout
    decode_jwt_token(token)

    # With JWT, we don't need to store tokens server-side
    # Client should discard the token
    return {"message": "Successfully logged out. Please discard your token."}

# 5. Validate JWT token endpoint
@app.get("/validate")
def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate if a JWT token is valid and not expired.
    Returns user information from the token.
    """
    token = credentials.credentials

    try:
        payload = decode_jwt_token(token)
        return {
            "valid": True,
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "role": payload.get("role")
        }
    except HTTPException:
        return {"valid": False}
