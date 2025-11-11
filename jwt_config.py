# Shared JWT configuration for all services
# Loads SECRET_KEY from environment variable

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get SECRET_KEY from environment variable
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-secret-key-please-change-in-env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Warn if using default key
if SECRET_KEY == "default-secret-key-please-change-in-env":
    print("⚠️  WARNING: Using default JWT_SECRET_KEY. Set JWT_SECRET_KEY in .env file for production!")
