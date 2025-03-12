import os
from dotenv import load_dotenv

# Explicitly specify the .env file path
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

# Fetch environment variables
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./expenses.db")  # Default to SQLite for local testing

# Qdrant Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")  # Default to local Qdrant
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))    # Default Qdrant port

# Ensure required variables are loaded
if not MISTRAL_API_KEY:
    raise ValueError("❌ MISTRAL_API_KEY is not set in the .env file")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set in the .env file")
if not QDRANT_HOST:
    raise ValueError("❌ QDRANT_HOST is not set in the .env file")
if not QDRANT_PORT:
    raise ValueError("❌ QDRANT_PORT is not set in the .env file")
