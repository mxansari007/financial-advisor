import logging
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, Filter
from .config import QDRANT_HOST, QDRANT_PORT
import uuid
import logging


# Configure Logging
logger = logging.getLogger(__name__)

# Initialize Qdrant Client
qdrant_client = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)

# Collection Names
EXPENSES_COLLECTION = "expenses"
USER_COLLECTION = "users"

def ensure_collection_exists():
    """Ensure the expenses collection exists in Qdrant."""
    try:
        existing_collections = qdrant_client.get_collections().collections
        collection_names = [col.name for col in existing_collections]

        if EXPENSES_COLLECTION not in collection_names:
            qdrant_client.create_collection(
                collection_name=EXPENSES_COLLECTION,
                vectors_config=VectorParams(size=1, distance=Distance.COSINE)  # 1D vector (amount)
            )
            logger.info(f"✅ Collection '{EXPENSES_COLLECTION}' created.")
        else:
            logger.info(f"🔹 Collection '{EXPENSES_COLLECTION}' already exists.")

    except Exception as e:
        logger.error(f"❌ Failed to create collection '{EXPENSES_COLLECTION}': {e}", exc_info=True)




def store_expense(expense_id: int, user_id: int, category: str, amount: float, description: str) -> bool:
    """Store an expense in Qdrant."""
    try:
        qdrant_client.upsert(
            collection_name=EXPENSES_COLLECTION,
            points=[
                PointStruct(
                    id=expense_id,  
                    vector=[amount],  # ✅ Ensure a single-dimension vector
                    payload={
                        "user_id": user_id,
                        "category": category,
                        "amount": amount,
                        "description": description,
                    },
                )
            ]
        )
        logger.info(f"✅ Expense {expense_id} stored in Qdrant for user {user_id}.")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to store expense {expense_id} in Qdrant: {e}", exc_info=True)
        return False



def store_chat_message(user_id: int, role: str, message: str):
    """Store chat messages in Qdrant for maintaining context."""
    try:
        message_id = str(uuid.uuid4())  # Unique ID for each message
        
        qdrant_client.upsert(
            collection_name="chat_history",
            points=[
                PointStruct(
                    id=message_id,
                    vector=[1.0] * 300,  # ✅ Dummy vector (replace with embedding)
                    payload={
                        "user_id": user_id,
                        "role": role,  # "user" or "assistant"
                        "message": message
                    },
                )
            ]
        )
        print(f"✅ Stored message for user {user_id}: {message}")
    
    except Exception as e:
        print(f"❌ Failed to store message: {e}")


def get_recent_chat_history(user_id: int, limit: int = 5):
    """Retrieve the latest chat history for a user from Qdrant."""
    try:
        search_results = qdrant_client.scroll(
            collection_name="chat_history",
            limit=limit,
            scroll_filter=Filter(must=[{"key": "user_id", "match": {"value": user_id}}])
        )

        points, _ = search_results
        return [
            {"role": point.payload.get("role", "user"), "content": point.payload.get("message", "")}
            for point in points
        ]

    except Exception as e:
        print(f"❌ Failed to fetch chat history: {e}")
        return []



    



    






def ensure_user_exist(user_id: int) -> bool:
    """Ensure a user exists in the Qdrant user collection."""
    try:
        search_results = qdrant_client.scroll(
            collection_name=USER_COLLECTION,
            limit=1,
            scroll_filter=Filter(must=[{"key": "user_id", "match": {"value": user_id}}])
        )

        points, _ = search_results
        if points:
            logger.info(f"✅ User {user_id} exists.")
            return True
        else:
            logger.info(f"🔴 User {user_id} does not exist.")
            return False

    except Exception as e:
        logger.error(f"❌ Failed to check existence of user {user_id}: {e}", exc_info=True)
        return False

# Ensure Qdrant collection exists
ensure_collection_exists()
