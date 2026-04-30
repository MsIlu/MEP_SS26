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
from fastapi.middleware.cors import CORSMiddleware

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

# gewähltes Modell
selected_model = "llama3.2"

# Master Prompt, unsichtbar über jedem Chat.
master_prompt = "Du bist ein hilfreicher Assistent. Antworte kurz und verständlich auf Deutsch."

#  Verbindung zum Hochschul-Ollama-Server 
#  Das Gerät auf dem der Server läuft muss im Hochschulnetzwerk sein!!!
client = ollama.Client(
    host="http://141.19.141.150:11434"
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

        if not user_input:
            return {"response": "⚠️ Leere Eingabe."}

        # Session initialisieren
        if session_id not in sessions:
            sessions[session_id] = [
                {
                    "role": "system",
                    "content": master_prompt
                }
            ]

        messages = sessions[session_id]

        # User Message speichern
        messages.append({
            "role": "user",
            "content": user_input
        })

        # Ollama Anfrage
        response = client.chat(
            model=selected_model,
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
            model=selected_model,
            messages=[{"role": "user", "content": "antworte mit ok"}],
            options={"keep_alive": "2m"}
        )
        return {"status": "warmed up"}
    except Exception as e:
        return {"error": str(e)}