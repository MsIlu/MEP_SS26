# Author: Ilu
# This file handles the database connection.
# It connects FastAPI to PostgreSQL, creates tables, and provides database sessions.

from pathlib import Path
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine
from . import models

#determines the projects main folder
BASE_DIR = Path(__file__).resolve().parents[2]

#path to .env-file in main folder
ENV_PATH = BASE_DIR / ".env"

#loads enviromentvariable from .env-File
load_dotenv(dotenv_path=ENV_PATH)

#loads databse-URL from .env-File
DATABASE_URL = os.getenv("DATABASE_URL")

#prints error-message if there is no database-URL
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing. Please check .env-File in MEP_SS26.")

#connects to postgresSQL-Database
engine = create_engine(DATABASE_URL, echo=True)

#creates all tables from db_models.py
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

#creates database-session
def get_db_session():
    return Session(engine)