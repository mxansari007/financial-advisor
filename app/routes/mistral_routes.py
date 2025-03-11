import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from mistralai import Mistral
from ..database import SessionLocal, Expense, IdealScenario, User
from datetime import datetime

# Initialize Mistral Client
api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"
client = Mistral(api_key=api_key)

router = APIRouter()

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mistral Chat Input Schema
class ChatMessageInput(BaseModel):
    user_id: int  # Add user_id to the schema
    user_message: str

# Route to Handle Chat Messages
@router.post("/chat")
async def chat_with_financial_advisor(message: ChatMessageInput, db: Session = Depends(get_db)):
    try:
        # Fetch user, expenses, and ideal scenario from the database
        user = db.query(User).filter(User.id == message.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        expenses = db.query(Expense).filter(Expense.user_id == message.user_id).filter(
            Expense.date >= datetime.utcnow().date()  # Only today's expenses
        ).all()

        ideal_scenario = db.query(IdealScenario).filter(IdealScenario.user_id == message.user_id).first()

        if not ideal_scenario:
            raise HTTPException(status_code=404, detail="Ideal scenario not set for user")

        # Prepare data to send to the chatbot
        total_expenses = sum(expense.amount for expense in expenses)
        ideal_food = ideal_scenario.food_limit
        ideal_transport = ideal_scenario.transport_limit
        ideal_entertainment = ideal_scenario.entertainment_limit

        chat_input = f"""
        User's daily expenses: {total_expenses} INR.
        Ideal food budget: {ideal_food} INR.
        Ideal transport budget: {ideal_transport} INR.
        Ideal entertainment budget: {ideal_entertainment} INR.
        
        The user is asking for advice: "{message.user_message}"
        """

        # Send the data to Mistral API for analysis and response
        chat_response = client.chat.complete(
            model=model,
            messages=[
                {"role": "user", "content": chat_input}
            ]
        )

        # Return Mistral's response
        return {"response": chat_response.choices[0].message.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# API: Get Financial Insight (Today's Expenses vs Ideal Scenario)
@router.get("/financial_insight/{user_id}")
def get_financial_insight(user_id: int, db: Session = Depends(get_db)):
    # Get Today's Date
    today = datetime.utcnow().date()

    currency = 'Indian Rupees'

    # Get the user's expenses for today
    expenses_today = db.query(Expense).filter(Expense.user_id == user_id, Expense.date >= today).all()

    # Get the user's ideal scenario
    ideal_scenario = db.query(IdealScenario).filter(IdealScenario.user_id == user_id).first()
    if not ideal_scenario:
        raise HTTPException(status_code=404, detail="Ideal Scenario not set for the user")

    if not expenses_today:
        raise HTTPException(status_code=404, detail="No expenses found for today")

    # Calculate total spent by category
    total_spent = {"food": 0, "transport": 0, "entertainment": 0}
    for expense in expenses_today:
        # Assuming `category` is a field in the Expense table, make sure it's populated correctly
        if expense.category in total_spent:
            total_spent[expense.category] += expense.amount

    # Compare with the ideal scenario and generate advice
    advice = []
    for category, spent in total_spent.items():
        ideal_limit = getattr(ideal_scenario, f"{category}_limit")
        if spent > ideal_limit:
            advice.append(f"You've overspent on {category} by {spent - ideal_limit:.2f}. Try to reduce this spending.")
        elif spent < ideal_limit:
            advice.append(f"You've saved on {category} by {ideal_limit - spent:.2f}. Good job!")
        else:
            advice.append(f"Your spending on {category} is on target. Keep it up!")

    # Prepare the message to send to Mistral
    message = f"Currency of spending is {currency}. Here is the analysis of your daily expenses:\n" + "\n".join(advice)

    # Send the financial insight to Mistral for more personalized advice
    try:
        chat_response = client.chat.complete(
            model=model,
            messages=[
                {"role": "user", "content": message}
            ]
        )
        # Return Mistral's response
        return {"response": chat_response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in Mistral API: {str(e)}")
