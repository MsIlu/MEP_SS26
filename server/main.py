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
from chat_history.router import router as chat_history_router
from profiles.router import router as profiles_router
from medications.router import router as medications_router
from symptoms.router import router as symptoms_router
from logging_config import configure_logging

from uuid import uuid4 #for turn_id

from careena4.bootstrap import build_default_services #for Careena4 runtime: LLM, TurnEngine, SessionStore
from careena4.models.turn import TurnInput, TurnResult #for User message in Careena4 and Response-Helpfunction
from careena4.models.input import (
    CancelDraftResponse,
    SymptomDraftResponse,
    SymptomDraftUpdateRequest,
)

app = FastAPI()

careena4_services = build_default_services(llm_mode="env") #build careena4
careena4_turn_engine = careena4_services.turn_engine #replace for chat_logic.handle.message(...)
careena4_session_store = careena4_services.session_store #replace for SessionManager
careena4_session_profiles: dict[str, int | None] = {} #extra for profile_id

app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(medications_router)
app.include_router(chat_history_router)
app.include_router(symptoms_router)

# CORS is permissive for local Flutter development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configure_logging()

class ChatRequest(BaseModel):
    message: str
    session_id: str
    profile_id: int | None = None


class SessionRequest(BaseModel):
    profile_id: int | None = None


def require_careena4_session(session_id: str):
    careena4_session = careena4_session_store.get(session_id)

    if careena4_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found.",
        )

    return careena4_session


def require_careena4_session_access(
        session_id: str,
        current_user: User | None,
        db_session: Session,
):
    careena4_session = require_careena4_session(session_id)
    profile_id = careena4_session_profiles.get(session_id)

    if profile_id is None:
        return careena4_session

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required for profile draft requests.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    get_profile_access_role(
        account_id=current_user.id,
        profile_id=profile_id,
        session=db_session,
    )

    return careena4_session

#Helper: convert Careena4 TurnResult into the Flutter chat response JSON.
def build_careena4_chat_response(result: TurnResult) -> dict:
    active_question = result.conversation_state.active_question
    pending_followup = None

    if active_question is not None and active_question.kind in {
        "followup",
        "subject_clarification",
    }:
        pending_followup = {
            "question_id": active_question.question_id,
            "kind": active_question.kind,
            "question_intent": active_question.question_intent,
            "target_observation_id": active_question.target_observation_id,
            "target_followup_id": active_question.target_followup_id,
            "prompt_text": active_question.prompt_text,
            "blocking": active_question.blocking,
        }

    recommendation_ready = result.response_mode in {
        "guide_next_step",
        "recommend",
    }

    return {
        "response": result.response_text,
        "response_mode": result.response_mode,
        "red_flag": result.response_mode == "emergency",
        "trace_notes": list(result.trace_notes),
        "pending_followup": pending_followup,
        "recommendation_requested": result.conversation_state.recommendation_requested,
        "recommendation_ready": recommendation_ready,
        "recommendation_result": (
            result.recommendation_result.model_dump()
            if result.recommendation_result is not None
            else None
        ),
    }


#1. checks if Careena4-Session exist
#2. validate empty input
#3. save profile_id
#4. build TurnInput
#5. Careena4 processes TurnInput
#6. write new state in session
#7. build API-Response for Flutter
@app.post("/chatscreen")
def chat(
        req: ChatRequest,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    careena4_session = careena4_session_store.get(req.session_id)

    if careena4_session is None:
        return {"response": "Fehler: Ungueltige Session-ID", "red_flag": False}

    if not req.message.strip():
        return {"response": "Fehler: Leere Eingabe.", "red_flag": False}

    session_profile_id = careena4_session_profiles.get(req.session_id)

    if session_profile_id is None and req.profile_id is not None:
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

        careena4_session_profiles[req.session_id] = req.profile_id
        session_profile_id = req.profile_id

    elif session_profile_id is not None:
        if req.profile_id is not None and req.profile_id != session_profile_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Chat session belongs to a different profile.",
            )

        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication is required for profile chat requests.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        get_profile_access_role(
            account_id=current_user.id,
            profile_id=session_profile_id,
            session=session,
        )

    turn_id = str(uuid4())

    turn_result = careena4_turn_engine.run_turn(
        TurnInput.from_persisted_state(
            message=req.message,
            session_id=req.session_id,
            turn_id=turn_id,
            conversation_messages=careena4_session.messages,
            persisted_case_topic=careena4_session.case_topic,
            persisted_medical_case=careena4_session.medical_case,
            persisted_conversation_state=careena4_session.conversation_state,
            persisted_recommendation_state=careena4_session.recommendation_state,
            persisted_symptom_input_draft=careena4_session.symptom_input_draft,
        )
    )

    careena4_session.case_topic = turn_result.case_topic
    careena4_session.medical_case = turn_result.medical_case
    careena4_session.conversation_state = turn_result.conversation_state
    careena4_session.recommendation_state = turn_result.recommendation_state
    careena4_session.last_turn_understanding = turn_result.current_turn_understanding

    if turn_result.symptom_input_draft is not None:
        careena4_session.symptom_input_draft = turn_result.symptom_input_draft

    careena4_session.messages.append({"role": "user", "content": req.message})

    response = build_careena4_chat_response(turn_result)

    careena4_session.messages.append(
        {"role": "assistant", "content": response["response"]}
    )

    return response

@app.post("/warmup")
def warmup():
    """
    Lightweight readiness endpoint for the chat backend.

    Kept for frontend compatibility; Careena4 manages LLM calls internally.
    """
    return {"status": "ok"}


@app.get("/input-drafts/{session_id}", response_model=SymptomDraftResponse)
def get_input_draft(
        session_id: str,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    """
    Return the current editable symptom draft for a Careena4 session.
    """
    careena4_session = require_careena4_session_access(
        session_id=session_id,
        current_user=current_user,
        db_session=session,
    )

    return SymptomDraftResponse(
        session_id=session_id,
        symptoms=careena4_session.symptom_input_draft.symptom_labels(),
        chips=careena4_session.symptom_input_draft.chips,
    )


@app.patch("/input-drafts/{session_id}", response_model=SymptomDraftResponse)
def update_input_draft(
        session_id: str,
        request: SymptomDraftUpdateRequest,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    """
    Replace the editable symptom draft after user edits in the frontend.
    """
    careena4_session = require_careena4_session_access(
        session_id=session_id,
        current_user=current_user,
        db_session=session,
    )

    if request.chips is not None:
        careena4_session.symptom_input_draft.replace_from_chips(request.chips)
    else:
        careena4_session.symptom_input_draft.replace_from_labels(request.symptoms)

    return SymptomDraftResponse(
        session_id=session_id,
        symptoms=careena4_session.symptom_input_draft.symptom_labels(),
        chips=careena4_session.symptom_input_draft.chips,
    )

@app.delete("/input-drafts/{session_id}", response_model=CancelDraftResponse)
def cancel_input_draft(
        session_id: str,
        current_user: User | None = Depends(get_optional_current_account),
        session: Session = Depends(get_session),
):
    """
    Clear the editable symptom draft for a Careena4 session.
    """
    careena4_session = require_careena4_session_access(
        session_id=session_id,
        current_user=current_user,
        db_session=session,
    )

    careena4_session.symptom_input_draft.replace_from_labels([])

    return CancelDraftResponse(
        message="Draft cancelled successfully.",
        session_id=session_id,
    )


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

    session_id = careena4_session_store.create_session()
    careena4_session_profiles[session_id] = profile_id

    print("Created Careena4 session:", session_id)
    return {"session_id": session_id}

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
