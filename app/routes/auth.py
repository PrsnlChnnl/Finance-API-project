from sanic import Blueprint
from sanic.response import json
from sanic.exceptions import SanicException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import authenticate_user, create_access_token

auth_bp = Blueprint("auth", url_prefix="/auth")

@auth_bp.route("/login", methods=["POST"])
async def login(request):
    session: AsyncSession = request.ctx.session  # Исправлено: db -> session
    data = request.json
    if not data or "email" not in data or "password" not in data:
        raise SanicException("Email and password required", status_code=400)
    
    user = await authenticate_user(session, data["email"], data["password"])
    if not user:
        raise SanicException("Invalid credentials", status_code=401)
    
    if not user.is_active:
        raise SanicException("User inactive", status_code=400)
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return json({
        "access_token": access_token,
        "token_type": "bearer"
    })