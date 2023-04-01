# connection to database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool, NullPool, QueuePool
import cloudinary
import os

from dotenv import load_dotenv

load_dotenv()

# cloudinary config
cloudinary.config(
    cloud_name = os.getenv('CLOUD_NAME'),
    api_key = os.getenv('CLOUD_KEY'),
    api_secret = os.getenv('CLOUD_SECRET'),
    secure = True
)
    
def get_db_conn_string():
    DB_HOST = os.environ['DB_HOST']
    DB_NAME = os.environ['DB_NAME']
    DB_USER = os.environ['DB_USER']
    DB_PASS = os.environ['DB_PASS']
    DB_CONNECTION = DB_USER+":"+DB_PASS+"@"+DB_HOST+"/"+DB_NAME
    
    return "mysql+mysqlconnector://"+DB_CONNECTION


# SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://"+DB_CONNECTION

# SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:10of10in10@localhost/heed"

database_url = get_db_conn_string()
poolclass = QueuePool
poolsize=5
maxoverflow=10
pooltimeout=10
pre_ping = False
connect_args = {}
connect_args["connect_timeout"] = 60 * 4
# database_url = "sqlite:///./bunique.db"
# poolclass = StaticPool
# pre_ping = False
# connect_args = {"check_same_thread": False}
  
engine = create_engine(database_url, pool_pre_ping = pre_ping, poolclass = poolclass, pool_size=poolsize, 
                       pool_timeout = pooltimeout, max_overflow = maxoverflow,
                       connect_args = connect_args)  


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()