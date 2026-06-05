"""
Konfigurationsmodul für das Projekt MEP_SS26.
Lädt Umgebungsvariablen aus der .env-Datei und stellt globale Parameter
sowie den Master-Prompt für das LLM bereit.
"""


import os
import logging 
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Projekt-Hauptordner bestimmen:
# config.py liegt in /server, deshalb gehen wir eine Ebene hoch zu MEP_SS26a
BASE_DIR = Path(__file__).resolve().parent.parent
SERVER_DIR = Path(__file__).resolve().parent

# .env aus dem Projekt-Hauptordner laden
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
    logger.info(f"Umgebungsvariablen erfolgreich aus {ENV_PATH} geladen.")
else:
    logger.warning(f"Keine .env-Datei unter {ENV_PATH} gefunden! Nutze Fallback-Werte.")

# API und Server-Schnittstellen
LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://localhost:4000").rstrip("/")
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY", "")
SELECTED_MODEL = os.getenv("LITELLM_MODEL", "medgemma:27b")

# LLM-Konfiguration
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "6"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "220"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))

# Dynamisches Laden des Master-Prompts

def _load_master_prompt() -> str:
    """Lädt den Prompt-Text dynamisch aus einer externen Textdatei."""
    prompt_path = SERVER_DIR / "master_prompt.txt"
    try:
        with open(prompt_path, "r", encoding="utf-8") as file:
            logger.info("Master-Prompt erfolgreich aus externer Textdatei geladen.")
            return file.read().strip()
    except FileNotFoundError:
        logger.error(f"Kritischer Fehler: {prompt_path} nicht gefunden!")
        return "Du bist ein medizinischer KI-Assistent. (Fallback-Prompt)"

# Globale Variable für main.py bereitstellen
MASTER_PROMPT = _load_master_prompt()