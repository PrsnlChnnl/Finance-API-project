from sanic import Blueprint, response
from sanic.exceptions import SanicException
from sqlalchemy.future import select
from app.models import Account, Payment, User
from app.auth import protected
from app.schemas import PaymentCreate
from datetime import datetime
import uuid

payments_bp = Blueprint("payments", url_prefix="/payments")

@payments_bp.post("/")
@protected()
async def create_payment(request):
    try:
        data = PaymentCreate(**request.json).dict()
        print(f"🔍 Creating payment: {data}")
        session = request.ctx.session
        user = request.ctx.user  # Используем user из контекста
        async with session.begin():
            # Проверяем, существует ли счет отправителя
            result = await session.execute(select(Account).where(Account.id == data["account_id"]))
            account = result.scalar_one_or_none()
            if not account:
                print(f"❌ Account not found: account_id={data['account_id']}")
                raise SanicException("Account not found", status_code=404)
            
            # Проверяем, принадлежит ли счет текущему пользователю
            if account.user_id != user.id:
                print(f"❌ Unauthorized access to account: account_id={data['account_id']}, user_id={user.id}")
                raise SanicException("Unauthorized", status_code=403)
            
            # Проверяем баланс
            if account.balance < data["amount"]:
                print(f"❌ Insufficient funds: account_id={data['account_id']}, balance={account.balance}, amount={data['amount']}")
                raise SanicException("Insufficient funds", status_code=400)
            
            # Проверяем, существует ли получатель
            result = await session.execute(select(User).where(User.email == data["recipient_email"]))
            recipient = result.scalar_one_or_none()
            if not recipient:
                print(f"❌ Recipient not found: recipient_email={data['recipient_email']}")
                raise SanicException("Recipient not found", status_code=404)
            
            # Создаем платеж
            payment = Payment(
                account_id=data["account_id"],
                user_id=user.id,
                amount=data["amount"],
                recipient_email=data["recipient_email"],
                transaction_id=str(uuid.uuid4()),
                status="completed",
                created_at=datetime.utcnow()
            )
            session.add(payment)
            
            # Обновляем баланс счета
            account.balance -= data["amount"]
            session.add(account)
            
            await session.commit()
            print(f"✅ Payment created: id={payment.id}, amount={payment.amount}, transaction_id={payment.transaction_id}")
            return response.json(
                {
                    "id": payment.id,
                    "account_id": payment.account_id,
                    "user_id": payment.user_id,
                    "amount": payment.amount,
                    "recipient_email": payment.recipient_email,
                    "transaction_id": payment.transaction_id,
                    "status": payment.status,
                    "created_at": payment.created_at.isoformat()
                },
                status=201
            )
    except Exception as e:
        print(f"❌ Error in create_payment: {str(e)}")
        raise SanicException(f"Payment creation failed: {str(e)}", status_code=500)

@payments_bp.get("/")
@protected()
async def get_payments(request):
    try:
        session = request.ctx.session
        user = request.ctx.user  # Используем user из контекста
        async with session.begin():
            result = await session.execute(select(Payment).where(Payment.user_id == user.id))
            payments = result.scalars().all()
            print(f"🔍 Retrieved {len(payments)} payments for user_id={user.id}")
            return response.json(
                [
                    {
                        "id": payment.id,
                        "account_id": payment.account_id,
                        "user_id": payment.user_id,
                        "amount": payment.amount,
                        "recipient_email": payment.recipient_email,
                        "transaction_id": payment.transaction_id,
                        "status": payment.status,
                        "created_at": payment.created_at.isoformat()
                    }
                    for payment in payments
                ]
            )
    except Exception as e:
        print(f"❌ Error in get_payments: {str(e)}")
        raise SanicException(f"Failed to retrieve payments: {str(e)}", status_code=500)