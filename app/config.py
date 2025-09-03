import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    DATABASE_URL = os.getenv("DATABASE_URL")
    DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
    DEFAULT_USER_EMAIL = os.getenv("DEFAULT_USER_EMAIL", "user@example.com")
    DEFAULT_USER_PASSWORD = os.getenv("DEFAULT_USER_PASSWORD", "user123")
    JWT_SECRET = os.getenv("JWT_SECRET", "my-super-secure-jwt-key-64-chars-long-1234567890abcdef")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 30))
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-webhook-secret")

config = Config()