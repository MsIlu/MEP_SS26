# Backend server using FastAPI and Uvicorn.
#
# Notes:
# - Chat handling is currently session-based.
# - Authentication and account data are persisted in PostgreSQL.
# - Medical profiles are stored separately from login accounts.
# - Chat history is still managed through the session manager unless explicitly persisted elsewhere.
#
# Requirements:
# <bash> pip install -r requirements.txt
#
# Run:
# <bash> uvicorn main:app --reload
# or
# <bash> python -m uvicorn main:app --reload

from fastapi import FastAPI, Depends
from sqlmodel import Session
from auth.security import get_current_account, get_session
from database.models import User
from profiles.service import get_profile_access_role
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database.connection import create_db_and_tables
from auth.router import router as auth_router
from profiles.router import router as profiles_router
from medications.router import router as medications_router
from chat.logic import ChatLogic
from extraction.core.extraction_engine import ExtractionEngine
from extraction.pipeline.extraction_pipeline import ExtractionPipeline
from extraction.core.llm_client import LLMClient
from sessions.manager import SessionManager
from logging_config import configure_logging
import config

app = FastAPI()

app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(medications_router)

# CORS (for Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # für Entwicklung ok
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configure_logging()

# Init
llm_client = LLMClient(
            base_url=config.LITELLM_BASE_URL,
            api_key=config.LITELLM_API_KEY,
            model=config.SELECTED_MODEL,
            )


session_manager = SessionManager()

chat_logic = ChatLogic(session_manager, llm_client)

engine = ExtractionEngine(llm_client)
pipeline = ExtractionPipeline(engine)

# Model
class ChatRequest(BaseModel):
    """
    Request body for sending a chat message within a selected medical profile.
    """

    message: str
    session_id: str
    profile_id: int

# Routes
@app.post("/chatscreen")
def chat(
        req: ChatRequest,
        current_user: User = Depends(get_current_account),
        session: Session = Depends(get_session),
):
    """
    Handle incoming chat messages for a selected medical profile.

    The authenticated account must have access to the requested profile.
    """
    get_profile_access_role(
        account_id=current_user.id,
        profile_id=req.profile_id,
        session=session,
    )

    return chat_logic.handle_message(req.session_id, req.message)

@app.post("/warmup")
def warmup():
    """
    Warm up the configured language model by sending a minimal test message.
    """
    try:
        llm_client.chat([{"role": "user", "content": "ok"}])
        return {"status": "warmed up"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/session")
def create_session():
    """
    Create and return a new chat session id.
    """
    session_id = session_manager.create_session()
    print("Created session:", session_id)
    return {"session_id": session_id}

@app.post("/pipetest")
def pipetest():
    """
    Run a hardcoded test input through the extraction pipeline.

    This endpoint is intended for development and debugging only.
    """
    input = (
        "Ich habe kopfschmerzen und meine nase läuft seit gestern, seit heute halsschmerzen aber noch kein husten. könnte das eine grippe sein?"
    )

    result = pipeline.run(input)

    return result.model_dump()

# Editor: Ilu
# Modified as part of the authentication and profile management implementation.
# Runs automatically when the FastAPI server starts.
# Creates all database tables if they do not already exist.
@app.on_event("startup")
def on_startup():
    """
    Initialize database tables on application startup.
    """
    create_db_and_tables()