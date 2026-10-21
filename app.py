"""
FinPulse AI - FastAPI Web Application & Financial Intelligence API
Serves the financial planning dashboard, advisor copilot, and 24/7 client chatbot.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os

from core.budgeting import analyze_transactions, build_tailored_budget_plan
from core.forecasting import run_monte_carlo_simulation, calculate_fire_metrics
from core.debt_planner import compare_debt_strategies
from core.report_generator import generate_client_report
from core.advisor_engine import answer_financial_query
from core.risk_profiler import get_risk_profile
from core.mock_data import CLIENT_PROFILES, get_client_profile

app = FastAPI(
    title="FinPulse AI - Financial Planning & Advisor Intelligence Suite",
    description="Dual-mode AI platform for Advisor Workflow Automation and 24/7 Client Financial Advisory.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ChatRequest(BaseModel):
    client_id: str = "alex_chen"
    message: str
    history: Optional[List[Dict[str, str]]] = []

class MonteCarloRequest(BaseModel):
    current_wealth: float = 85000.0
    monthly_contribution: float = 1600.0
    years_to_retirement: int = 27
    years_in_retirement: int = 30
    annual_retirement_spend: float = 70000.0
    expected_return: float = 0.075
    volatility: float = 0.15
    inflation_rate: float = 0.025
    num_simulations: int = 1000

class DebtPayoffRequest(BaseModel):
    debts: List[Dict[str, Any]]
    extra_monthly_payment: float = 300.0

class SpendingAnalysisRequest(BaseModel):
    transactions: List[Dict[str, Any]]
    monthly_income: float

class TailoredBudgetRequest(BaseModel):
    monthly_income: float = 30000.0
    fixed_costs: float = 20000.0

# In-memory store for client mutations (resets on restart)
clients_db = {k: dict(v) for k, v in CLIENT_PROFILES.items()}

@app.get("/api/clients")
def list_clients():
    """Returns available client summary cards."""
    summaries = []
    for cid, c in clients_db.items():
        total_inv = sum(c.get("investments", {}).values())
        total_debt = sum(d.get("balance", 0) for d in c.get("debts", []))
        net_worth = total_inv + c.get("emergency_fund", 0) - total_debt
        summaries.append({
            "id": cid,
            "name": c["name"],
            "age": c["age"],
            "occupation": c["occupation"],
            "monthly_net_income": c["monthly_net_income"],
            "risk_tolerance": c["risk_tolerance"],
            "net_worth": round(net_worth, 2),
            "total_debt": round(total_debt, 2),
            "num_goals": len(c.get("goals", []))
        })
    return summaries

@app.get("/api/client/{client_id}")
def get_client(client_id: str):
    """Returns full details for a client."""
    if client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Client not found")
    client = clients_db[client_id]
    
    # Calculate initial overview numbers
    report = generate_client_report(client)
    return {
        "profile": client,
        "report": report
    }

@app.post("/api/chat")
def chat_with_advisor(req: ChatRequest):
    """Processes natural language financial inquiries for a client."""
    client = clients_db.get(req.client_id, clients_db["alex_chen"])
    result = answer_financial_query(req.message, client, req.history)
    return result

@app.post("/api/monte-carlo")
def simulate_monte_carlo(req: MonteCarloRequest):
    """Runs 1,000-iteration stochastic Monte Carlo wealth simulation."""
    res = run_monte_carlo_simulation(
        current_wealth=req.current_wealth,
        monthly_contribution=req.monthly_contribution,
        years_to_retirement=req.years_to_retirement,
        years_in_retirement=req.years_in_retirement,
        annual_retirement_spend=req.annual_retirement_spend,
        expected_return=req.expected_return,
        volatility=req.volatility,
        inflation_rate=req.inflation_rate,
        num_simulations=req.num_simulations
    )
    return res

@app.post("/api/debt-payoff")
def evaluate_debt(req: DebtPayoffRequest):
    """Compares Avalanche vs Snowball debt elimination strategies."""
    res = compare_debt_strategies(req.debts, req.extra_monthly_payment)
    return res

@app.post("/api/analyze-spending")
def analyze_spending(req: SpendingAnalysisRequest):
    """Runs categorization, subscription detection, and 50/30/20 analysis."""
    res = analyze_transactions(req.transactions, req.monthly_income)
    return res

@app.post("/api/tailored-budget")
def get_tailored_budget(req: TailoredBudgetRequest):
    """Calculates adaptive financial plan for custom income & fixed costs."""
    return build_tailored_budget_plan(req.monthly_income, req.fixed_costs)

@app.get("/api/report/{client_id}")
def get_report(client_id: str):
    """Generates complete client executive report."""
    if client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Client not found")
    return generate_client_report(clients_db[client_id])

# Serve static assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "FinPulse AI API is running. Please check static files."}
