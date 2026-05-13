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
from openai import OpenAI
import uuid
from fastapi.middleware.cors import CORSMiddleware
import config
from medical_rules import detect_medical_red_flags
from topic_filter import (
    is_health_related,
    is_smalltalk_or_boredom,
    OUT_OF_SCOPE_RESPONSE,
    SMALLTALK_GOODBYE_RESPONSE,
)

app = FastAPI()

# CORS (für Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # für Entwicklung ok
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Speicher
sessions = {}

def build_llm_messages(messages: list[dict]) -> list[dict]:
    """
  Baut einen kleineren Kontext für das LLM:
  - Systemprompt bleibt immer enthalten
  - nur die letzten Chatnachrichten werden an das Modell geschickt
  - der vollständige Verlauf bleibt trotzdem in sessions gespeichert
  """
    system_messages = [m for m in messages if m.get("role") == "system"]
    chat_messages = [m for m in messages if m.get("role") != "system"]

    recent_chat_messages = chat_messages[-config.MAX_HISTORY_MESSAGES:]

    return system_messages + recent_chat_messages

# Verbindung zum LiteLLM-Proxy der Hochschule.
# Der Proxy stellt eine OpenAI-kompatible API bereit.
# Das eigene Gerät muss sich im Hochschulnetzwerk befinden.
client = OpenAI(
    base_url=config.LITELLM_BASE_URL,
    api_key=config.LITELLM_API_KEY,
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

# Endpunkt für Chatnachrichten
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        user_input = req.message.strip()
        session_id = req.session_id

        print(f"[{session_id}] User: {user_input}")
        
        if session_id not in sessions:
            return {"response": "Fehler: Ungültige Session-ID"}
        
        if not user_input:
            return {"response": "Fehler: Leere Eingabe."}

        messages = sessions[session_id]
        # Smalltalk / Langeweile freundlich beenden
        if is_smalltalk_or_boredom(user_input):
            return {"response": SMALLTALK_GOODBYE_RESPONSE}

        # Nur gesundheitsbezogene Anliegen zulassen
        if not is_health_related(user_input, messages):
            return {"response": OUT_OF_SCOPE_RESPONSE}

        # User Message speichern
        messages.append({
            "role": "user",
            "content": user_input
        })

        # detect_medical_red_flags kommt aus medical_rules.py
        result = detect_medical_red_flags(user_input)

        # Falls result leer ist (z.B. None), 
        # wird der Block nicht ausgeführt 
        if result:
            messages.append({
                "role":"assistant",
                "content":result
            })
            return {"response": result}

        # Nur reduzierten Verlauf an das LLM schicken
        llm_messages = build_llm_messages(messages)

        # Chat-Anfrage an LiteLLM über OpenAI-kompatible API
        response = client.chat.completions.create(
            model=config.SELECTED_MODEL,
            messages=llm_messages,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
        )

        # Debug Konsolenausgabe
        print(f"[{session_id}] LiteLLM response received.")

        reply = response.choices[0].message.content

        if reply:
            reply = reply.strip()
        else:
            reply = "⚠️ Keine Antwort vom Modell."

        # Assistant Message speichern
        messages.append({
            "role": "assistant",
            "content": reply
        })

        print(f"[{session_id}] Verlauf Länge: {len(messages)}")

        return {"response": reply}

    except Exception as e:
        print("Error:", e)
        return {"response": f"❌ Fehler: {str(e)}"}



# Endpunkt zur Abfrage der verfügbaren Modelle
@app.get("/models")
def get_models():
    try:
        models = client.models.list()

        model_names = [m.id for m in models.data]

        print("Available models:", model_names)

        return {"models": model_names}

    except Exception as e:
        print("MODELS ERROR:", repr(e))
        return {"error": str(e)}
    
    
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
        return {"status": "warmed up"}
    except Exception as e:
        print("WARMUP ERROR:", repr(e))
        return {"error": str(e)}
    
# Endpunkt zur Vergabe von Session IDs
@app.post("/session")
def create_session():
    session_id = str(uuid.uuid4())

    # Session initialisieren
    sessions[session_id] = [
        {
            "role": "system",
            "content": config.MASTER_PROMPT
        }
    ]

    #Debug/Log
    print("Created session: ", session_id)

    return {"session_id": session_id}