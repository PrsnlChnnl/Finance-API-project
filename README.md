# Finance-API-project
A RESTful API built with Sanic and SQLAlchemy for managing users, accounts, payments, and webhooks. Supports user authentication, admin operations, and payment processing with SQLite as the database.

# Finance-API-project
A RESTful API built with Sanic and SQLAlchemy for managing users, accounts, payments, and webhooks. Supports user authentication, admin operations, and payment processing with SQLite as the database.

## Features
- User authentication (JWT-based login for admin and regular users).
- User management (create, retrieve user info, list all users for admins).
- Account management (retrieve user accounts).
- Payment processing via webhook with signature verification.
- Health check endpoint.

## Requirements
- Python 3.12
  
  Dependencies (listed in `requirements.txt`):
  
- sanic==23.6.0
- sqlalchemy[asyncio]==2.0.23
- aiosqlite==0.20.0
- python-jose[cryptography]==3.3.0
- passlib[bcrypt]==1.7.4
- python-dotenv==1.0.1
- aiohttp==3.9.5
- pydantic==2.6.0
  
## Setup
1. **Clone the repository**:
```
 git clone https://github.com/your-username/finance-api.git
 cd finance-api
```

2. **Create and activate a virtual environment:**
```
python3.12 -m venv venv
```
# Windows
```
.\venv\Scripts\activate
```
# Linux/Mac
```
source venv/bin/activate
```
3. **Install dependencies:**
 ```  
pip install -r requirements.txt
```
4. **Configure environment variables:**

Copy .env.example to .env and update values as needed:
```
cp .env.example .env
```
**Running the Application**

1. **Start the server:**
```
python main.py
```
The server runs on http://localhost:8000. It initializes the SQLite database (finance.db) with default admin and user accounts.

2. **Run tests:**

```
python test_api.py
```
Tests cover health check, authentication, user management, account retrieval, and webhook payment processing. All 9 tests should pass.

Using the Application (Without Postman)You can interact with the API using curl commands. Below are examples of key endpoints:

1. **Health Check**
```   
curl http://localhost:8000/
```
Response: {"status": "OK", "message": "Finance API is running"}

2. **Login (Admin)**
```   
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"admin@example.com","password":"AdminSecurePassword123!"}'
```
4. **Login (User)**
```
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"UserStrongPass456!"}'
```
Response: {"access_token": "<token>", "token_type": "bearer"}

4. **Get Current User Info**
```   
curl -X GET http://localhost:8000/users/me -H "Authorization: Bearer <user_token>"
```
Response: {"id": 2, "email": "user@example.com", "full_name": "Regular User", ...}

5. **Get User Accounts**
```   
curl -X GET http://localhost:8000/users/me/accounts -H "Authorization: Bearer <user_token>"
```
Response: [{"id": 1, "user_id": 2, "balance": 500.0, ...}]

6. **Get All Users (Admin Only)**
```  
curl -X GET http://localhost:8000/admin/users -H "Authorization: Bearer <admin_token>"
```
Response: [{"id": 1, "email": "admin@example.com", ...}, {"id": 2, "email": "user@example.com", ...}]

7. **Create New User (Admin Only)**
```   
curl -X POST http://localhost:8000/admin/users -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d '{"email":"newuser@example.com","full_name":"New User","password":"NewPass123!"}'
```
Response: {"id": 3, "email": "newuser@example.com", "full_name": "New User", ...}

8. **Webhook Payment**
```   
curl -X POST http://localhost:8000/webhook/payment -H "Content-Type: application/json" -d '{"transaction_id":"test-tx-123","user_id":2,"account_id":1,"amount":100.0,"signature":"<signature>"}'
```

**Note:**

The signature must be generated using the WEBHOOK_SECRET (see app/auth.py for signature generation logic).

The database is automatically initialized with default admin (admin@example.com) and user (user@example.com) accounts on server start.

Ensure the .env file is correctly configured before running the application.

Tests require the server to be running (python main.py) in a separate terminal.

For production, consider using a more robust database (e.g., PostgreSQL) and securing the JWT_SECRET and WEBHOOK_SECRET.
