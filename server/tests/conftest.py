import sys
from pathlib import Path

# Adds the server directory to Python's import path.
# This allows tests to import modules like inputs.draft_service.
sys.path.append(str(Path(__file__).resolve().parent.parent))