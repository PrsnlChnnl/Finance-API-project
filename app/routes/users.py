from sanic import Blueprint, response
from sanic.exceptions import SanicException
from sqlalchemy.future import select
from app.models import Account
from app.auth import protected

users_bp = Blueprint("users", url_prefix="/users")

@users_bp.get("/me")
@protected()
async def get_current_user_info(request):
    try:
        user = request.ctx.user  # Используем user из контекста
        print(f"🔍 Retrieved user: id={user.id}, email={user.email}")
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
        print(f"❌ Error in get_current_user_info: {str(e)}")
        raise SanicException(f"Failed to retrieve user info: {str(e)}", status_code=500)

@users_bp.get("/me/accounts")
@protected()
async def get_user_accounts(request):
    try:
        session = request.ctx.session
        user = request.ctx.user  # Используем user из контекста
        result = await session.execute(select(Account).where(Account.user_id == user.id))
        accounts = result.scalars().all()
        print(f"🔍 Retrieved {len(accounts)} accounts for user_id={user.id}")
        return response.json(
            [
                {
                    "id": account.id,
                    "user_id": account.user_id,
                    "balance": account.balance,
                    "created_at": account.created_at.isoformat()
                }
                for account in accounts
            ]
        )
    except Exception as e:
        print(f"❌ Error in get_user_accounts: {str(e)}")
        raise SanicException(f"Failed to retrieve accounts: {str(e)}", status_code=500)