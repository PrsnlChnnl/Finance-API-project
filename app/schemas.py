from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    class Config:
        from_attributes = True

class AccountBase(BaseModel):
    balance: float = Field(ge=0.0)

class Account(AccountBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class AccountCreate(AccountBase):
    pass

class PaymentBase(BaseModel):
    amount: float = Field(gt=0.0)
    recipient_email: EmailStr
    transaction_id: Optional[str] = None

class PaymentCreate(PaymentBase):
    account_id: int

class Payment(PaymentBase):
    id: int
    user_id: int
    account_id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class WebhookData(BaseModel):
    transaction_id: str
    user_id: int
    account_id: int
    amount: float = Field(gt=0.0)
    signature: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None