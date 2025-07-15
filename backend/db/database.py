from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# to load environment variables from .env file
load_dotenv()

# to read database url from .env
DATABASE_URL = os.getenv("DB_URL")

if DATABASE_URL is None:
    raise Exception("DB_URL not found in .env file!")

# to Create database engine
engine = create_engine(DATABASE_URL)

# to Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
