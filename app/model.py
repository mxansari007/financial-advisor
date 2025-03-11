import os
from mistralai import Mistral
from .config import MISTRAL_API_KEY
from .database import SessionLocal, Expense

from transformers import AutoModelForCausalLM, AutoTokenizer

# Load fine-tuned model
model_name = "../training/mistral_finetuned"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)





client = Mistral(api_key=MISTRAL_API_KEY)

def get_financial_advice(user_input):
    messages = [{"role": "user", "content": user_input}]
    response = client.chat.complete(model="mistral-tiny", messages=messages)
    return response.choices[0].message.content


def get_spending_advice(user_id):
    db = SessionLocal()
    expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
    
    total_spent = sum(e.amount for e in expenses)
    category_spending = {}
    for e in expenses:
        category_spending[e.category] = category_spending.get(e.category, 0) + e.amount

    # AI Prompt
    prompt = f"User spent ${total_spent} this month. Breakdown: {category_spending}. Suggest improvements."

    messages = [ChatMessage(role="user", content=prompt)]
    response = client.chat(model="mistral-tiny", messages=messages)
    
    return response.choices[0].message.content