from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal
import datetime


class UserBase(BaseModel):
    telegram_user_id: int
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    credit_balance: Optional[Decimal] = None


class UserInDBBase(UserBase):
    id: int
    credit_balance: Decimal
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True  # Pydantic V2 (formerly orm_mode)


class User(UserInDBBase):
    pass
