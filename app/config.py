import os
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./expenses.db")  # Use SQLite for local testing