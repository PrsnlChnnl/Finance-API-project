from sanic import Blueprint
from sanic.response import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import engine
from app.models import User, Account, Payment
from app.auth import verify_webhook_signature
from sanic.exceptions import SanicException
from datetime import datetime

webhook_bp = Blueprint("webhook", url_prefix="/webhook")

@webhook_bp.route("/payment", methods=["POST"])
async def payment_webhook(request):
    data = request.json
    
    if not data or not all(key in data for key in ["transaction_id", "user_id", "account_id", "amount", "signature"]):
        raise SanicException("Invalid webhook data", status_code=400)
    
    # Проверяем подпись
    if not verify_webhook_signature(data):
        raise SanicException("Invalid signature", status_code=400)
    
    async with AsyncSession(engine) as session:
        try:
            # Проверяем существование пользователя
            result = await session.execute(select(User).where(User.id == data["user_id"]))
            user = result.scalar_one_or_none()
            if not user:
                raise SanicException("User not found", status_code=404)
            
            # Проверяем существование счета
            result = await session.execute(
                select(Account).where(Account.id == data["account_id"], Account.user_id == data["user_id"])
            )
            account = result.scalar_one_or_none()
            if not account:
                raise SanicException("Account not found", status_code=404)
            
            # Проверяем, существует ли уже транзакция
            result = await session.execute(
                select(Payment).where(Payment.transaction_id == data["transaction_id"])
            )
            existing_payment = result.scalar_one_or_none()
            if existing_payment:
                raise SanicException("Transaction already processed", status_code=400)
            
            # Обновляем баланс
            account.balance += data["amount"]
            
            # Создаем запись о платеже
            payment = Payment(
                transaction_id=data["transaction_id"],
                user_id=data["user_id"],
                account_id=data["account_id"],
                amount=data["amount"],
                status="completed",
                created_at=datetime.utcnow(),
                recipient_email=user.email  # Добавляем recipient_email
            )
            
            session.add(payment)
            session.add(account)
            await session.commit()
            
            return json({"status": "success", "message": "Payment processed"})
        
        except Exception as e:
            await session.rollback()
            raise SanicException(f"Failed to process payment: {str(e)}", status_code=500)