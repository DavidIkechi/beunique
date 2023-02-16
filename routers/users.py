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


user_router = APIRouter(
    prefix='/users',
    tags=['users'],
)

# endpoint for user login
@user_router.post('/login', summary = "create access token for logged in user",
                  status_code= status.HTTP_200_OK)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(_services.get_session)):
    # return token once the user has been successfully authenticated, or it returns an error.
    return await main_login(form_data, db)


# creating a users account.
@user_router.post("/create_users", status_code= status.HTTP_201_CREATED, 
                  summary = "create/register a new user user")
async def create_user(user: schema.Users, db: Session = Depends(_services.get_session)):
    db_user = crud.get_user_by_email(db, email=user.email)
    # if user exists, throw an exception.
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # check if email exists and is valid
    email_exists = utils.validate_and_verify_email(user.email)
    if not email_exists:
        return JSONResponse(
            status_code=400,
            content = jsonable_encoder({"detail": "User email couldnot be verified!, please use a proper email"})
        )
    # create the user before sending a mail.
    new_user = crud.create_user(db=db, user=user)
    # Sawait send_email([user.email], user)
        
    return {    
        "detail" : "Account was successfully created."
    }