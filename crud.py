from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile, File, Depends, Response
import models, schema
from random import randint
from passlib.context import CryptContext
from fastapi import HTTPException 
import cloudinary
import cloudinary.uploader
from datetime import datetime
import uuid
from sqlalchemy import or_, null
from sqlalchemy.sql import func
from collections import defaultdict

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_uuid():
    return str(uuid.uuid4())

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schema.Users):
    # set the admin.
    is_admin= True
    # create the user.
    db_user = models.User(is_admin= is_admin, is_active = True, is_verified = True,
                          email=user.email, password=pwd_context.hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # add the address and the more information.
    create_address(db, user.email)
    create_more_info(db, user.email)
    return db_user

def create_address(db: Session, email_add: str):
    db_address = models.Address(user_email=email_add)
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

def create_more_info(db: Session, email_add: str):
    db_info = models.MoreInfo(user_email=email_add)
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info

def add_newsletter_subscriber(db: Session, email_add: str):
    db_subscriber = models.Newsletter(email = email_add)
    db.add(db_subscriber)
    db.commit()
    db.refresh(db_subscriber)
    return db_subscriber

def check_subscrition_email(db: Session, email: str):
    return db.query(models.Newsletter).filter(models.Newsletter.email == email).first()


def get_newsletter_subscribers(db: Session, skip: int = 0):
    return db.query(models.Newsletter).offset(skip).all()

def update_user_address(db: Session, user_address: schema.Address, email_add: str):
    # get the row with that details first.
    db_address = db.query(models.Address).filter(models.Address.user_email == email_add).first()
    db_address.country = user_address.country
    db_address.states = user_address.states
    db_address.city = user_address.city
    db.commit()
    return db_address

def update_phone(db: Session, user_address: schema.MoreInfo, email_add: str):
    # get the row with that details first.
    db_details = db.query(models.MoreInfo).filter(models.MoreInfo.user_email == email_add).first()
    if not user_address.full_name or user_address.full_name.strip() == "":
        # update the phone number.
        db_details.phone_num = user_address.phone_num
    elif not user_address.phone_num or user_address.phone_num.strip() == "":
        # update the full name.
        db_details.full_name = user_address.full_name 
    else: 
        db_details.full_name = user_address.full_name
        db_details.phone_num = user_address.phone_num    
    db.commit()
    return db_details
