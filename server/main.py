# Backend Server mit fastapi x uvicorn
# 
# HINWEISE: 
#
# - Session basiert, unterschiedliche Nutzer sollten eigenen Chatkontext haben
# - Chatverläufe werden bei Server Neustart gelöscht, noch keine DB vorhanden
#
# Benötigt:
# <bash> $ pip install fastapi uvicorn openai python-dotenv
#
# Zum Ausführen:
# <bash> $ uvicorn main:app --reload
# oder
# <bash> $ python -m uvicorn main:app --reload

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
#from database.connection import create_db_and_tables
from chat.logic import ChatLogic
from extraction.core.extraction_engine import ExtractionEngine
from extraction.pipeline.extraction_pipeline import ExtractionPipeline
from extraction.core.llm_client import LLMClient
from sessions.manager import SessionManager
from logging_config import configure_logging
import config

app = FastAPI()

# CORS (für Flutter)
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
    message: str
    session_id: str

# Routes

"""Endpunkt für chatnachrichten"""
@app.post("/chatscreen")
def chat(req: ChatRequest):
    return chat_logic.handle_message(req.session_id, req.message)

"""Endpunkt startet Sprachmodell serverseitig für schnellere Antworten"""
# Bug: gibt aktuell immer 200 ok zurück
@app.post("/warmup")
def warmup():
    try:
        llm_client.chat([{"role": "user", "content": "ok"}])
        return {"status": "warmed up"}
    except Exception as e:
        return {"error": str(e)}
    
"""Endpunkt zur Vergabe von Session IDs"""
@app.post("/session")
def create_session():
    session_id = session_manager.create_session()
    print("Created session:", session_id)
    return {"session_id": session_id}

"""Endpunkt für pipeline entwicklung"""
@app.post("/pipetest")
def pipetest():
    input = (
        "Ich habe kopfschmerzen und meine nase läuft seit gestern, seit heute halsschmerzen aber noch kein husten. könnte das eine grippe sein?"
        #"Ich habe grippe und einen gebrochenen zeh"
        #"Mein hund hat durchfall und ich habe seit gestern starke kopfschmerzen"
        #"Wie geht es dir?"
        #"Ich brauche dringend einen arzttermin "
    )

    result = pipeline.run(input)

    return result.model_dump()

# Editor: Ilu
# Runs automatically when the FastAPI server starts.
# Creates all database tables if they do not already exist.
#@app.on_event("startup")
#def on_startup():
#    create_db_and_tables()