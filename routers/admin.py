from fastapi import FastAPI, status, Depends, APIRouter,  UploadFile, File, Form, Query, Request, HTTPException
from typing import List, Union, Optional
import services as _services
import models, schema
from fastapi_pagination import Page, paginate, Params
from sqlalchemy.orm import Session
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
from awt import main_login, get_access_token, verify_password, refresh
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from emails import send_delete_email, send_email, verify_token, send_password_reset_email, password_verif_token, send_deactivation_email

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse
from starlette.responses import RedirectResponse
from datetime import datetime, date


admin_router = APIRouter(
    prefix='/admin',
    tags=['admin'],
)


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
def add_category(skip: int = 0, db: Session = Depends(_services.get_session), user: models.User = Depends(get_admin)):
    try:
        email = user.email
    
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        )
        
    return {
        "detail": "yes"
    }
        
