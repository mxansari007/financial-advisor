from fastapi import APIRouter, HTTPException, Query
from qdrant_client.models import Filter, ScoredPoint
from ..model import query_mistral
from ..services import qdrant_client, EXPENSES_COLLECTION  # ✅ Ensure Qdrant setup

router = APIRouter()

@router.get("/chat/")
def chat(user_id: int = Query(..., description="User ID for filtering expenses"), query: str = Query(..., description="User query for insights")):
    """
    Retrieve similar past expenses from Qdrant & provide financial insights using Mistral 7B.
    """
    try:
        # ✅ Search for similar expenses in Qdrant
        search_results = qdrant_client.search(
            collection_name=EXPENSES_COLLECTION,
            query_vector=[100.0],  # ✅ Ensure this is a single-dimension vector
            query_filter=Filter(must=[{"key": "user_id", "match": {"value": user_id}}]),
            limit=5
        )


        if not search_results:
            return {"message": "No similar past expenses found for analysis."}

        # ✅ Format retrieved expenses
        relevant_expenses = [
            f"{res.payload.get('category', 'Unknown')}: ₹{res.payload.get('amount', 0)} - {res.payload.get('description', 'No description')}"
            for res in search_results if isinstance(res, ScoredPoint)
        ]

        # ✅ Query Mistral 7B model for financial advice
        system_message = "You are a financial assistant helping users analyze their spending."
        user_message = f"Based on past expenses:\n{', '.join(relevant_expenses)}\n\n{query}"

        response = query_mistral(system_message, user_message)

        return {"message": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


def generate_embedding(text: str):
    """
    Generate a query vector. Replace this with real embedding logic.
    """
    return [100.0]  # ✅ Example: Use a single float value (same as stored amount)

