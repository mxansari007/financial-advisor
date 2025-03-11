from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal, Expense, IdealScenario, User
from datetime import datetime
from database import collection, generate_embedding
from model import model, tokenizer



router = APIRouter()

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API: Get Financial Advice (Today's Expenses vs Ideal Scenario)
@router.post("/generate-response/")
def generate_response(user_input: str):
    inputs = tokenizer(user_input, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=150)
    return {"response": tokenizer.decode(outputs[0], skip_special_tokens=True)}