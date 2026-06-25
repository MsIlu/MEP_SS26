# Author: Ilu
# This file handles the database connection.
# It connects FastAPI to PostgreSQL, creates tables, and provides database sessions.

from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy import text
from sqlmodel import SQLModel, Session, create_engine
from . import models
from sqlmodel import Session
from sqlalchemy import text
from .catalog import models as catalog_models

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

def _env_flag(name: str, *, default: bool = False) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


#connects to postgresSQL-Database
engine_options = {"echo": _env_flag("SQL_ECHO")}

if DATABASE_URL.startswith(("postgresql://", "postgresql+")):
    engine_options["connect_args"] = {"options": "-csearch_path=public"}

engine = create_engine(DATABASE_URL, **engine_options)


def _get_table_columns(connection, table_name: str) -> set[str]:
    result = connection.execute(
        text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = :table_name
            """
        ),
        {"table_name": table_name},
    )
    return {row[0] for row in result}


def _constraint_exists(connection, constraint_name: str) -> bool:
    result = connection.execute(
        text(
            """
            SELECT 1
            FROM pg_constraint
            WHERE conname = :constraint_name
            LIMIT 1
            """
        ),
        {"constraint_name": constraint_name},
    )
    return result.first() is not None


def _migrate_legacy_user_schema():
    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as connection:
        columns = _get_table_columns(connection, "users")

        if not columns:
            return

        if "email" not in columns and "username" in columns:
            connection.execute(text("ALTER TABLE users RENAME COLUMN username TO email"))
            columns.remove("username")
            columns.add("email")

        if "email" not in columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(255)"))
            columns.add("email")

        connection.execute(
            text(
                """
                UPDATE users
                SET email = CONCAT('legacy-user-', id, '@local.invalid')
                WHERE email IS NULL OR email = ''
                """
            )
        )
        connection.execute(text("ALTER TABLE users ALTER COLUMN email SET NOT NULL"))

        connection.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN")
        )
        connection.execute(
            text("UPDATE users SET is_active = TRUE WHERE is_active IS NULL")
        )
        connection.execute(text("ALTER TABLE users ALTER COLUMN is_active SET NOT NULL"))

        connection.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS active_profile_id INTEGER")
        )
        connection.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at "
                "TIMESTAMP WITHOUT TIME ZONE"
            )
        )
        connection.execute(
            text(
                """
                UPDATE users
                SET updated_at = COALESCE(updated_at, created_at, NOW())
                WHERE updated_at IS NULL
                """
            )
        )
        connection.execute(text("ALTER TABLE users ALTER COLUMN updated_at SET NOT NULL"))

        connection.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at "
                "TIMESTAMP WITHOUT TIME ZONE"
            )
        )
        connection.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)")
        )

        if not _constraint_exists(connection, "users_active_profile_id_fkey"):
            connection.execute(
                text(
                    """
                    ALTER TABLE users
                    ADD CONSTRAINT users_active_profile_id_fkey
                    FOREIGN KEY (active_profile_id) REFERENCES profiles(id)
                    """
                )
            )


def _migrate_chat_history_schema():
    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as connection:
        columns = _get_table_columns(connection, "chat_history")

        if not columns:
            return

        connection.execute(
            text("ALTER TABLE chat_history ADD COLUMN IF NOT EXISTS title VARCHAR(80)")
        )
        connection.execute(
            text(
                "ALTER TABLE chat_history "
                "ADD COLUMN IF NOT EXISTS is_emergency BOOLEAN DEFAULT FALSE"
            )
        )
        connection.execute(
            text(
                "UPDATE chat_history "
                "SET is_emergency = FALSE "
                "WHERE is_emergency IS NULL"
            )
        )


def _ensure_postgres_schema():
    if engine.dialect.name != "postgresql":
        return

    with engine.begin() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
        connection.execute(text("SET search_path TO public"))


#creates all tables from db_models.py
def create_db_and_tables():
    _ensure_postgres_schema()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.exec(
            text(
                "ALTER TABLE profiles "
                "ADD COLUMN IF NOT EXISTS height_cm INTEGER"
            )
        )
        session.exec(
            text(
                "ALTER TABLE profiles "
                "ADD COLUMN IF NOT EXISTS weight_kg DOUBLE PRECISION"
            )
        )
        session.exec(
            text(
                "ALTER TABLE profiles "
                "ADD COLUMN IF NOT EXISTS ai_disclaimer_accepted_at TIMESTAMP "
            )
        )
        session.commit()
    _migrate_legacy_user_schema()
    _migrate_chat_history_schema()

#creates database-session
def get_db_session():
    return Session(engine)
