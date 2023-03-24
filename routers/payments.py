from fastapi import FastAPI, status, Depends, APIRouter,  UploadFile, File, Form, Query, Request, HTTPException, Header, Request
from typing import List, Union, Optional
import services as _services
import models, schema
from sqlalchemy.orm import Session
import auth
from . import utility as utils
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
import os
import cloudinary
import cloudinary.uploader
from BitlyAPI import shorten_urls
import crud
# from jwt import main_login, get_access_token, verify_password, refresh
# from emails import send_email, verify_token, send_password_reset_email, password_verif_token, send_successful_payment_email, send_failed_payment_email
from BitlyAPI import shorten_urls

from paystackapi.paystack import Paystack
from paystackapi.charge import Charge
from datetime import datetime

import json
from . import utility
from fastapi.responses import RedirectResponse

from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
import time
from rave_python import Rave
import requests

import hashlib, hmac, http

order_router = APIRouter(
    prefix='/payment',
    tags=['orders'],
)

#Can be found in .env file at base directory
RAVE_PUBLIC_KEY = os.getenv("RAVE_PUBLIC_KEY")
SECRET_KEY = os.getenv('RAVE_SECRET_KEY')

payment_endpoint = "https://api.flutterwave.com/v3/payments"
header = {'Authorization':'Bearer '+ SECRET_KEY}

# This is for flutterwave
# @order_router.post("/create_order", description="Create Paystack order for a user", status_code = 200)
# async def create_order(userPayment: schema.PaymentBase, db: Session = Depends(_services.get_session), user: models.User = Depends(auth.get_active_user)):
#     paystack = Paystack(secret_key=os.getenv('PAYSTACK_SECRET_KEY'))
#     user_email = user.email
#     try:
#         # initialize a transaction.
#         trans = paystack.transaction()

#         # get amount for the plan.
#         get_plan_details = crud.get_plan_by_name(db, userPayment.plan.lower())
#         if get_plan_details is None:
#             return JSONResponse(
#                 status_code= 400,
#                 content=jsonable_encoder({"detail": "Sorry, we do not have that plan"}),
#             )
             
#         amount = get_plan_details.price * userPayment.minutes * 100
#         if amount/100 < 10:
#             return JSONResponse(
#                 status_code= 400,
#                 content=jsonable_encoder({"detail": "Sorry, minimum order you can place is $10"}),
#             )
        
#         # initialise the transaction
#         res = trans.initialize(email= user_email, amount = amount,
#                                metadata = {'minutes': userPayment.minutes, 'plan': userPayment.plan,
#                                            'cancel_action': "https://heed.cx/paymentFailure"},
#                                callback_url= "https://heed.cx/paymentSuccess")
        
#         if res['status'] == True:
#         # get the authorization url, access_code, and also the reference number.
#             autho_url = res['data']['authorization_url']
#             access_code = res['data']['access_code']
#             reference = res['data']['reference']
#         else:
#             return JSONResponse(
#                 status_code= 400,
#                 content=jsonable_encoder({"detail": "An error occured while trying to initialise payment, please try again"}),
#             )
         
#     except Exception as e:
#         return JSONResponse(
#             status_code= 500,
#             content=jsonable_encoder({"detail": str(e)}),
#         )
    
#     return {"detail": {
#         "payment_url": autho_url,
#         "gateway": "paystack"
#         }
#     }

@order_router.post("/create_order", description="Create Paystack order for a user", status_code = 200)
async def create_order(userPayment: schema.ProductItems, db: Session = Depends(_services.get_session), user: models.User = Depends(auth.get_active_user)):
    paystack = Paystack(secret_key=os.getenv('PAYSTACK_SECRET_KEY'))
    user_email = user.email
    try:
        # initialize a transaction.
        # 3.9% + 100 (paystack)
        trans = paystack.transaction()
        # get product_dict
        product_dict = utils.get_product_meta_data(userPayment)
        # pass the product id and quantity and size.
        # update product
        prod_price = crud.get_product_price(db, product_dict['paid_items'])
        
        if prod_price is None:
            return JSONResponse(
                status_code= 400,
                content=jsonable_encoder({"detail": "Please check that you've selected the right products and quantity"}),
            )
            
        # get the shipping fee.
        prod_shipping = utils.get_shipping_fee(product_dict['delivery_mode'], product_dict['delivery_address'])
        total_amount = prod_shipping + prod_price
        
        product_dict['total_amount'] = total_amount
        product_dict['shipping_fee'] = prod_shipping
        product_dict['prod_price'] = prod_price
        product_dict['gateway'] = "Paystack"
        # initialise the transaction
        res = trans.initialize(email= user_email, amount = total_amount * 100,
                               metadata = {'product':product_dict, 'email': user_email, 'cancel_action': os.getenv("CANCEL_URL")},
                               callback_url= os.getenv("PAYSTACK_SUCCESS"))
        
        if res['status'] == True:
        # get the authorization url, access_code, and also the reference number.
            autho_url = res['data']['authorization_url']
            access_code = res['data']['access_code']
            reference = res['data']['reference']
        else:
            return JSONResponse(
                status_code= 400,
                content=jsonable_encoder({"detail": "An error occured while trying to initialise payment, please try again"}),
            )
         
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        )
    
    return {"detail": {
        "payment_url": autho_url,
        "gateway": "paystack"
        }
    }
    
@order_router.post("/verify_order/{ref_code}", description="Verify Paystack order for a user", status_code = 200)
async def verify_order(ref_code: str, db: Session = Depends(_services.get_session), user: models.User = Depends(auth.get_active_user)):
    paystack = Paystack(secret_key=os.getenv('PAYSTACK_SECRET_KEY'))
    user = crud.get_user_by_email(db, email=user.email)

    try:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
        veri = paystack.transaction().verify(reference = ref_code)
        get_status = veri['data']
        get_date = get_status['paid_at'].split("T")
        conv_date = get_date[1].split(".")[0]
        new_date1 = get_date[0] + " " + conv_date
        new_date2 = datetime.strptime(new_date1, "%Y-%m-%d %H:%M:%S")
        transaction = {"amount": get_status['amount']/100,
                        "trans_id": str(get_status['id']),
                        "reference": get_status['reference'],
                        "customer_name": get_status['metadata']['product']['customer_name'],
                        "paid_items": get_status['metadata']['product']['paid_items'],
                        "time_paid": new_date2,
                        "payment_channel": get_status['channel'],
                        "customer_number": get_status['metadata']['product']['customer_number'],
                        "delivery_mode": get_status['metadata']['product']['delivery_mode'],
                        "delivery_address": get_status['metadata']['product']['delivery_address'],
                        "total_amount": get_status['metadata']['product']['total_amount'],
                        "shipping_fee": get_status['metadata']['product']['shipping_fee'],
                        "prod_price": get_status['metadata']['product']['prod_price'],   
                        "email_address": user.email,
                        "payment_gateway": get_status['metadata']['product']['gateway']
                    }
        # check if the transaction has already been submitted
        check_trans = crud.check_transaction(db, ref_code)
        
        if check_trans is not None:
            return {"detail": transaction, 'status':"failed"}
        
        if get_status['status'].strip().lower() != "success":
            # send a mail receipt
            # await send_transaction_failure_receipt([user.email], transaction)
            # await send_failed_payment_email([email], user, 
            #                                     plan=transaction['plan'], 
            #                                     minutes=transaction['minutes'], 
            #                                     price=transaction['amount'])
            return JSONResponse(
                status_code= 400,
                content=jsonable_encoder({"detail": "Sorry, your payment failed, please try again"}),
            )
            
            
            #push the details into the database.
        trans_crud = crud.store_transaction(db, transaction)
            # top_up_details = {"minutes": get_status['metadata']['minutes'],
            #                "plan": get_status['metadata']['plan']}
            # # top up the users account
            # top_up = crud.top_up(db,user.email, top_up_details)
            # # send a mail receipt
            # await send_successful_payment_email([email], user, 
            #                                         plan=transaction['plan'], 
            #                                         minutes=transaction['minutes'], 
            #                                         price=transaction['amount'])
            # await send_transaction_success_receipt([user.email], transaction)
            
    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        )
        
    return {
        "detail": transaction
    }
    
    
# paystack webhook.
@order_router.post('/paystack_webhook', include_in_schema=False)
async def heed_webhook_view(request: Request, db: Session = Depends(_services.get_session)):
    paystack_secret = os.getenv('PAYSTACK_SECRET_KEY')

    try:
        payload = await request.body()
        # get the header
        paystack_header = request.headers.get('x-paystack-signature')
        # convert data to dictionary.
        get_data = json.loads(payload.decode('utf-8'))
        signature = utils.generate_signature(paystack_secret, payload)
        if signature != paystack_header:
            return JSONResponse(
                status_code= 401,
                content=jsonable_encoder({"detail": "Authentication error"}),
            )

        # get the reference
        ref_code = get_data['data']['reference']
        check_trans = crud.check_transaction(db, ref_code)

        # get all the data need.
        get_status = get_data['data']
        get_date = get_status['paid_at'].split("T")
        conv_date = get_date[1].split(".")[0]
        new_date1 = get_date[0] + " " + conv_date
        new_date2 = datetime.strptime(new_date1, "%Y-%m-%d %H:%M:%S")
        transaction = {"amount": get_status['amount']/100,
                        "trans_id": str(get_status['id']),
                        "reference": get_status['reference'],
                        "customer_name": get_status['metadata']['product']['customer_name'],
                        "paid_items": get_status['metadata']['product']['paid_items'],
                        "time_paid": new_date2,
                        "payment_channel": get_status['channel'],
                        "customer_number": get_status['metadata']['product']['customer_number'],
                        "delivery_mode": get_status['metadata']['product']['delivery_mode'],
                        "delivery_address": get_status['metadata']['product']['delivery_address'],
                        "total_amount": get_status['metadata']['product']['total_amount'],
                        "shipping_fee": get_status['metadata']['product']['shipping_fee'],
                        "prod_price": get_status['metadata']['product']['prod_price'],   
                        "email_address": get_status['metadata']['email'],
                        "payment_gateway": get_status['metadata']['product']['gateway']
                    }
        user = crud.get_user_by_email(db, email=transaction['email_address'])
        email = transaction['email_address']
        if check_trans is not None:
            return {"detail": transaction}

        if get_data['event'] == "charge.success":
            # store in the crud database.
            trans_crud = crud.store_transaction(db, transaction)
            # top_up_details = {"minutes": get_status['metadata']['minutes'],
            #             "plan": get_status['metadata']['plan']}
            # # top up the users account
            # top_up = crud.top_up(db,user.email, top_up_details)
            # # send a mail receipt
            # await send_successful_payment_email([email], user, 
            #                                     plan=transaction['plan'], 
            #                                     minutes=transaction['minutes'], 
            #                                     price=transaction['amount'])

            # get the transaction details
        else:
            # an error must have occurred, send error mail.
            # await send_failed_payment_email([email], user, 
            #                                     plan=transaction['plan'], 
            #                                     minutes=transaction['minutes'], 
            #                                     price=transaction['amount'])
            return JSONResponse(
                status_code= 404,
                content=jsonable_encoder({"detail": "Transaction failed!."}),
            )

    except Exception as e:
        return JSONResponse(
            status_code= 500,
            content=jsonable_encoder({"detail": str(e)}),
        ) 
     
        
    return {
        "detail": transaction
    }

