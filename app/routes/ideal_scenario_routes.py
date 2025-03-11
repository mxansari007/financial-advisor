from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import SessionLocal, IdealScenario, User

router = APIRouter()

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Ideal Scenario Schema
class IdealScenarioCreate(BaseModel):
    food_limit: float
    transport_limit: float
    entertainment_limit: float

# API: Set Ideal Scenario
@router.post("/ideal_scenario/{user_id}")
def set_ideal_scenario(user_id: int, scenario: IdealScenarioCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ideal_scenario = IdealScenario(user_id=user_id, **scenario.dict())
    db.add(ideal_scenario)
    db.commit()
    db.refresh(ideal_scenario)
    return ideal_scenario

# API: Get Ideal Scenario
@router.get("/ideal_scenario/{user_id}")
def get_ideal_scenario(user_id: int, db: Session = Depends(get_db)):
    ideal_scenario = db.query(IdealScenario).filter(IdealScenario.user_id == user_id).first()
    if not ideal_scenario:
        raise HTTPException(status_code=404, detail="Ideal Scenario not set")
    return ideal_scenario
