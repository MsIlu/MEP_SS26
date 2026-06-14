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

from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session
from auth.security import get_optional_current_account, get_session
from database.models import User
from profiles.service import get_profile_access_role
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database.connection import create_db_and_tables
from auth.router import router as auth_router
from profiles.router import router as profiles_router
from inputs.draft_router import router as draft_router, set_session_manager
from inputs.symptom_draft_extraction import SymptomDraftExtractionService
from chat.logic import ChatLogic
from extraction.core.extraction_engine import ExtractionEngine
from extraction.pipeline.extraction_pipeline import ExtractionPipeline
from extraction.pipeline.extractor_events import EventExtractor
from extraction.pipeline.extractor_symptom_confirmation import (
    SymptomConfirmationExtractor,
)
from extraction.core.llm_client import LLMClient
from sessions.manager import SessionManager
from logging_config import configure_logging
import config

app = FastAPI()
session_manager = SessionManager()
set_session_manager(session_manager)

app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(draft_router)

# CORS is permissive for local Flutter development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configure_logging()

# Shared infrastructure for chat handling and structured extraction.
llm_client = LLMClient(
            base_url=config.LITELLM_BASE_URL,
            api_key=config.LITELLM_API_KEY,
            model=config.SELECTED_MODEL,
            )

engine = ExtractionEngine(llm_client)
event_extractor = EventExtractor(engine)
symptom_confirmation_extractor = SymptomConfirmationExtractor(engine)
symptom_draft_service = SymptomDraftExtractionService(
    event_extractor,
    confirmation_extractor=symptom_confirmation_extractor,
)
pipeline = ExtractionPipeline(engine)
chat_logic = ChatLogic(
    session_manager,
    llm_client,
    symptom_draft_service=symptom_draft_service,
)

class ChatRequest(BaseModel):
    message: str
    session_id: str
    profile_id: int | None = None


class SessionRequest(BaseModel):
    profile_id: int | None = None


@app.post("/chatscreen")
def chat(
        req: ChatRequest,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    if req.profile_id is not None:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication is required for profile chat requests.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        get_profile_access_role(
            account_id=current_user.id,
            profile_id=req.profile_id,
            session=session,
        )

    if session_manager.session_exists(req.session_id):
        session_profile_id = session_manager.get_profile_id(req.session_id)

        if session_profile_id is None and req.profile_id is not None:
            session_manager.bind_profile(req.session_id, req.profile_id)
        elif session_profile_id is not None and req.profile_id != session_profile_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Chat session belongs to a different profile.",
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
def create_session(
    req: SessionRequest | None = None,
    current_user: User | None = Depends(get_optional_current_account),
    session: Session = Depends(get_session),
):
    """
    Create and return a new chat session id.
    """
    profile_id = req.profile_id if req is not None else None

    if profile_id is not None:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication is required for profile chat sessions.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        get_profile_access_role(
            account_id=current_user.id,
            profile_id=profile_id,
            session=session,
        )

    session_id = session_manager.create_session(profile_id=profile_id)
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
