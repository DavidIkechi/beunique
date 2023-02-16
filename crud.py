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
    # create_user_profile(db, company_id, user.email)
    return db_user
