import asyncio
import aiohttp
import json
import sys
import time
from hashlib import sha256

class FinanceAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        
    async def test_health_check(self):
        """Тест здоровья приложения"""
        print("🔍 Testing health check...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/") as response:
                    data = await response.json()
                    print(f"✅ Health check: {data}")
                    return response.status == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    async def admin_login(self):
        """Авторизация администратора"""
        print("\n🔐 Admin login...")
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "email": "admin@example.com",
                    "password": "AdminSecurePassword123!"
                }
                async with session.post(
                    f"{self.base_url}/auth/login",
                    json=payload
                ) as response:
                    data = await response.json()
                    if response.status == 200:
                        self.admin_token = data["access_token"]
                        print(f"✅ Admin login successful: {data['access_token'][:20]}...")
                        return True
                    else:
                        print(f"❌ Admin login failed: {data}")
                        return False
        except Exception as e:
            print(f"❌ Admin login error: {e}")
            return False
    
    async def user_login(self):
        """Авторизация пользователя"""
        print("\n🔐 User login...")
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "email": "user@example.com",
                    "password": "UserStrongPass456!"
                }
                async with session.post(
                    f"{self.base_url}/auth/login",
                    json=payload
                ) as response:
                    data = await response.json()
                    if response.status == 200:
                        self.user_token = data["access_token"]
                        print(f"✅ User login successful: {data['access_token'][:20]}...")
                        return True
                    else:
                        print(f"❌ User login failed: {data}")
                        return False
        except Exception as e:
            print(f"❌ User login error: {e}")
            return False
    
    async def get_admin_info(self):
        """Получение информации об администраторе"""
        print("\n👑 Getting admin info...")
        if not self.admin_token:
            print("❌ Admin token not available")
            return False
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.admin_token}",
                    "Content-Type": "application/json"
                }
                async with session.get(
                    f"{self.base_url}/admin/me",
                    headers=headers
                ) as response:
                    data = await response.json()
                    print(f"✅ Admin info: {json.dumps(data, indent=2)}")
                    return response.status == 200
        except Exception as e:
            print(f"❌ Admin info error: {e}")
            return False
    
    async def get_user_info(self):
        """Получение информации о пользователе"""
        print("\n👤 Getting user info...")
        if not self.user_token:
            print("❌ User token not available")
            return False
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.user_token}",
                    "Content-Type": "application/json"
                }
                async with session.get(
                    f"{self.base_url}/users/me",
                    headers=headers
                ) as response:
                    data = await response.json()
                    print(f"✅ User info: {json.dumps(data, indent=2)}")
                    return response.status == 200
        except Exception as e:
            print(f"❌ User info error: {e}")
            return False
    
    async def get_user_accounts(self):
        """Получение счетов пользователя"""
        print("\n💳 Getting user accounts...")
        if not self.user_token:
            print("❌ User token not available")
            return False
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.user_token}",
                    "Content-Type": "application/json"
                }
                async with session.get(
                    f"{self.base_url}/users/me/accounts",
                    headers=headers
                ) as response:
                    data = await response.json()
                    print(f"✅ User accounts: {json.dumps(data, indent=2)}")
                    return response.status == 200
        except Exception as e:
            print(f"❌ User accounts error: {e}")
            return False
    
    async def get_all_users(self):
        """Получение всех пользователей (админ)"""
        print("\n📊 Getting all users...")
        if not self.admin_token:
            print("❌ Admin token not available")
            return False
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.admin_token}",
                    "Content-Type": "application/json"
                }
                async with session.get(
                    f"{self.base_url}/admin/users",
                    headers=headers
                ) as response:
                    data = await response.json()
                    if response.status == 200:
                        print(f"✅ All users: {len(data)} users found")
                        for user in data[:2]:
                            print(f"   - {user.get('email', 'N/A')} (ID: {user.get('id', 'N/A')})")
                        return True
                    else:
                        print(f"❌ All users failed: {data}")
                        return False
        except Exception as e:
            print(f"❌ All users error: {e}")
            return False
    
    async def create_user(self):
        """Создание нового пользователя администратором"""
        print("\n👤 Creating new user...")
        if not self.admin_token:
            print("❌ Admin token not available")
            return False
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.admin_token}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "email": f"testuser{int(time.time())}@example.com",
                    "full_name": "Test User",
                    "password": "TestPass123!"
                }
                async with session.post(
                    f"{self.base_url}/admin/users",
                    json=payload,
                    headers=headers
                ) as response:
                    data = await response.json()
                    if response.status == 201:
                        print(f"✅ User created: {json.dumps(data, indent=2)}")
                        return True
                    else:
                        print(f"❌ User creation failed: {data}")
                        return False
        except Exception as e:
            print(f"❌ User creation error: {e}")
            return False
    
    async def get_user_id(self):
        """Получение ID пользователя"""
        print("\n🔍 Getting user ID...")
        if not self.user_token:
            print("❌ User token not available")
            return None
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.user_token}",
                    "Content-Type": "application/json"
                }
                async with session.get(
                    f"{self.base_url}/users/me",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ User ID: {data['id']}")
                        return data["id"]
                    else:
                        print(f"❌ Failed to get user ID: {await response.text()}")
                        return None
        except Exception as e:
            print(f"❌ Error getting user ID: {e}")
            return None
    
    async def get_user_account_id(self):
        """Получение ID счета пользователя"""
        print("\n🔍 Getting user account ID...")
        if not self.user_token:
            print("❌ User token not available")
            return None
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.user_token}",
                    "Content-Type": "application/json"
                }
                async with session.get(
                    f"{self.base_url}/users/me/accounts",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            print(f"✅ User account ID: {data[0]['id']}")
                            return data[0]["id"]
                        else:
                            print("❌ No accounts found for user")
                            return None
                    else:
                        print(f"❌ Failed to get user account ID: {await response.text()}")
                        return None
        except Exception as e:
            print(f"❌ Error getting account ID: {e}")
            return None
    
    async def test_webhook_payment(self):
        """Тест вебхука платежа"""
        print("\n💸 Testing payment webhook...")
        try:
            # Получаем user_id
            user_id = await self.get_user_id()
            if not user_id:
                print("❌ Cannot get user ID")
                return False

            # Получаем account_id
            account_id = await self.get_user_account_id()
            if not account_id:
                print("❌ Cannot get user account ID")
                return False

            # Генерируем подпись
            secret_key = "7d8f9e0a1b2c3d4e5f6a7b8c9d0e1f2a"  # Из .env
            transaction_data = {
                "transaction_id": f"test-tx-{int(time.time())}",
                "user_id": user_id,
                "account_id": account_id,
                "amount": 100.0
            }
            
            # Создаем подпись
            sorted_keys = sorted(transaction_data.keys())
            concatenated = ''.join(str(transaction_data[key]) for key in sorted_keys)
            concatenated += secret_key
            signature = sha256(concatenated.encode()).hexdigest()
            
            payload = {
                **transaction_data,
                "signature": signature
            }
            
            print(f"📤 Webhook payload: {json.dumps(payload, indent=2)}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/webhook/payment",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Payment successful: {json.dumps(data, indent=2)}")
                        return True
                    else:
                        error_data = await response.text()
                        print(f"❌ Payment failed: Status {response.status}, Error: {error_data}")
                        return False
                    
        except Exception as e:
            print(f"❌ Payment webhook error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def run_tests(self):
        """Запуск всех тестов"""
        print("🚀 Starting Finance API Tests")
        print("=" * 50)
        
        # Список всех тестов
        tests = [
            ("Health Check", self.test_health_check),
            ("Admin Login", self.admin_login),
            ("User Login", self.user_login),
            ("Admin Info", self.get_admin_info),
            ("User Info", self.get_user_info),
            ("User Accounts", self.get_user_accounts),
            ("All Users", self.get_all_users),
            ("Create User", self.create_user),
            ("Webhook Payment", self.test_webhook_payment),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                success = await test_func()
                results.append((test_name, success))
                print(f"   {'✅' if success else '❌'} {test_name}")
            except Exception as e:
                print(f"❌ {test_name} failed with error: {e}")
                results.append((test_name, False))
            
            await asyncio.sleep(0.1)
        
        # Вывод результатов
        print("\n" + "=" * 50)
        print("📊 Test Results:")
        print("=" * 50)
        
        passed = 0
        for test_name, success in results:
            status = "PASS" if success else "FAIL"
            print(f"{'✅' if success else '❌'} {test_name}: {status}")
            if success:
                passed += 1
        
        print("=" * 50)
        print(f"🎯 Total: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("\n🎉 All tests passed! API is working correctly.")
        else:
            print("\n⚠️ Some tests failed. Check the output above.")
        
        return all(success for _, success in results)

async def main():
    """Основная функция"""
    tester = FinanceAPITester()
    
    try:
        success = await tester.run_tests()
        if not success:
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())