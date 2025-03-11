from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal, Expense
from pydantic import BaseModel
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ExpenseCreate(BaseModel):
    user_id: int
    category: str
    amount: float
    description: str

@router.post("/expenses")
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    new_expense = Expense(**expense.dict())
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@router.get("/expenses/{user_id}", response_model=List[ExpenseCreate])
def get_expenses(user_id: int, db: Session = Depends(get_db)):
    return db.query(Expense).filter(Expense.user_id == user_id).all()
