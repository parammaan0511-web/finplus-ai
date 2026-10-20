"""
FinPulse AI Core Module
"""
from .budgeting import analyze_transactions, categorize_transaction
from .forecasting import run_monte_carlo_simulation, calculate_fire_metrics
from .debt_planner import calculate_debt_payoff, compare_debt_strategies
from .risk_profiler import get_risk_profile
from .report_generator import generate_client_report
from .advisor_engine import answer_financial_query
from .mock_data import CLIENT_PROFILES, get_client_profile

__all__ = [
    "analyze_transactions",
    "categorize_transaction",
    "run_monte_carlo_simulation",
    "calculate_fire_metrics",
    "calculate_debt_payoff",
    "compare_debt_strategies",
    "get_risk_profile",
    "generate_client_report",
    "answer_financial_query",
    "CLIENT_PROFILES",
    "get_client_profile"
]
