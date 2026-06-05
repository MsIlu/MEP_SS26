"""
Backend Server für das Projekt MEP_SS26.
Dieses basiert auf FastAPI und nutzt eine PostgreSQL-Datenbank via Docker.
Die Kommunikation mit dem hochschulinternen KI-Modell (medgemma:27b) erfolgt über einen 
LiteLLM-Proxy, der über die standardisierte OpenAI-Schnittstelle angesprochen wird.
"""

import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

import config
from red_flags.detector import detect_medical_red_flags
from topic_filter import (
    is_health_related,
    is_smalltalk_or_boredom,
    OUT_OF_SCOPE_RESPONSE,
    SMALLTALK_GOODBYE_RESPONSE,
)
from database.connection import create_db_and_tables

# Zentrales Logging konfigurieren (besser als rohe print-Statements)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Standardisierte medizinische Notfallwarnung auslagern
EMERGENCY_WARNING_TEXT = (
    "Wichtiger Hinweis:\n"
    "Ihre Angaben können auf eine akute Notfallsituation hinweisen.\n\n"
    "Nächster Schritt:\n"
    "Bitte wählen Sie sofort den Notruf 112 oder holen Sie umgehend medizinische Hilfe.\n\n"
    "Hinweis:\n"
    "Diese Einschätzung ersetzt keine ärztliche Untersuchung und stellt keine Diagnose dar."
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modernes Lifecycle-Management für den FastAPI-Startup-Prozess."""
    logger.info("Starte Backend-Server und initialisiere Datenbanktabellen...")
    try:
        create_db_and_tables()
        logger.info("Datenbanktabellen erfolgreich abgeglichen/erstellt.")
    except Exception as e:
        logger.error(f"Fehler bei der Datenbank-Initialisierung: {e}")
    yield
    logger.info("Backend-Server wird heruntergefahren...")


# FastAPI-Instanz mit modernem Lifespan-Handler initialisieren
app = FastAPI(
    title="MEP_SS26 Backend",
    description="Medizininformatik Projekt-Backend mit KI-Anbindung",
    version="1.0.0",
    lifespan=lifespan
)

# CORS (für Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # für Entwicklung ok
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory Session Speicher (Wird später durch DB-Modell ersetzt)
sessions = {}

# OpenAI-kompatibler LiteLLM-Client
client = OpenAI(
    base_url=config.LITELLM_BASE_URL,
    api_key=config.LITELLM_API_KEY,
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

def build_llm_messages(messages: list[dict]) -> list[dict]:
    """Baut einen reduzierten Kontext für das LLM unter Beibehaltung des System-Prompts."""
    system_messages = [m for m in messages if m.get("role") == "system"]
    chat_messages = [m for m in messages if m.get("role") != "system"]
    recent_chat_messages = chat_messages[-config.MAX_HISTORY_MESSAGES:]
    return system_messages + recent_chat_messages

# Endpunkt für Chatnachrichten
@app.post("/chatscreen")
def chat(req: ChatRequest):
    try:
        user_input = req.message.strip()
        session_id = req.session_id

        logger.info(f"[{session_id}] Eingehende Nachricht: '{user_input}'")
        
        if session_id not in sessions:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ungültige Session-ID")
        
        if not user_input:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Leere Eingabe.")

        messages = sessions[session_id]

        # 1. Guard-Rails: Smalltalk abfangen 
        if is_smalltalk_or_boredom(user_input):
            return {"response": SMALLTALK_GOODBYE_RESPONSE}

        # 2. Guard-Rails: Prüfung der medizinischen Relevanz
        if not is_health_related(user_input, messages):
            return {"response": OUT_OF_SCOPE_RESPONSE}

        # User-Eingabe im Verlauf sichern 
        messages.append({"role": "user", "content": user_input})

        # 3. Sicherheitsprüfung: Red-Flags (Notfälle) erkennen
        red_flag_result = detect_medical_red_flags(user_input)

        if red_flag_result.get("red_flag") and red_flag_result.get("block_ai_response", False):
            logger.warning(f"[{session_id}] Medizinischer Notfall erkannt: {red_flag_result}")

            messages.append({"role": "assistant", "content": EMERGENCY_WARNING_TEXT})

            return {
                "response": EMERGENCY_WARNING_TEXT,
                "red_flag": True,
                "severity": red_flag_result.get("severity"),
                "action": red_flag_result.get("action"),
                "rule_id": red_flag_result.get("rule_id"),
                "rule_name": red_flag_result.get("rule_name"),
                "category": red_flag_result.get("category"),
                "message_key": red_flag_result.get("message_key"),
                "matched_keywords": red_flag_result.get("matched_keywords", [])
            }

        # 4. KI-Verarbeitung (Nur wenn kein Notfall vorliegt)
        llm_messages = build_llm_messages(messages)

        # Chat-Anfrage an LiteLLM Proxy
        response = client.chat.completions.create(
            model=config.SELECTED_MODEL,
            messages=llm_messages,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
        )

        # Debug Konsolenausgabe
        logger.info(f"[{session_id}] Antwort von LiteLLM erfolgreich empfangen.")
        reply = response.choices[0].message.content

        reply = reply.strip() if reply else "⚠️ Keine Antwort vom Modell."

        # KI-Assistenten Antwort im Verlauf sichern 
        messages.append({"role": "assistant","content": reply})
        logger.info(f"[{session_id}] Aktuelle Verlaufslänge: {len(messages)}")

        return {"response": reply}

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Interner Serverfehler in /chatscreen: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Endpunkt zur Abfrage der verfügbaren Modelle
@app.get("/models")
def get_models():
    try:
        models = client.models.list()
        model_names = [m.id for m in models.data]
        logger.info(f"Verfügbare KI-Modelle abgerufen: {model_names}")
        return {"models": model_names}
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Modelle: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    
# Endpunkt startet Sprachmodell serverseitig für schnellere Antworten
@app.post("/warmup")
def warmup():
    try:
        client.chat.completions.create(
            model=config.SELECTED_MODEL,
            messages=[{"role": "user", "content": "antworte mit ok"}],
            temperature=config.LLM_TEMPERATURE,
            max_tokens=10,
        )
        logger.info("Modell-Warmup erfolgreich durchgeführt.")
        return {"status": "warmed up"}
    except Exception as e:
        logger.error(f"Fehler beim Modell-Warmup: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
# Endpunkt zur Vergabe von Session IDs
@app.post("/session")
def create_session():
    try:
        session_id = str(uuid.uuid4())
        sessions[session_id] = [
            {
                "role": "system",
                "content": config.MASTER_PROMPT
            }
        ]
        logger.info(f"Neue Session erfolgreich generiert: {session_id}")
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Fehler bei Session-Erstellung: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

