from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sanic.exceptions import SanicException
from app.config import config
from app.models import User
from hashlib import sha256
from functools import wraps

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user(session: AsyncSession, email: str, password: str):
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(session: AsyncSession, token: str):
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise SanicException("Invalid token", status_code=401)
    except (JWTError, ValueError):
        raise SanicException("Invalid token", status_code=401)
    
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise SanicException("User not found", status_code=401)
    return user

async def get_current_active_user(current_user: User):
    if not current_user.is_active:
        raise SanicException("Inactive user", status_code=400)
    return current_user

async def get_current_admin_user(current_user: User):
    if not current_user.is_admin:
        raise SanicException("Not enough permissions", status_code=403)
    return current_user

def verify_webhook_signature(data: dict) -> bool:
    """Verify webhook signature"""
    if not data.get("signature"):
        return False
    
    received_signature = data["signature"]
    secret_key = config.WEBHOOK_SECRET
    
    sorted_keys = sorted(key for key in data.keys() if key != "signature")
    concatenated = ''.join(str(data[key]) for key in sorted_keys)
    concatenated += secret_key
    expected_signature = sha256(concatenated.encode()).hexdigest()
    
    return received_signature == expected_signature

def protected():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            session = request.ctx.session
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                raise SanicException("Missing or invalid token", status_code=401)
            token = auth_header.replace("Bearer ", "")
            user = await get_current_user(session, token)
            request.ctx.user = user  # Сохраняем пользователя в контексте запроса
            return await f(request, *args, **kwargs)
        return decorated_function
    return decorator