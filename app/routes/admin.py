from sanic import Blueprint, response
from sanic.exceptions import SanicException
from sqlalchemy.future import select
from app.models import User
from app.auth import protected, get_current_admin_user
from app.schemas import UserCreate
from app.auth import get_password_hash
from datetime import datetime

admin_bp = Blueprint("admin", url_prefix="/admin")

@admin_bp.get("/users")
@protected()
async def get_all_users(request):
    try:
        session = request.ctx.session
        await get_current_admin_user(request.ctx.user)  # Проверяем, что пользователь — админ
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"🔍 Retrieved {len(users)} users")
        return response.json(
            [
                {
                    "id": u.id,
                    "email": u.email,
                    "full_name": u.full_name,
                    "is_active": u.is_active,
                    "is_admin": u.is_admin,
                    "created_at": u.created_at.isoformat()
                }
                for u in users
            ]
        )
    except Exception as e:
        print(f"❌ Error in get_all_users: {str(e)}")
        raise SanicException(f"Failed to retrieve users: {str(e)}", status_code=500)

@admin_bp.get("/me")
@protected()
async def get_admin_info(request):
    try:
        user = await get_current_admin_user(request.ctx.user)  # Проверяем, что пользователь — админ
        print(f"🔍 Retrieved admin: id={user.id}, email={user.email}")
        return response.json(
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat()
            }
        )
    except Exception as e:
        print(f"❌ Error in get_admin_info: {str(e)}")
        raise SanicException(f"Failed to retrieve admin info: {str(e)}", status_code=500)

@admin_bp.post("/users")
@protected()
async def create_user(request):
    try:
        session = request.ctx.session
        await get_current_admin_user(request.ctx.user)  # Проверяем, что пользователь — админ
        data = UserCreate(**request.json).dict()
        print(f"🔍 Creating user: {data}")
        
        # Проверяем, существует ли пользователь с таким email
        result = await session.execute(select(User).where(User.email == data["email"]))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            print(f"❌ User already exists: email={data['email']}")
            raise SanicException("User with this email already exists", status_code=400)
        
        # Создаем нового пользователя
        user = User(
            email=data["email"],
            full_name=data["full_name"],
            hashed_password=get_password_hash(data["password"]),
            is_active=True,
            is_admin=False,
            created_at=datetime.utcnow()
        )
        session.add(user)
        await session.commit()  # Коммитим изменения
        print(f"✅ User created: id={user.id}, email={user.email}")
        
        return response.json(
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat()
            },
            status=201
        )
    except Exception as e:
        print(f"❌ Error in create_user: {str(e)}")
        await session.rollback()  # Откатываем изменения в случае ошибки
        raise SanicException(f"Failed to create user: {str(e)}", status_code=500)