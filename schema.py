from datetime import datetime
from enum import Enum
from fastapi import FastAPI, File, Form
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Extra
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
    
class MoreInfo(BaseModel):
    full_name: Optional[str] = None
    phone_num: Optional[str] = None
    
    
