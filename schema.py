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

    