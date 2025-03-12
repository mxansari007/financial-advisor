from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal, Expense
from ..services import store_expense, qdrant_client, EXPENSES_COLLECTION
from qdrant_client.models import Filter, ScoredPoint
import logging


logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/add-expense/")
def add_expense(user_id: int, category: str, amount: float, description: str, db: Session = Depends(get_db)):
    """Add an expense & store it in both SQL and Qdrant."""
    try:
        # ✅ Save to SQL Database
        expense = Expense(user_id=user_id, category=category, amount=amount, description=description)
        db.add(expense)
        db.commit()
        db.refresh(expense)  # ✅ Get auto-generated ID

        # ✅ Store in Qdrant using the SQL-assigned ID
        qdrant_success = store_expense(expense.id, user_id, category, amount, description)

        if not qdrant_success:
            logger.error(f"⚠️ Expense {expense.id} saved in SQL but failed in Qdrant!")

        return {"message": "✅ Expense added successfully", "expense_id": expense.id}

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to add expense: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"❌ Failed to add expense: {str(e)}")
    

@router.get("/get-expenses/")
def get_expenses(user_id: int = Query(None, description="Filter expenses by user ID")):
    """Retrieve all expenses from Qdrant, optionally filtered by user ID."""
    try:
        query_filter = None
        if user_id is not None:
            query_filter = Filter(must=[{"key": "user_id", "match": {"value": user_id}}])  # ✅ user_id should be an int

        # Qdrant scroll request
        scroll_result = qdrant_client.scroll(
            collection_name=EXPENSES_COLLECTION,
            limit=20,
            scroll_filter=query_filter,  # ✅ Ensure the filter is applied correctly
        )

        points, _ = scroll_result  # Extract points

        if not points:
            return {"message": f"No expenses found for user_id: {user_id}" if user_id else "No expenses found."}

        # ✅ Ensure we process all stored expenses correctly
        expense_list = [
            {
                "id": point.id,
                "category": point.payload.get("category", "Unknown"),
                "amount": point.payload.get("amount", 0),  # ✅ Fetch amount from payload
                "description": point.payload.get("description", "No description"),
                "user_id": point.payload.get("user_id", "Unknown"),
            }
            for point in points
        ]

        return {"expenses": expense_list}

    except Exception as e:
        return {"error": f"Failed to fetch expenses: {str(e)}"}