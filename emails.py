from fastapi import (BackgroundTasks, UploadFile,File, Form, Depends, HTTPException, status)
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from typing import List, Dict, Any
from jose import jwt, JWTError
from fastapi.exceptions import HTTPException
from datetime import datetime, timedelta
from awt import credentials_exception
from dotenv import dotenv_values
from models import User
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi.responses import JSONResponse
from crud import get_user_by_email
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr, BaseModel



# Load all environment variables
load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv('EMAIL'),
    MAIL_PASSWORD = os.getenv('PASS'),
    MAIL_FROM = os.getenv('EMAIL'),
    MAIL_PORT = 465,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_FROM_NAME="BEUNIQUE",
    MAIL_STARTTLS = False,
    USE_CREDENTIALS = True,
    MAIL_SSL_TLS= True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER='templates'

)

class EmailSchema(BaseModel):
    body: Dict[str, Any]


async def send_password_reset_email(email: List, instance: User):
    expire = datetime.utcnow() + timedelta(minutes=1440)

    token_data = {
        'sub': instance.email,
        'exp': expire,
    }

    token = jwt.encode(token_data, os.getenv('SECRET'), algorithm='HS256')
    url = os.getenv("HOST_URL")
    emails: EmailSchema = {
        "body": {
            "url": f"{url}reset_password?token={token}",
            "firstname": "Esteem User"
        } 
    }

    message = MessageSchema(
        subject = "Password Reset",
        recipients =email,
        template_body=emails.get("body"),
        subtype=MessageType.html,
    )

    fm =FastMail(conf)
    await fm.send_message(message=message, template_name='ResetPassword/index.html')

    return token



def password_verif_token(token):
    try:
        payload = jwt.decode(token, os.getenv('SECRET'), algorithms=['HS256'])
        email:str = payload.get('sub')
        # exp_date: datetime = payload.get('exp')
    except JWTError:
        raise credentials_exception
    
    return email

async def send_deactivation_email(email: List, instance: User):

    emails: EmailSchema = {
        "body": {
            "firstname": instance.first_name
        } 
    }

    message = MessageSchema(
        subject = "Account Deactivation",
        recipients =email,
        template_body=emails.get("body"),
        subtype=MessageType.html,
    )

    fm =FastMail(conf)
    await fm.send_message(message=message, template_name='Deactivation/index.html')

    return {
        "detail": "Your Account has been deactivated successfully"
    }

async def send_delete_email(email: List, instance: dict):

    emails: EmailSchema = {
        "body": {
            "firstname": instance["first_name"]
        } 
    }

    message = MessageSchema(
        subject = "Account Deletion",
        recipients =email,
        template_body=emails.get("body"),
        subtype=MessageType.html,
    )

    fm =FastMail(conf)
    await fm.send_message(message=message, template_name='Deletion/index.html')


async def verify_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, os.getenv('SECRET'), algorithms=['HS256'])
        user = get_user_by_email(db, payload.get("email"))
        
        if user is None:
            return JSONResponse(
                status_code= 400,
                content=jsonable_encoder({"detail": "Token not authorized for user"}),
            )
    except Exception as e:
        return False
        
    return user

async def send_successful_payment_email(email: List, instance: User, plan, minutes, price):

    emails: EmailSchema = {
        "body": {
            "url": f"https://heed.cx/dashboard",
            "firstname": instance.first_name,
            "plan": plan,
            "minutes" : minutes,
            "price" : price
        } 
    }

    message = MessageSchema(
        subject = "HEED - Successful Top-Up",
        recipients =email,
        template_body=emails.get("body"),
        subtype=MessageType.html,
    )

    fm =FastMail(conf)
    await fm.send_message(message=message, template_name='TopUp/success.html')

async def send_failed_payment_email(email: List, instance: User, plan, minutes, price, reference):

    emails: EmailSchema = {
        "body": {
            "firstname": instance.first_name,
            "plan": plan,
            "minutes" : minutes,
            "price" : price,
            "reference": reference
        } 
    }

    message = MessageSchema(
        subject = "HEED - Failed Top-up",
        recipients =email,
        template_body=emails.get("body"),
        subtype=MessageType.html,
    )

    fm =FastMail(conf)
    await fm.send_message(message=message, template_name='TopUp/failure.html')

