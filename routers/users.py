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
from emails import send_delete_email, verify_token, send_password_reset_email, password_verif_token, send_deactivation_email

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
    
@user_router.post('/update_address')
async def update_address(user_address: schema.Address, db: Session = Depends(_services.get_session),user: models.User = Depends(get_active_user)):
    try:
        email = user.email
        country = user_address.country.strip()
        states = user_address.states.strip()
        city = user_address.city.strip()
        
        if country == "" or states == "" or city == "":
            return JSONResponse(
                status_code=400,
                content = jsonable_encoder({"detail": "No field should be left empty"})
            )
        
        update_add = crud.update_user_address(db, user_address, email)
        # update the account.
    except:
        raise HTTPException(status_code=500, detail="An unknown error occured. Try Again")
    
    return{
        "detail": "Address was successfully updated."
    }
    
@user_router.post('/update_user_details')
async def update_user_details(user_address: schema.MoreInfo, db: Session = Depends(_services.get_session),user: models.User = Depends(get_active_user)):
    try:
        if not user_address.full_name or not user_address.phone_num:
            return JSONResponse(
                    status_code=400,
                    content = jsonable_encoder({"detail": "No field should be empty"})
                )
        
        update_phone = crud.update_phone(db, user_address, user.email)
        
    except Exception as e:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({"detail": str(e)}),
        )
        
    return{
        "detail":"Update was Successful"
    }
    
@user_router.post("/newsletter-subscription", summary="newsletter subscription", status_code = 200)
def subscribe_to_newletter(subscriber: schema.Newsletter, db: Session = Depends(_services.get_session)):
    db_subscriber = crud.check_subscrition_email(db, email=subscriber.email)

    if db_subscriber:
        raise HTTPException(status_code=400, detail="You are already subscribed to our newsletter")
    try:
        email_exists = utils.validate_and_verify_email(subscriber.email)
        if not email_exists:
            return JSONResponse(
                status_code=400,
                content = jsonable_encoder({"detail": "User email couldnot be verified!, please use a proper email"})
            )
        crud.add_newsletter_subscriber(db=db, email_add = subscriber.email)
        return {
            "detail": subscriber.email
        }
    except:
        raise HTTPException(status_code=500, detail="An unknown error occured. Try Again") 

@user_router.get('/user_detail', summary="get users detail", status_code = 200)
async def get_user(db: Session = Depends(_services.get_session),user: models.User = Depends(get_active_user)):
    try:
        email_address = user.email
        db_user = crud.get_user_by_email(db, email=user.email)
        all_address = db_user.address[0]
        all_details = db_user.moreinfo[0]
        
        all_details = {
            "email": db_user.email,
            "country": all_address.country,
            "state": all_address.states,
            "city": all_address.city,
            "full_name":all_details.full_name,
            "phone": all_details.phone_num
        }
    except Exception as e:
        return JSONResponse(
                status_code= status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder({"detail": str(e)}),
            )
    return {
        "detail": all_details
    }
    
@user_router.patch('/reset-password', summary = "reset password", status_code = 200)
async def reset_password(token: str, new_password: schema.UpdatePassword, db: Session = Depends(_services.get_session)):
    
    try:
        email = password_verif_token(token)
        user: models.User = crud.get_user_by_email(db, email)
            
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        if new_password.password != new_password.confirm_password:
            raise HTTPException(status_code=400, detail="Password do not match")
          
        its_match = verify_password(new_password.password, user.password)
        its_le_eight = len(new_password.password) < 8

        if its_match:
            raise HTTPException(status_code=500, detail="New password cannot be the same as old password")
        elif its_le_eight:
            raise HTTPException(status_code=500, detail="Password must have at least 8 characters")

        
        reset_done = crud.reset_password(db, new_password.password, user)

        if reset_done is None:
            raise HTTPException(status_code=500, detail="Failed to update password")
        
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        )
    
    return {
        "detail":reset_done
        }
    
@user_router.post('/forgot-password', summary = "get token for password reset", status_code = 200)
async def forgot_password(email: schema.ForgetPassword, db: Session = Depends(_services.get_session)):
    
    try:
        user: models.User = crud.get_user_by_email(db, email.email)
        if user is None:
            return JSONResponse(
                status_code= status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder({"detail": "User not found"}),
            )        
        token = await send_password_reset_email([email.email], user)
    except Exception as e:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({"detail": str(e)}),
        )
    return {"detail": user}

    
