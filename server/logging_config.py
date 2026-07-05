# Author @Freddy
"""Basic logging setup for the server process.

Note: careena4/server_log/logging.py configures its own (file-based) logging
for the chat pipeline; this module only covers the plain console output.
"""

import logging


def configure_logging():
    """Configure root console logging and silence noisy HTTP client loggers."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )

    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
