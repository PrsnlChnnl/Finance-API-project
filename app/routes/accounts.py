from sanic import Blueprint, response
from sanic.exceptions import SanicException
from sqlalchemy.future import select
from app.models import Account
from app.auth import protected
from app.schemas import AccountCreate
from datetime import datetime

accounts_bp = Blueprint("accounts", url_prefix="/accounts")

@accounts_bp.post("/")
@protected()
async def create_account(request):
    try:
        data = AccountCreate(**request.json).dict()
        print(f"🔍 Creating account: {data}")
        session = request.ctx.session
        user = request.ctx.user  # Используем user из контекста
        async with session.begin():
            account = Account(
                user_id=user.id,
                balance=data["balance"],
                created_at=datetime.utcnow()
            )
            session.add(account)
            await session.commit()
            print(f"✅ Account created: id={account.id}, user_id={user.id}")
            return response.json(
                {
                    "id": account.id,
                    "user_id": account.user_id,
                    "balance": account.balance,
                    "created_at": account.created_at.isoformat()
                },
                status=201
            )
    except Exception as e:
        print(f"❌ Error in create_account: {str(e)}")
        raise SanicException(f"Account creation failed: {str(e)}", status_code=500)