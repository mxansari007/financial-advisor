from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from .config import DATABASE_URL
from datetime import datetime
import chromadb
from sentence_transformers import SentenceTransformer


# Create Database Engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Initialize ChromaDB with persistent storage
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("financial_chatbot")



# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # Ensuring unique names
    expenses = relationship("Expense", back_populates="user")  # Establish relationship
    ideal_scenario = relationship("IdealScenario", back_populates="user", uselist=False)  # Relationship to Ideal Scenario

# Expense Model
class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)  # Foreign key added
    category = Column(String, index=True)
    amount = Column(Float)
    description = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="expenses")  # Relationship with User



# Ideal Scenario Model (Store ideal daily spending limits)
class IdealScenario(Base):
    __tablename__ = "ideal_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_limit = Column(Float, default=30.0)  # Default ideal value for food
    transport_limit = Column(Float, default=20.0)  # Default ideal value for transport
    entertainment_limit = Column(Float, default=15.0)  # Default ideal value for entertainment
    user = relationship("User", back_populates="ideal_scenario")









# Initialize Database
def init_db():
    Base.metadata.create_all(bind=engine)



# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text):
    """Convert text to an embedding vector"""
    return embedding_model.encode(text).tolist()