"""
Wealth Forecasting & Monte Carlo Stochastic Engine
Simulates 1,000 randomized market trajectories to quantify Sequence of Returns Risk,
calculates retirement probability of success, and computes FIRE milestones.
"""

import math
import random
from typing import Dict, Any, List

def run_monte_carlo_simulation(
    current_wealth: float,
    monthly_contribution: float,
    years_to_retirement: int,
    years_in_retirement: int = 30,
    annual_retirement_spend: float = 60000.0,
    expected_return: float = 0.075,       # 7.5% annual nominal return
    volatility: float = 0.15,             # 15% annual standard deviation
    inflation_rate: float = 0.025,        # 2.5% inflation
    num_simulations: int = 1000
) -> Dict[str, Any]:
    """
    Simulates stochastic paths over the accumulation phase + decumulation phase.
    Accounts for Sequence of Returns Risk and variable inflation-adjusted withdrawals.
    """
    total_years = years_to_retirement + years_in_retirement
    annual_contribution = monthly_contribution * 12
    
    # Store annual balances for every simulation
    # trajectories[year_idx] = list of balances across all simulations
    yearly_paths = [[] for _ in range(total_years + 1)]
    success_count = 0
    final_balances = []
    
    random.seed(42) # Consistent reproducible benchmark results
    
    for _ in range(num_simulations):
        balance = current_wealth
        yearly_paths[0].append(balance)
        failed = False
        
        # Accumulation Phase
        for yr in range(1, years_to_retirement + 1):
            # Lognormal market return shock: r = exp( (mu - 0.5*sigma^2) + sigma * Z ) - 1
            z = random.gauss(0, 1)
            annual_r = math.exp((expected_return - 0.5 * (volatility ** 2)) + volatility * z) - 1
            
            balance = (balance + annual_contribution) * (1 + annual_r)
            if balance < 0:
                balance = 0
            yearly_paths[yr].append(balance)
            
        # Decumulation (Retirement) Phase
        current_withdrawal = annual_retirement_spend * ((1 + inflation_rate) ** years_to_retirement)
        for yr in range(years_to_retirement + 1, total_years + 1):
            if balance <= 0:
                balance = 0
                failed = True
            else:
                z = random.gauss(0, 1)
                annual_r = math.exp((expected_return - 0.5 * (volatility ** 2)) + volatility * z) - 1
                
                # Withdraw at start of year, remaining grows
                balance = max(0, balance - current_withdrawal)
                balance = balance * (1 + annual_r)
                current_withdrawal *= (1 + inflation_rate)
                
            yearly_paths[yr].append(balance)
            
        if balance > 0 and not failed:
            success_count += 1
        final_balances.append(balance)

    # Compute percentiles for each year (10th, 25th, 50th/Median, 75th, 90th)
    labels = []
    p10_trajectory = []
    p50_trajectory = []
    p90_trajectory = []
    
    for yr in range(total_years + 1):
        vals = sorted(yearly_paths[yr])
        labels.append(f"Yr {yr}")
        idx_10 = int(0.10 * (len(vals) - 1))
        idx_50 = int(0.50 * (len(vals) - 1))
        idx_90 = int(0.90 * (len(vals) - 1))
        
        p10_trajectory.append(round(vals[idx_10], 0))
        p50_trajectory.append(round(vals[idx_50], 0))
        p90_trajectory.append(round(vals[idx_90], 0))
        
    probability_of_success = round((success_count / num_simulations) * 100, 1)
    
    # Portfolio value at retirement milestone
    median_at_retirement = p50_trajectory[years_to_retirement]
    p10_at_retirement = p10_trajectory[years_to_retirement]
    p90_at_retirement = p90_trajectory[years_to_retirement]
    
    # Assess resilience
    if probability_of_success >= 85:
        health_assessment = "High Confidence Plan: Extremely resilient against historical down-market sequences."
        badge = "success"
    elif probability_of_success >= 70:
        health_assessment = "Moderate Confidence: Viable, but vulnerable to prolonged early-retirement bear markets."
        badge = "warning"
    else:
        health_assessment = "Action Required: Significant probability of portfolio depletion. Increase contributions or adjust target retirement age."
        badge = "danger"

    return {
        "num_simulations": num_simulations,
        "probability_of_success": probability_of_success,
        "health_assessment": health_assessment,
        "badge": badge,
        "years_to_retirement": years_to_retirement,
        "years_in_retirement": years_in_retirement,
        "labels": labels,
        "p10_trajectory": p10_trajectory, # Bearish
        "p50_trajectory": p50_trajectory, # Median
        "p90_trajectory": p90_trajectory, # Bullish
        "median_at_retirement": median_at_retirement,
        "p10_at_retirement": p10_at_retirement,
        "p90_at_retirement": p90_at_retirement,
        "median_final": p50_trajectory[-1]
    }

def calculate_fire_metrics(
    annual_expenses: float,
    current_net_worth: float,
    annual_savings: float,
    expected_real_return: float = 0.05, # Real return after inflation
    swr: float = 0.04                   # 4% safe withdrawal rate
) -> Dict[str, Any]:
    """
    Computes FIRE (Financial Independence, Retire Early) benchmarks:
    - Standard FIRE (25x expenses)
    - Lean FIRE (75% expenses)
    - Fat FIRE (135% expenses)
    - Coast FIRE (Already saved enough to reach standard FIRE at 65 without saving another dime)
    - Estimated years until FIRE
    """
    fire_target = annual_expenses / swr
    lean_fire_target = (annual_expenses * 0.75) / swr
    fat_fire_target = (annual_expenses * 1.35) / swr
    
    # Years to reach standard FIRE using geometric compound accumulation
    # FV = PV*(1+r)^n + PMT * [((1+r)^n - 1) / r]
    # We solve iteratively for accuracy
    years_to_fire = None
    balance = current_net_worth
    for yr in range(1, 60):
        balance = balance * (1 + expected_real_return) + annual_savings
        if balance >= fire_target:
            years_to_fire = yr
            break
            
    if years_to_fire is None:
        years_to_fire = 60 # >60 years
        
    # Coast FIRE calculation for age 65 (assuming typical current age 30 or 25 years horizon)
    horizon_to_65 = 25
    coast_fire_needed = fire_target / ((1 + expected_real_return) ** horizon_to_65)
    is_coast_fire = current_net_worth >= coast_fire_needed

    return {
        "fire_target": round(fire_target, 2),
        "lean_fire_target": round(lean_fire_target, 2),
        "fat_fire_target": round(fat_fire_target, 2),
        "current_progress_pct": round(min(100.0, (current_net_worth / fire_target) * 100), 1),
        "estimated_years_to_fire": years_to_fire,
        "coast_fire_needed": round(coast_fire_needed, 2),
        "is_coast_fire": is_coast_fire
    }
