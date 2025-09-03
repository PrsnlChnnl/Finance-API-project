import asyncio
import os
import signal
from sanic import Sanic, response
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.config import config
from app.models import Base, User, Account, Payment
from app.auth import get_password_hash
from app.routes.auth import auth_bp
from app.routes.accounts import accounts_bp
from app.routes.payments import payments_bp
from app.routes.users import users_bp
from app.routes.admin import admin_bp
from app.routes.webhook import webhook_bp
from datetime import datetime, UTC
import uuid

app = Sanic("FinanceAPI")

app.blueprint(auth_bp)
app.blueprint(accounts_bp)
app.blueprint(payments_bp)
app.blueprint(users_bp)
app.blueprint(admin_bp)
app.blueprint(webhook_bp)

engine = create_async_engine(config.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

@app.get("/")
async def health_check(request):
    return response.json({"status": "OK", "message": "Finance API is running"})

@app.before_server_start
async def setup_db(app, loop):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully")
    
    async with AsyncSessionLocal() as session:
        # Создание пользователей
        async with session.begin():
            admin_result = await session.execute(
                select(User).where(User.email == config.DEFAULT_ADMIN_EMAIL)
            )
            admin = admin_result.scalar_one_or_none()
            
            if not admin:
                admin_password = config.DEFAULT_ADMIN_PASSWORD
                admin_hashed = get_password_hash(admin_password)
                admin = User(
                    email=config.DEFAULT_ADMIN_EMAIL,
                    full_name="Admin User",
                    hashed_password=admin_hashed,
                    is_active=True,
                    is_admin=True,
                    created_at=datetime.now(UTC)
                )
                session.add(admin)
                print(f"🔍 Admin user created: email={config.DEFAULT_ADMIN_EMAIL}, hashed_password={admin_hashed}")
            
            user_result = await session.execute(
                select(User).where(User.email == config.DEFAULT_USER_EMAIL)
            )
            user = user_result.scalar_one_or_none()
            
            if not user:
                user_password = config.DEFAULT_USER_PASSWORD
                user_hashed = get_password_hash(user_password)
                user = User(
                    email=config.DEFAULT_USER_EMAIL,
                    full_name="Regular User",
                    hashed_password=user_hashed,
                    is_active=True,
                    is_admin=False,
                    created_at=datetime.now(UTC)
                )
                session.add(user)
                print(f"🔍 Regular user created: email={config.DEFAULT_USER_EMAIL}, hashed_password={user_hashed}")
            await session.commit()
            
            admin_id = admin.id
            user_id = user.id
            print(f"✅ Created users: admin_id={admin_id}, user_id={user_id}")
        
        # Создание счетов
        async with session.begin():
            user_account = Account(
                user_id=user_id,
                balance=500.0,
                created_at=datetime.now(UTC)
            )
            admin_account = Account(
                user_id=admin_id,
                balance=1000.0,
                created_at=datetime.now(UTC)
            )
            session.add_all([user_account, admin_account])
            await session.commit()
            
            account_id = user_account.id
            admin_account_id = admin_account.id
            print(f"✅ Created accounts: account_id={account_id}, admin_account_id={admin_account_id}")
        
        # Создание платежа
        async with session.begin():
            payment = Payment(
                account_id=account_id,
                user_id=user_id,
                amount=100.0,
                recipient_email=config.DEFAULT_ADMIN_EMAIL,
                transaction_id=f"test-transaction-{uuid.uuid4()}",
                status="completed",
                created_at=datetime.now(UTC)
            )
            session.add(payment)
            await session.commit()
            
            print("✅ Default users, accounts, and payments created successfully")

@app.middleware("request")
async def add_session(request):
    request.ctx.session = AsyncSessionLocal()

@app.middleware("response")
async def close_session(request, response):
    if hasattr(request.ctx, "session"):
        if request.ctx.session.in_transaction():
            await request.ctx.session.commit()
        await request.ctx.session.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True, single_process=True)