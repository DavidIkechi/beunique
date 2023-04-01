from sqlalchemy.orm import Session, load_only
from fastapi import HTTPException, status, UploadFile, File, Depends, Response
import models, schema
from random import randint
from passlib.context import CryptContext
from fastapi import HTTPException 
import cloudinary
import cloudinary.uploader
import datetime as dt
from datetime import datetime
import uuid
from sqlalchemy import or_, null, desc
from sqlalchemy.sql import func
from collections import defaultdict
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_product_id(db: Session):
    prod_id = randint(1000000000, 9999999999)
    while get_product_by_number(db, prod_id) is not None:
        prod_id = randint(1000000000, 9999999999)
        
    return prod_id

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schema.Users):
    # set the admin.
    if user.email.lower() in ['beuniqueglobal@gmail.com','davidakwuruu@gmail.com']:
        is_admin = True
    else:
        is_admin = False
    # create the user.
    db_user = models.User(is_admin= is_admin, is_active = True, is_verified = True,
                          email=user.email.lower(), password=pwd_context.hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # add the address and the more information.
    create_address(db, user.email)
    create_more_info(db, user.email)
    return db_user

def create_address(db: Session, email_add: str):
    db_admin = get_user_by_email(db, email_add)
    db_address = models.Address(user_id=db_admin.id)
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

def create_more_info(db: Session, email_add: str):
    db_admin = get_user_by_email(db, email_add)
    db_info = models.MoreInfo(user_id=db_admin.id)
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

def update_user_address(db: Session, user_address: schema.Address, user_id: int):
    # get the row with that details first.
    db_address = db.query(models.Address).get(user_id)
    db_address.country = user_address.country
    db_address.states = user_address.states
    db_address.city = user_address.city
    db_address.address = user_address.address
    db.commit()
    
    return db_address

def update_phone(db: Session, user_address: schema.MoreInfo, user_id: int):
    # get the row with that details first.
    db_details = db.query(models.MoreInfo).get(user_id)
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

def reset_password(db: Session, password: str, user: models.User):
    user.password = pwd_context.hash(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def add_category(db: Session, category: schema.CategoryType):
    db_category = models.Category(category_name = category.name.lower())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def add_product_size(db: Session, product: schema.ProductSize):
    if product.description is not None:
        db_size = models.ProductSize(name = product.name.lower(), description = product.description)
    else:
        db_size = models.ProductSize(name = product.name.lower())
    db.add(db_size)
    db.commit()
    db.refresh(db_size)  
    return db_size

def get_category(db: Session, category: str):
    return db.query(models.Category).filter(models.Category.category_name == category.lower()).first()

def get_category_by_slug(db: Session, category_slug: str):
    return db.query(models.Category).filter(models.Category.slug_name == category_slug.lower()).first()

    
def get_sizes(db: Session, product_size: str):
    return db.query(models.ProductSize).filter(models.ProductSize.name == product_size.lower()).first()

def add_new_product(db: Session, products: dict):
    db_prod = models.Product(
        product_name = products['product_name'], 
        product_num = generate_product_id(db),
        weights = products['weight'],
        sales_price = products['sales_price'],
        category = products['category'],
        sizes = products['sizes'],
        price = products['product_price'],
        units = products['units'],
        product_url = products['image_url'],
        description = products['description'],
        slug_name = products['category_slug'],
        new_stock = products['new_stock']
    )
    db.add(db_prod)
    db.commit()
    db.refresh(db_prod)
    db_flash = models.FlashSales(product_name = products['product_name'])
    db.add(db_flash)
    db.commit()
    db.refresh(db_flash)
    return db_prod
    
def get_product(db: Session, product_name: str):
    return db.query(models.Product).filter(models.Product.product_name == product_name.lower()).first()

def get_product_by_id(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_product_by_slug_name(db: Session, product_slug: str):
    return db.query(models.Product).filter(models.Product.category == slug_name.lower()).all()

def get_product_by_number(db: Session, product_num: int):
    return db.query(models.Product).filter(models.Product.product_num == product_num).first()

# def get_all_products(db: Session):
#     return db.query(models.Product).all()

def get_all_categories(db: Session):
    return db.query(models.Category).all()

def get_all_sizes(db: Session):
    return db.query(models.ProductSize).all()

def get_all_products(db: Session, category: str):
    return db.query(models.Product).filter(models.Product.category == category.lower()).all()
    
def delete_category(db:Session, category: str):
    db.query(models.Category).filter(models.Category.category_name == category.lower()).delete()
    db.commit()
    return {
        "detail": "successfully deleted"
    }
    
def delete_product(db:Session, product_id: int):
    db.query(models.Product).filter(models.Product.id == product_id).delete()
    db.commit()
    return {
        "detail": "product successfully deleted"
    }
    
def get_new_products(db: Session, limit: int = 40):
    return db.query(models.Product).filter(models.Product.new_stock == True).order_by(desc(models.Product.added_at)).limit(limit).all()

def get_products(db: Session, limit: int = 40):
    return db.query(models.Product).order_by(desc(models.Product.added_at)).limit(limit).all()


def get_product_price(db: Session, product: list):
    total = 0
    for item in product:
        # get the item based on the product_id.
        get_product = get_product_by_id(db, item['id'])
        if get_product is None:
            return None
        if get_product.units < int(item['quantity']):
            return None
        total +=float(get_product.sales_price) * float(item['quantity'])
        
    return total
        
def check_transaction(db: Session, ref_code: str):
    return db.query(models.PaidItems).filter(models.PaidItems.order_number == ref_code).first()
        
def store_transaction(db: Session, trans: dict):
    # store transaction
    transt = models.PaidItems(
        email = trans['email_address'],
        order_number = trans['reference'],
        prod_amount = trans['prod_price'],
        ship_amount = trans['shipping_fee'],
        total_amount = trans['total_amount'],
        product_id = trans['trans_id'],
        payment_gateway = trans['payment_gateway'],
        payment_type = trans['payment_channel'],
        created_at = trans['time_paid'],
    )
    
    db.add(transt)
    db.commit()
    
    get_trans = check_transaction(db , trans['reference'])
    
    paid_products = models.PaidProduct(
        product_quan = int(trans['quantity']),
        paid_id = int(trans['product_id']),
        product_size = trans['product_size'],
        delivery_mode = trans['delivery_mode'],
        delivery_address = trans['delivery_address'],
        customer_name = trans['customer_name'],
        customer_number = trans['customer_number'],
        shipping_date = datetime.now() + dt.timedelta(days=1),
        product_trans = get_trans.id
    )
    db.add(paid_products)
    db.commit()
    
    # for item in trans['paid_items']:
        # get the item based on the product_id.
    get_product = get_product_by_id(db, int(trans['product_id']))
    get_product.units -=  int(trans['quantity'])
    db.add(get_product)
    db.commit()
    db.refresh(get_product)
    
    return paid_products


def get_paginated_products(db: Session, page, page_size):
    get_object = db.query(models.Product).options(load_only(
        models.Product.product_name,
        models.Product.product_num,
        models.Product.category,
        models.Product.sales_price,
        models.Product.units
    ))
    
    page_offset = Params(page=page, size=page_size)
    data_result = paginate(get_object, page_offset)
    
    return data_result

def get_all_orders(db: Session):
    return db.query(models.PaidItems).all()


def get_ordered_items(db: Session, email: str):
    return db.query(models.PaidItems).filter(models.PaidItems.email == email).all()

    
    
     