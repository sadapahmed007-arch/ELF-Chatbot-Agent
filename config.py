"""Application configuration loaded from environment variables."""
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "chatbot_db"),
}

FLASK_CONFIG = {
    "host": os.getenv("FLASK_HOST", "127.0.0.1"),
    "port": int(os.getenv("FLASK_PORT", "5000")),
    "debug": os.getenv("FLASK_DEBUG", "false").lower() == "true",
}

API_KEYS = {
    "openweathermap": os.getenv("OPENWEATHERMAP_API_KEY", ""),
    "newsapi": os.getenv("NEWSAPI_KEY", ""),
}

CHATBOT_NAME = os.getenv("CHATBOT_NAME", "ELF")
DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "Dhaka")

NLP_CONFIG = {
    "min_confidence": 0.5,
    "max_entities": 10,
}
