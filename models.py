# models for database [SQLAlchemy]
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum, Float, JSON, TEXT, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date

from sqlalchemy_utils import URLType

from db import Base

from sqlalchemy.dialects.postgresql import UUID
import uuid
from random import randint

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255))
    password = Column(String(255))
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    is_deactivated = Column(Boolean, default=False)
    deactivated_at = Column(DateTime(timezone=True), default=datetime.now())
    is_due_for_deletion = Column(Boolean, default=False)
    is_super_admin = Column(Boolean, default = False)
    
    address = relationship("Address", back_populates="users")
    moreinfo = relationship("MoreInfo", back_populates="users")
    
    
class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True, nullable=False)
    country = Column(String(255), nullable=True)
    states = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    user_email = Column(String(255), ForeignKey("users.email", ondelete='CASCADE'))
    users = relationship("User", back_populates="address")

class MoreInfo(Base):
    __tablename__ = 'moreinfo'
    id= Column(Integer, primary_key=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    phone_num = Column(String(255), nullable=True)
    user_email = Column(String(255), ForeignKey("users.email", ondelete='CASCADE'))
    
    users = relationship("User", back_populates="moreinfo")
    