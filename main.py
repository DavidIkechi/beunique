from typing import List, Union, Optional
from fastapi import Depends, FastAPI, UploadFile, File, status, HTTPException, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from rocketry import Rocketry
from rocketry.conds import (
    every, hourly, daily,
    after_success,
    true, false
)
import logging

import asyncio
import uvicorn
import models, json
from routers.users import user_router

from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db import Base, engine, SessionLocal
from sqlalchemy.orm import Session
import crud, schema
from starlette.requests import Request
import fastapi as _fastapi
import cloudinary
import cloudinary.uploader
from BitlyAPI import shorten_urls
from datetime import datetime, timedelta, date
import shutil
import os
from dotenv import load_dotenv
from starlette.responses import FileResponse
from starlette.requests import Request
from starlette.responses import Response
import uuid
import random, string, ssl
from scheduler import cron_schedule as cron_rocketry


load_dotenv()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


description = """
BeUnique 
"""

tags_metadata = [
    {
        "name": "users",
        "description": "CRUD User Endpoints",
    },
]

# create the database.
models.Base.metadata.create_all(engine)
# Open a SSH tunnel


app = FastAPI(
    title="BeUnique API",
    description=description,
    version="0.0.1",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# add all the routers here.


class Server(uvicorn.Server):
    """Customized uvicorn.Server
    
    Uvicorn server overrides signals and we need to include
    Rocketry to the signals."""
    def handle_exit(self, sig: int, frame) -> None:
        cron_rocketry.session.shut_down()
        return super().handle_exit(sig, frame)

async def main() -> None:
    server = Server(uvicorn.Config(
        "main:app", 
        host=os.getenv("HOST"), 
        port=int(os.getenv("PORT")), 
        reload=os.getenv("RELOAD"),
        workers=1, 
        loop="asyncio")
    )
    
    api = asyncio.create_task(server.serve())
    sched = asyncio.create_task(cron_rocketry.serve())
    await asyncio.wait([sched, api])
    
app.include_router(
    user_router
    )

@app.get("/")
async def ping():
    return {"message": "BEUNIQUE IS UP"}

if __name__ == "__main__":
    # Print Rocketry's logs to terminal
    # logger = logging.getLogger("rocketry.task")
    # logger.addHandler(logging.StreamHandler())

    # Run both applications
    asyncio.run(main())
