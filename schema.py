from datetime import datetime
from enum import Enum
from fastapi import FastAPI, File, Form
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Extra, Field
from uuid import UUID, uuid1


class Users(BaseModel):
    email: EmailStr
    password: str
    # created_at: datetime
    
class PaymentBase(BaseModel):
    minutes: int
    plan: str

class RefreshToken(BaseModel):
    refresh_token:str

class Newsletter(BaseModel):
    email: EmailStr
    
class Address(BaseModel):
    country: str
    states: str
    city: str
    address: str
    
class MoreInfo(BaseModel):
    full_name: Optional[str] = None
    phone_num: Optional[str] = None
    
class RefreshToken(BaseModel):
    refresh_token:str
    
class UpdatePassword(BaseModel):
    password: str
    confirm_password: str
    
class ForgetPassword(BaseModel):
    email: str

class CategoryType(BaseModel):
    name: str

class ProductSize(BaseModel):
    name: str 
    description: Optional[str] = None   
    
class ProductItems(BaseModel):
    cust_name: str = Field(...)
    paid_items: List[dict] = Field(...)
    delivery_mode: str = Field(...)
    delivery_address: str = Field(...)
    cust_numb: str = Field(...)
    
class ChangePassword(BaseModel):
    old_password: str
    new_password: str
    
    
    
