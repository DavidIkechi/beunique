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