# Backend Server mit fastapi x uvicorn
# 
# HINWEISE: 
#
# - Session basiert, unterschiedliche Nutzer sollten eigenen Chatkontext haben
# - Chatverläufe werden bei Server Neustart gelöscht, noch keine DB vorhanden
#
# Benötigt:
# <bash> $ pip install fastapi uvicorn ollama
#
# Zum Ausführen:
# <bash> $ uvicorn main:app --reload
# oder
# <bash> $ python -m uvicorn main:app --reload

from fastapi import FastAPI
from pydantic import BaseModel
import ollama
import uuid
from fastapi.middleware.cors import CORSMiddleware
import config
from medical_rules import detect_medical_red_flags
from fastapi.responses import StreamingResponse
from pdf_exporter import generate_chat_pdf

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

#  Verbindung zum Hochschul-Ollama-Server 
#  Das Gerät auf dem der Server läuft muss im Hochschulnetzwerk sein!!!
client = ollama.Client(
    host=config.OLLAMA_HOST
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

        # Ollama Anfrage
        response = client.chat(
            model=config.SELECTED_MODEL,
            messages=messages,
            options={"keep_alive": "2m"}
        )

        # Debug Konsolenausgabe
        print(f"[{session_id}] Ollama Server response:")
        print("    Model: ", response.model, "| Total Dur (s):", response.total_duration / 1e9, "| Load Dur (s):", response.load_duration / 1e9, "| Eval Dur (s):", response.eval_duration / 1e9, "| Tokens (prompt):", response.prompt_eval_count, "| Tokens (generated):", response.eval_count)

        reply = response["message"]["content"].strip()

        if not reply:
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
        models = client.list()
        model_names = [m.model for m in models.models]

        print("Available models:", model_names)

        return {"models": model_names}

    except Exception as e:
        return {"error": str(e)}
    
    
# Endpunkt startet Sprachmodell serverseitig für schnellere Antworten
@app.post("/warmup")
def warmup():
    try:
        client.chat(
            model=config.SELECTED_MODEL,
            messages=[{"role": "user", "content": "antworte mit ok"}],
            options={"keep_alive": "2m"}
        )
        return {"status": "warmed up"}
    except Exception as e:
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
        },
        {
            "role": "assistant",
            "content": config.WELCOME_MESSAGE
        }
    ]

    #Debug/Log
    print("Created session: ", session_id)

    return {"session_id": session_id}

# Define GET endpoint with dynamic session_id
@app.get("/export/{session_id}")
def export_pdf(session_id: str):

    # Check if the session exists in memory
    if session_id not in sessions:
        return {"response": "Fehler: Ungültige Session-ID"}
    
    # Generate PDF from stored chat messages
    pdf_buffer = generate_chat_pdf(sessions[session_id])

    # Return PDF as a streaming response (no file saved on a disk)
    return StreamingResponse(

        # In-memory PDF file
        pdf_buffer,
        # Tell browser it's a PDF
        media_type="application/pdf",
        headers={
            # Force browser to download the file instead of displaying it
            "Content-Disposition": "attachment; filename=chat.pdf"
        }
    )