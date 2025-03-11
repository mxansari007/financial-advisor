from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal, Expense
from collections import defaultdict

router = APIRouter()

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API: Get Expenses Breakdown and Generate Chart Data
@router.get("/chart/{user_id}")
def generate_chart(user_id: int, db: Session = Depends(get_db)):
    expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
    summary = defaultdict(float)

    for expense in expenses:
        summary[expense.category] += expense.amount

    # Return the summary for the chart (or more complex data)
    chart_data = [{"category": k, "amount": v} for k, v in summary.items()]
    return {"chart_data": chart_data}
