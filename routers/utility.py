import requests
import time
from math import ceil
from fastapi import HTTPException
import logging
import requests
import time
from fastapi import FastAPI, status, Depends, APIRouter,  UploadFile, File, Form, Query, Request, HTTPException
import hashlib, hmac, http
import os

from dotenv import load_dotenv
from email_validate import validate
import calendar
import datetime
load_dotenv()


# Verify/Validate email address

def validate_and_verify_email(input_email):
    email = input_email
    isValid = validate(
        email_address=email,
        check_format=True,
        check_blacklist=True,
        check_dns=True,
        dns_timeout=10,
        check_smtp=True,
        smtp_debug=True,
    )
    return isValid

# return a hashed string.
def generate_signature(secret: bytes, payload: bytes, digest_method = hashlib.sha512):
    return hmac.new(secret.encode('utf-8'), payload, digest_method).hexdigest()

def weeks_in_month(year, month):
    c = calendar.Calendar(firstweekday=calendar.MONDAY)
    monthcal = c.monthdatescalendar(year, month)
    return len(monthcal)

def current_year_month():
    now = datetime.datetime.now()
    return now.year, now.month

def week_of_month(dt):
    first_day = dt.replace(day=1)
    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))