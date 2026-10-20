"""
Automated Executive Financial Report Generator
Generates comprehensive, audit-ready, client-facing financial planning reports
with radar scorecards, risk metrics, Monte Carlo percentiles, and advisor action items.
"""

from typing import Dict, Any
from .budgeting import analyze_transactions
from .forecasting import run_monte_carlo_simulation, calculate_fire_metrics
from .debt_planner import compare_debt_strategies
from .risk_profiler import get_risk_profile

def generate_client_report(client: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesizes complete financial health report for advisor or client delivery.
    """
    # 1. Budget & Spending
    tx_analysis = analyze_transactions(client.get("transactions", []), client.get("monthly_net_income", 0))
    
    # 2. Total Assets & Net Worth
    inv_dict = client.get("investments", {})
    total_investments = sum(inv_dict.values())
    emergency_fund = client.get("emergency_fund", 0.0)
    total_liquid_assets = total_investments + emergency_fund
    
    # Debts
    debts = client.get("debts", [])
    total_debt = sum(d["balance"] for d in debts)
    net_worth = total_liquid_assets - total_debt
    
    # 3. Liquidity Ratio (Emergency fund months of expenses)
    avg_monthly_exp = tx_analysis["total_spent"] if tx_analysis["total_spent"] > 0 else client.get("monthly_net_income", 5000) * 0.7
    emergency_months = round(emergency_fund / avg_monthly_exp, 1) if avg_monthly_exp > 0 else 0
    
    # 4. Debt-to-Income (DTI)
    total_monthly_debt = sum(d.get("min_payment", 0) for d in debts)
    dti_percent = round((total_monthly_debt / client.get("monthly_net_income", 1)) * 100, 1)
    
    # 5. Risk & Forecasting
    risk_info = get_risk_profile(client.get("risk_tolerance", "Moderate"))
    years_to_ret = max(1, client.get("target_retirement_age", 65) - client.get("age", 30))
    
    mc_results = run_monte_carlo_simulation(
        current_wealth=total_investments,
        monthly_contribution=client.get("monthly_savings_current", 1000),
        years_to_retirement=years_to_ret,
        years_in_retirement=30,
        annual_retirement_spend=client.get("target_annual_retirement_spend", 60000),
        expected_return=risk_info["expected_return"],
        volatility=risk_info["volatility"]
    )
    
    fire_stats = calculate_fire_metrics(
        annual_expenses=avg_monthly_exp * 12,
        current_net_worth=net_worth,
        annual_savings=client.get("monthly_savings_current", 1000) * 12
    )
    
    debt_plan = None
    if debts:
        debt_plan = compare_debt_strategies(debts, extra_monthly_payment=300.0)
        
    # Pillar Scores (0 to 100)
    # 1. Liquidity
    liquidity_score = min(100, int((emergency_months / 6.0) * 100))
    
    # 2. Debt Health (lower DTI is better)
    debt_score = 100 if not debts else max(20, int(100 - (dti_percent * 2.2)))
    
    # 3. Budget Discipline
    budget_score = tx_analysis["budget_score"]
    
    # 4. Retirement Readiness
    retirement_score = int(mc_results["probability_of_success"])
    
    # 5. Overall Health Composite
    overall_health = round((liquidity_score * 0.20) + (debt_score * 0.20) + (budget_score * 0.25) + (retirement_score * 0.35))
    
    # Executive Recommendations
    action_items = []
    if emergency_months < 3:
        action_items.append({
            "priority": "HIGH",
            "category": "Liquidity",
            "text": f"Build emergency reserves from {emergency_months} months to at least 3-6 months (${round(avg_monthly_exp * 3, 0):,})."
        })
    elif emergency_months > 9:
        action_items.append({
            "priority": "MEDIUM",
            "category": "Cash Drag",
            "text": f"Emergency reserves are currently {emergency_months} months. Consider moving excess cash beyond 6 months into high-yield accounts or diversified index investments."
        })
        
    if debts:
        high_apr_debts = [d for d in debts if d.get("apr", 0) > 10]
        if high_apr_debts:
            action_items.append({
                "priority": "HIGH",
                "category": "Debt Elimination",
                "text": f"Aggressively pay down high-interest credit card debt using the Avalanche method to save up to ${debt_plan['interest_saved_vs_minimums']:,} in interest."
            })
            
    if mc_results["probability_of_success"] < 75:
        action_items.append({
            "priority": "HIGH",
            "category": "Retirement Target",
            "text": f"Monte Carlo success rate is {mc_results['probability_of_success']}%. Increase monthly contributions by $300-$500 or adjust target retirement age to improve durability."
        })
    else:
        action_items.append({
            "priority": "LOW",
            "category": "Tax Optimization",
            "text": "Retirement probability is robust. Focus next on maximizing tax-advantaged buckets (HSA and Backdoor Roth IRA)."
        })

    report_payload = {
        "client": {
            "name": client["name"],
            "age": client["age"],
            "occupation": client["occupation"],
            "risk_tolerance": client["risk_tolerance"],
            "target_retirement_age": client["target_retirement_age"],
            "target_annual_retirement_spend": client["target_annual_retirement_spend"]
        },
        "scorecard": {
            "overall_health": overall_health,
            "liquidity_score": liquidity_score,
            "debt_score": debt_score,
            "budget_score": budget_score,
            "retirement_score": retirement_score,
            "emergency_months": emergency_months,
            "dti_percent": dti_percent
        },
        "balance_sheet": {
            "emergency_fund": emergency_fund,
            "total_investments": total_investments,
            "total_liquid_assets": total_liquid_assets,
            "total_debt": total_debt,
            "net_worth": net_worth,
            "investments_breakdown": inv_dict
        },
        "budget_analysis": tx_analysis,
        "forecasting": mc_results,
        "fire_metrics": fire_stats,
        "debt_plan": debt_plan,
        "risk_model": risk_info,
        "action_items": action_items
    }
    
    return report_payload
