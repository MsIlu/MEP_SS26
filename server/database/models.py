# Author: Ilu
# This file defines the database models.
# SQLModel uses these classes to create the corresponding tables in PostgreSQL.

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

# User table for login and authentication
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=100)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)