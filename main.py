from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.user_routes import router as user_router
from app.routes.expense_routes import router as expense_router
from app.routes.chart_routes import router as chart_router
from app.routes.mistral_routes import router as mistral_router  # Import Mistral routes
from app.routes.ideal_scenario_routes import router as ideal_scenario_router  # Ideal scenario routes
from app.database import init_db

app = FastAPI(title="Financial Manager Chatbot API")

# CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


# Include routers in the FastAPI app
app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(expense_router, prefix="/api", tags=["Expenses"])
app.include_router(chart_router, prefix="/api", tags=["Charts"])
app.include_router(mistral_router, prefix="/api", tags=["Mistral"])  # Include Mistral router
app.include_router(ideal_scenario_router, prefix="/api", tags=["Ideal Scenario"])




@app.get("/")
def home():
    return {"message": "Welcome to the Financial Chatbot API"}