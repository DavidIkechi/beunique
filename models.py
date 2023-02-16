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
    