# models for database [SQLAlchemy]
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum, Float, JSON, TEXT, Date, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date

from sqlalchemy_utils import URLType
from slugify import slugify



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
    address = Column(TEXT, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    users = relationship("User", back_populates="address")

class MoreInfo(Base):
    __tablename__ = 'moreinfo'
    id= Column(Integer, primary_key=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    phone_num = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    
    users = relationship("User", back_populates="moreinfo")
    
class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key = True, nullable=False)
    slug_name = Column(String(255), unique = True, nullable = False)
    category_name = Column(String(255), unique = True, nullable = False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_slug()
        
    def generate_slug(self):
        self.slug_name = slugify(self.category_name)
    
class ProductSize(Base):
    __tablename__ = "product_size"
    id = Column(Integer, primary_key = True, nullable=False)
    name = Column(String(255), unique = True, nullable = False)
    description = Column(String(255), nullable = True)
    
class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key = True, nullable=False)
    product_name = Column(String(255), unique=True, nullable=False)
    slug_name = Column(String(255), unique=True)
    product_num = Column(Integer)
    weights = Column(String(255), nullable=False)
    sales_price = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    sizes = Column(JSON, nullable = False)
    price = Column(Float, nullable=False, index=True)
    units = Column(Integer, nullable=False, index=True)
    product_url = Column(JSON, nullable=False)
    description = Column(TEXT)
    new_stock =  Column(Boolean, default = False)
    out_of_stocks = Column(Boolean, default = False)
    added_at = Column(DateTime(timezone=True), default=datetime.now())

    flashsales = relationship("FlashSales", back_populates="products")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_slug()
        
    def generate_slug(self):
        self.slug_name = slugify(self.product_name)
    
class FlashSales(Base):
    __tablename__ = 'flash_sales'
    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    end_at = Column(DateTime(timezone=True), default=datetime.now())
    flash_on = Column(Boolean, default = False)
    percentage = Column(Float, nullable=True)
    product_name = Column(String(255), ForeignKey("product.product_name", ondelete='CASCADE'))
    products = relationship("Product", back_populates="flashsales")
    
     # Add a check constraint to ensure end at >= created at
    __table_args__ = (
        CheckConstraint('end_at >= created_at', name='check_end_at_time_greater_than_created_at_time'),
    )
    
class PaidItems(Base):
    __tablename__ = 'paid_items'
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(255), nullable=False)
    order_number = Column(String(255), nullable=False)
    prod_amount = Column(Float, nullable=False)
    ship_amount = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    product_id = Column(String(255), nullable=False) 
    payment_type = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    payment_gateway = Column(String(255), nullable=False)
    delivered = Column(String(255), default="sorting")
    paid_items = relationship("PaidProduct", back_populates="paid_product")

class PaidProduct(Base):
    __tablename__ = 'paid_products'
    id = Column(Integer, primary_key=True, nullable=False)
    product_quan = Column(Integer, default= 0, nullable = False)
    paid_id = Column(Integer, default=0, nullable=False)
    product_size = Column(String(255), default="", nullable=False)
    delivery_mode = Column(String(255), nullable = False)
    delivery_address = Column(TEXT, nullable = False)
    customer_name = Column(String(255), nullable = False)
    customer_number = Column(String(255), nullable = False)
    shipping_date = Column(DateTime(timezone=True))
    product_trans= Column(Integer, ForeignKey("paid_items.id", ondelete='CASCADE'))
    paid_product = relationship("PaidItems", back_populates="paid_items")      