from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from app.config import config
from app.models import Base, User, Account, Payment
from app.auth import get_password_hash
from datetime import datetime

engine = create_async_engine(config.DATABASE_URL, echo=True)

async def init_db():
    try:
        # Создание таблиц
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)  # Удаляем таблицы для чистого старта
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created successfully")
        
        # Создание дефолтных пользователей, счетов и платежей
        async with AsyncSession(engine) as session:
            async with session.begin():
                try:
                    # Проверяем, существует ли администратор
                    result = await session.execute(select(User).where(User.email == config.DEFAULT_ADMIN_EMAIL))
                    admin = result.scalar_one_or_none()
                    if not admin:
                        admin = User(
                            email=config.DEFAULT_ADMIN_EMAIL,
                            full_name="Admin User",
                            hashed_password=get_password_hash(config.DEFAULT_ADMIN_PASSWORD),
                            is_active=True,
                            is_admin=True,
                            created_at=datetime.utcnow()
                        )
                        session.add(admin)
                        await session.commit()  # Коммитим администратора
                        print(f"✅ Created admin: email={admin.email}, id={admin.id}")
                    else:
                        print(f"ℹ️ Admin already exists: email={admin.email}, id={admin.id}")

                    # Проверяем, существует ли обычный пользователь
                    result = await session.execute(select(User).where(User.email == config.DEFAULT_USER_EMAIL))
                    user = result.scalar_one_or_none()
                    if not user:
                        user = User(
                            email=config.DEFAULT_USER_EMAIL,
                            full_name="Regular User",
                            hashed_password=get_password_hash(config.DEFAULT_USER_PASSWORD),
                            is_active=True,
                            is_admin=False,
                            created_at=datetime.utcnow()
                        )
                        session.add(user)
                        await session.commit()  # Коммитим пользователя
                        print(f"✅ Created user: email={user.email}, id={user.id}")
                    else:
                        print(f"ℹ️ User already exists: email={user.email}, id={user.id}")

                    # Проверяем, существуют ли счета
                    result = await session.execute(select(Account).where(Account.user_id == user.id))
                    user_account = result.scalar_one_or_none()
                    if not user_account:
                        user_account = Account(
                            user_id=user.id,
                            balance=500.0,
                            created_at=datetime.utcnow()
                        )
                        session.add(user_account)
                        await session.commit()  # Коммитим счет пользователя
                        print(f"✅ Created user account: account_id={user_account.id}, user_id={user.id}")
                    else:
                        print(f"ℹ️ User account already exists: account_id={user_account.id}, user_id={user.id}")

                    result = await session.execute(select(Account).where(Account.user_id == admin.id))
                    admin_account = result.scalar_one_or_none()
                    if not admin_account:
                        admin_account = Account(
                            user_id=admin.id,
                            balance=1000.0,
                            created_at=datetime.utcnow()
                        )
                        session.add(admin_account)
                        await session.commit()  # Коммитим счет администратора
                        print(f"✅ Created admin account: account_id={admin_account.id}, user_id={admin.id}")
                    else:
                        print(f"ℹ️ Admin account already exists: account_id={admin_account.id}, user_id={admin.id}")

                    # Проверяем, существует ли платеж
                    result = await session.execute(select(Payment).where(Payment.transaction_id == "test-transaction-1"))
                    payment = result.scalar_one_or_none()
                    if not payment:
                        payment = Payment(
                            account_id=user_account.id,
                            user_id=user.id,
                            amount=100.0,
                            recipient_email=config.DEFAULT_ADMIN_EMAIL,
                            transaction_id="test-transaction-1",
                            status="completed",
                            created_at=datetime.utcnow()
                        )
                        session.add(payment)
                        await session.commit()  # Коммитим платеж
                        print(f"✅ Created payment: transaction_id={payment.transaction_id}, account_id={payment.account_id}")
                    else:
                        print(f"ℹ️ Payment already exists: transaction_id={payment.transaction_id}, account_id={payment.account_id}")

                    print("✅ Default users, accounts, and payments initialized successfully")
                except Exception as e:
                    print(f"❌ Failed to create default users: {str(e)}")
                    await session.rollback()
                    raise
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        raise