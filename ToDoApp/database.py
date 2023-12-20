from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()
DB_HOST= os.getenv("DB_HOST")
DB_USER= os.getenv("DB_USER")
DB_NAME= os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# create a location of our database inside the project - sqlite:///
# SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
# connect_args={"check_same_thread":False} -> only for sqlite

SQLALCHEMY_DATABASE_URL = F"""postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"""
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()
