"""
Debt Optimization Engine
Simulates and contrasts Debt Avalanche (Highest APR First) vs Debt Snowball (Lowest Balance First)
to provide exact payoff timelines, total interest paid, and interest savings.
"""

from typing import List, Dict, Any
import copy

def calculate_debt_payoff(
    debts: List[Dict[str, Any]],
    extra_monthly_payment: float = 300.0,
    strategy: str = "avalanche"
) -> Dict[str, Any]:
    """
    Simulates monthly amortization payoff schedule.
    strategy can be 'avalanche' or 'snowball'.
    """
    # Clone debts so we don't mutate input
    active_debts = [copy.deepcopy(d) for d in debts]
    for d in active_debts:
        d["balance"] = float(d["balance"])
        d["apr"] = float(d["apr"]) / 100.0 # convert 18.5% -> 0.185
        d["monthly_rate"] = d["apr"] / 12.0
        d["min_payment"] = float(d["min_payment"])

    # Sorting
    if strategy.lower() == "avalanche":
        # Sort by APR descending
        active_debts.sort(key=lambda x: x["apr"], reverse=True)
    else: # snowball
        # Sort by balance ascending
        active_debts.sort(key=lambda x: x["balance"])

    month = 0
    total_interest_paid = 0.0
    total_principal_paid = 0.0
    schedule = [] # sample checkpoints: 0, 6, 12, 18, 24, etc.
    payoff_milestones = []
    
    # Track initial total balance
    initial_total = sum(d["balance"] for d in active_debts)
    
    max_months = 360 # 30 years limit
    
    while any(d["balance"] > 0 for d in active_debts) and month < max_months:
        month += 1
        month_interest = 0.0
        
        # 1. Accrue monthly interest
        for d in active_debts:
            if d["balance"] > 0:
                interest = d["balance"] * d["monthly_rate"]
                month_interest += interest
                d["balance"] += interest
                
        total_interest_paid += month_interest
        
        # 2. Pay minimums first
        extra_pool = extra_monthly_payment
        for d in active_debts:
            if d["balance"] > 0:
                payment = min(d["balance"], d["min_payment"])
                d["balance"] -= payment
                total_principal_paid += payment
                if d["balance"] == 0:
                    payoff_milestones.append({
                        "debt_name": d["name"],
                        "month_cleared": month,
                        "years": round(month / 12, 1)
                    })
                    
        # 3. Apply extra payment pool to the primary target
        for d in active_debts:
            if d["balance"] > 0 and extra_pool > 0:
                payment = min(d["balance"], extra_pool)
                d["balance"] -= payment
                extra_pool -= payment
                total_principal_paid += payment
                if d["balance"] == 0 and not any(m["debt_name"] == d["name"] for m in payoff_milestones):
                    payoff_milestones.append({
                        "debt_name": d["name"],
                        "month_cleared": month,
                        "years": round(month / 12, 1)
                    })
                if extra_pool <= 0:
                    break
                    
        # Record periodic snapshot
        remaining_balance = sum(d["balance"] for d in active_debts)
        if month == 1 or month % 6 == 0 or remaining_balance == 0:
            schedule.append({
                "month": month,
                "remaining_balance": round(remaining_balance, 2),
                "cumulative_interest": round(total_interest_paid, 2)
            })
            
        if remaining_balance == 0:
            break

    return {
        "strategy": strategy,
        "months_to_debt_free": month,
        "years_to_debt_free": round(month / 12, 1),
        "total_interest_paid": round(total_interest_paid, 2),
        "total_paid": round(initial_total + total_interest_paid, 2),
        "milestones": payoff_milestones,
        "schedule": schedule
    }

def compare_debt_strategies(
    debts: List[Dict[str, Any]],
    extra_monthly_payment: float = 300.0
) -> Dict[str, Any]:
    """
    Runs both Avalanche and Snowball strategies and minimum payments only,
    comparing savings and speed.
    """
    avalanche_res = calculate_debt_payoff(debts, extra_monthly_payment, strategy="avalanche")
    snowball_res = calculate_debt_payoff(debts, extra_monthly_payment, strategy="snowball")
    minimums_res = calculate_debt_payoff(debts, extra_monthly_payment=0.0, strategy="avalanche")
    
    interest_saved_vs_minimums = round(minimums_res["total_interest_paid"] - avalanche_res["total_interest_paid"], 2)
    interest_saved_avalanche_vs_snowball = round(snowball_res["total_interest_paid"] - avalanche_res["total_interest_paid"], 2)
    months_faster_vs_minimums = minimums_res["months_to_debt_free"] - avalanche_res["months_to_debt_free"]

    return {
        "avalanche": avalanche_res,
        "snowball": snowball_res,
        "minimums_only": minimums_res,
        "interest_saved_vs_minimums": max(0.0, interest_saved_vs_minimums),
        "interest_saved_avalanche_vs_snowball": max(0.0, interest_saved_avalanche_vs_snowball),
        "months_faster_vs_minimums": max(0, months_faster_vs_minimums),
        "recommendation": (
            "Avalanche strategy mathematically saves the most interest ($" 
            + str(interest_saved_avalanche_vs_snowball) 
            + " more than Snowball). Snowball offers earlier psychological wins if motivation is a barrier."
        )
    }
