import logging
from mistralai import Mistral
from .config import MISTRAL_API_KEY
from .services import get_recent_chat_history, store_chat_message
# ✅ Ensure API key is set
if not MISTRAL_API_KEY:
    raise ValueError("❌ MISTRAL_API_KEY is not set. Please check your environment variables.")

# ✅ Initialize Mistral client
client = Mistral(api_key=MISTRAL_API_KEY)

def query_mistral(user_id: int, user_message: str) -> str:
    """
    Query Mistral with user chat history for better context.
    """
    try:
        # ✅ Fetch chat history for better responses
        chat_history = get_recent_chat_history(user_id)

        # ✅ Add system instruction
        messages = [{"role": "system", "content": "You are a financial assistant helping users analyze spending."}]
        
        # ✅ Append past conversations
        messages.extend(chat_history)

        # ✅ Append new user query
        messages.append({"role": "user", "content": user_message})

        response = client.chat.complete(
            model="ft:open-mistral-7b:adec0789:20250312:1955206e",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )

        bot_reply = response.choices[0].message.content

        # ✅ Store user query and bot response in Qdrant
        store_chat_message(user_id, "user", user_message)
        store_chat_message(user_id, "assistant", bot_reply)

        return bot_reply

    except Exception as e:
        logging.error(f"❌ Mistral API Error: {str(e)}", exc_info=True)
        return "Error processing your request."


