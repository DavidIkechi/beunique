from fastapi import FastAPI, status, Depends, APIRouter,  UploadFile, File, Form, Query, Request, HTTPException
from typing import List, Union, Optional
import services as _services
import models, schema
from sqlalchemy.orm import Session, load_only
from auth import (
    get_active_user,
    get_admin,
    get_current_user
)
import auth
from . import utility as utils
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import os
import cloudinary
import cloudinary.uploader
from BitlyAPI import shorten_urls
import crud
from admin_awt import main_login, get_access_token, verify_password, refresh
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from emails import send_delete_email, send_email, verify_token, send_password_reset_email, password_verif_token, send_deactivation_email

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse
from starlette.responses import RedirectResponse
from datetime import datetime, date
from fastapi_pagination import Page, Params, paginate
import locale




admin_router = APIRouter(
    prefix='/admin',
    tags=['admin'],
)

# endpoint for user login
@admin_router.post('/login', summary = "create access token for logged in user",
                  status_code= status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(_services.get_session)):
    # return token once the user has been successfully authenticated, or it returns an error.
    return await main_login(form_data, db)

@admin_router.get("/get_newsletter-subscribers", summary="Get all existing subscribers", status_code = 200)
def get_subscribers(skip: int = 0, db: Session = Depends(_services.get_session), user: models.User = Depends(get_admin)):
    try:
        subscribers = crud.get_newsletter_subscribers(db, skip=skip)
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        )
        
    return {
        "detail": subscribers
    }
    
@admin_router.post('/add_product_category', summary="Add different Category required for products")
def add_category(category: schema.CategoryType, db: Session = Depends(_services.get_session), user: models.User = Depends(get_admin)):
    try:
        
        db_cate = crud.add_category(db, category)
        if db_cate is None:
            return JSONResponse(
                status_code= 500,
                content=jsonable_encoder({"detail": "An error occurred while trying to add the category"}),
            )
    
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        )
        
    return {
        "detail": "Category was successfully added"
    }
    
@admin_router.post('/add_product_size', summary="Add different Sizes required for products")
def add_category(product: schema.ProductSize, db: Session = Depends(_services.get_session), user: models.User = Depends(get_admin)):
    try:
        db_prod = crud.add_product_size(db, product)
        if db_prod is None:
            return JSONResponse(
                status_code= 500,
                content=jsonable_encoder({"detail": "An error occurred while trying to add the product size"}),
            )
    
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        )
        
    return {
        "detail": "Product Size was successfully added"
    }
    
@admin_router.post('/add_product', summary="Add Products")
def add_product(product_name: str = Form(),
                product_price: float = Form(),
                sizes: List[str] = Form(),
                category: str = Form(),
                units: int = Form(),
                weight: str = Form(),
                sales_price: str = Form(),
                description: str = Form(),
                new_stock: bool = Form(),
                product_url: List[UploadFile] = File(..., content_type='image/*'),
                db: Session = Depends(_services.get_session), user: models.User = Depends(get_admin)):
    
    try:
        # check if category exist
        check_cate = crud.get_category(db, category)
        
        if check_cate is None:
            return JSONResponse(
                status_code= 404,
                content=jsonable_encoder({"detail": f"Category {category} doesn't exist!"}),
            )
        # check for sizes.
        cate_slug = check_cate.slug_name
        sizes = "".join(sizes)
        sizes = sizes.split(",")
        
        dress_size = []
        # get all the sizes:
        get_all_sizes = crud.get_all_sizes(db)
        
        
        for size in sizes:
            if crud.get_sizes(db, size) is None:
                return JSONResponse(
                    status_code= 404,
                    content=jsonable_encoder({"detail": f"size {size} doesn't exist!"}),
                )
        
        for each_size in get_all_sizes:
            if each_size.name in sizes:
                dress_size.append(
                    {'id': each_size.id,
                     'size':each_size.name,
                     'selected': False
                     }
                )
                
            
        all_urls = []
        for prod in product_url:
            result = cloudinary.uploader.upload(prod.file)
            url = result.get("secure_url")
            urls = [url]
            response = shorten_urls(urls)
            retrieve_url = response[0]
            new_url = retrieve_url.short_url
            all_urls.append(new_url)
            
        products = {
            "product_name": product_name.lower(),
            "product_price": product_price,
            "units": units,
            "weight": weight,
            "sales_price": sales_price,
            "description": description,
            "category": category,
            "sizes": dress_size,
            "category_slug": cate_slug,
            "image_url": all_urls,
            "new_stock": new_stock
        }
        
        if crud.get_product(db, products['product_name']) is not None:
            return JSONResponse(
                status_code= 404,
                content=jsonable_encoder({"detail": f"product name already exist!"}),
            )
            
        db_add_products = crud.add_new_product(db, products)
           
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        )
        
    return {
        "detail": "Product was successfully added."
    }
    
@admin_router.get('/all_orders', summary="get all the orders", status_code = 200)
async def get_all_stocks(params: Params = Depends(), db: Session = Depends(_services.get_session), user: models.User = Depends(get_admin)):
    try:
        # set the locale to the user's default
        locale.setlocale(locale.LC_ALL, 'en_NG.utf8')
        # format the number as a currency string with a custom symbol
        all_items = []     
        # get the records
        items = crud.get_all_orders(db)
        paid = []
        
        for item in items:
            prod_name = crud.get_product_by_id(db, int(item.paid_items[0].paid_id))
            prod_name = prod_name.product_name
            prod_name += " - " + item.paid_items[0].product_size                                
            new_item = {
                "product_name": prod_name,
                "product_id": int(item.paid_items[0].paid_id),
                "order_num": item.order_number,
                "order_email":item.email,
                "order_status": item.delivered,
                "order_quantity": int(item.paid_items[0].product_quan),
                "ordered_date": item.created_at
            }
            all_items.append(new_item)
            
        returned_page = paginate(all_items, params)
        
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        )       
    return {
        "detail": returned_page
    }

@admin_router.get('/overview')
async def get_overview(db: Session = Depends(_services.get_session), user: models.User = Depends(get_admin)):
    try:
        # get all the categories.
        all_category = len(crud.get_all_categories(db))
        # get all the orders.
        get_amount = crud.get_all_orders(db)
        total_amt = 0
        total_unit = 0
        total_stock = 0
                
        for stock in get_amount:
            if stock.delivered.lower() != "canceled":
                total_amt += float(stock.total_amount)
                total_unit  += stock.paid_items[0].product_quan
                total_stock += 1
        
        all_overview = [
            {
                "all_sales": total_amt,
                "all_units": total_unit,
                "all_categories": all_category,
                "all_orders": total_stock
            }
        ]            
        
        
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        ) 
    
    return {
        "detail": all_overview
    }
          
@admin_router.get('/all_categories')
async def get_overview(db: Session = Depends(_services.get_session), user: models.User = Depends(get_admin)):
    try:
        all_categories = crud.get_all_categories(db)
        
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        )
    
    return {
        "detail": all_categories
    } 
        
@admin_router.get('/all_product_sizes')
async def get_overview(db: Session = Depends(_services.get_session), user: models.User = Depends(get_admin)):
    try:
        all_sizes = crud.get_all_sizes(db)
        
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        )
    
    return {
        "detail": all_sizes
    }
    
    
@admin_router.delete('/delete/{category}')
async def get_overview(category: str, db: Session = Depends(_services.get_session), user: models.User = Depends(get_admin)):
    try:
        all_sizes = crud.delete_category(db, category)
        
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        )
    
    return {
        "detail": all_sizes
    }
    
@admin_router.delete('/delete/{product_id}')
async def get_overview(product_id: int, db: Session = Depends(_services.get_session), user: models.User = Depends(get_admin)):
    try:
        remove_product = crud.delete_product(db, product_id)
        
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        )
    
    return {
        "detail": remove_product
    }
    
@admin_router.get('/get_stocks')
async def get_overview(page: int = Query(1, ge=1), page_size: int = 10, db: Session = Depends(_services.get_session), user: models.User = Depends(get_admin)):
    try:
        get_product = crud.get_paginated_products(db, page, page_size)
    except Exception as e:
        return JSONResponse(
            status_code = 500,
            content = jsonable_encoder({"detail": str(e)}),
        )
        
    return {
        "detail": get_product
    }
    