"""
Budgeting & Spending Intelligence Engine
Categorizes financial transactions, extracts recurring subscriptions,
detects spending patterns and anomalies, and evaluates 50/30/20 budget adherence.
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict
import re

# Defined in priority order so more specific categories match first
CATEGORY_RULES = [
    ("Debt Payments", ["credit card payment", "student loan", "nelnet", "sofi loan", "personal loan", "auto loan", "car loan", "min payment"]),
    ("Housing", ["rent", "mortgage", "hoa", "property tax", "home insurance", "apartment rent"]),
    ("Transportation", ["chevron", "shell", "gas station", "exxon", "bp", "uber", "lyft", "transit", "subway", "metro", "car insurance", "parking", "auto insurance"]),
    ("Utilities", ["electric", "power", "water", "natural gas", "gas utility", "internet", "wifi", "comcast", "verizon", "att", "t-mobile", "sewer"]),
    ("Groceries", ["supermarket", "whole foods", "trader joe", "kroger", "costco", "safeway", "walmart grocery", "grocer", "market"]),
    ("Subscriptions", ["gym", "fitness", "equinox", "netflix", "spotify", "apple", "amazon prime", "youtube", "chatgpt", "cloud storage", "icloud", "disney+", "hulu", "nytimes", "adobe"]),
    ("Dining & Entertainment", ["restaurant", "cafe", "coffee", "blue bottle", "starbucks", "uber eats", "doordash", "grubhub", "bar", "cinema", "amc", "bistro", "sushi", "thai"]),
    ("Healthcare", ["pharmacy", "cvs", "walgreens", "doctor", "clinic", "dental", "vision", "hospital", "health insurance", "pediatrician"]),
    ("Investments & Savings", ["vanguard", "fidelity", "schwab", "robinhood", "ira", "401k", "transfer to savings", "treasury direct"]),
    ("Shopping & Discretionary", ["amazon", "target", "clothing", "nike", "nordstrom", "best buy", "electronics", "zara", "sephora"])
]

CATEGORY_CLASSIFICATION = {
    "Housing": "Needs",
    "Utilities": "Needs",
    "Groceries": "Needs",
    "Healthcare": "Needs",
    "Transportation": "Needs",
    "Dining & Entertainment": "Wants",
    "Subscriptions": "Wants",
    "Shopping & Discretionary": "Wants",
    "Investments & Savings": "Savings",
    "Debt Payments": "Needs"
}

def categorize_transaction(description: str, amount: float) -> str:
    """Categorizes a transaction based on rule-priority keyword matching."""
    desc_clean = description.lower()
    
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc_clean) or kw in desc_clean:
                return category
                
    return "Shopping & Discretionary" if amount < 200 else "Other Expenses"

def analyze_transactions(transactions: List[Dict[str, Any]], monthly_income: float) -> Dict[str, Any]:
    """
    Analyzes transaction list:
    - Categorization & spending breakdown
    - 50/30/20 rule comparison (Needs, Wants, Savings)
    - Recurring subscription detection
    - High-frequency merchant detection
    - Discretionary leak identification
    """
    category_totals = defaultdict(float)
    merchant_counts = defaultdict(int)
    merchant_totals = defaultdict(float)
    class_totals = {"Needs": 0.0, "Wants": 0.0, "Savings": 0.0}
    
    categorized_txs = []
    total_spent = 0.0
    
    # Extract sub keywords for subscription detection
    sub_keywords = []
    for cat, kws in CATEGORY_RULES:
        if cat == "Subscriptions":
            sub_keywords = kws
            break

    for tx in transactions:
        amount = float(tx.get("amount", 0.0))
        desc = tx.get("description", "Unknown")
        date = tx.get("date", "")
        
        # Categorize if not already specified
        cat = tx.get("category") or categorize_transaction(desc, amount)
        classification = CATEGORY_CLASSIFICATION.get(cat, "Wants")
        
        category_totals[cat] += amount
        merchant_counts[desc] += 1
        merchant_totals[desc] += amount
        class_totals[classification] += amount
        total_spent += amount
        
        categorized_txs.append({
            "id": tx.get("id", len(categorized_txs) + 1),
            "date": date,
            "description": desc,
            "amount": round(amount, 2),
            "category": cat,
            "classification": classification
        })
    
    # Identify recurring subscriptions
    detected_subscriptions = []
    for merchant, count in merchant_counts.items():
        avg_amt = merchant_totals[merchant] / count
        is_sub_kw = any(kw in merchant.lower() for kw in sub_keywords)
        if (count >= 2 or is_sub_kw) and avg_amt <= 300:
            detected_subscriptions.append({
                "merchant": merchant,
                "occurrences": count,
                "monthly_cost": round(avg_amt, 2),
                "annual_cost": round(avg_amt * 12, 2)
            })
            
    total_subscription_annual = sum(s["annual_cost"] for s in detected_subscriptions)
    
    # 50/30/20 Analysis
    needs_pct = round((class_totals["Needs"] / monthly_income * 100), 1) if monthly_income > 0 else 0
    wants_pct = round((class_totals["Wants"] / monthly_income * 100), 1) if monthly_income > 0 else 0
    savings_actual = monthly_income - total_spent
    savings_pct = round((savings_actual / monthly_income * 100), 1) if monthly_income > 0 else 0
    
    # Budget Health Score (0 - 100)
    score = 100
    if needs_pct > 50:
        score -= min(35, (needs_pct - 50) * 1.5)
    if wants_pct > 30:
        score -= min(35, (wants_pct - 30) * 1.5)
    if savings_pct < 20:
        score -= min(30, (20 - max(0, savings_pct)) * 2)
    score = max(10, min(100, round(score)))
    
    # Insights & Anomalies
    insights = []
    if needs_pct > 50:
        insights.append(f"Fixed needs absorb {needs_pct}% of income (ideal is under 50%). Consider refinancing debt or optimizing utility/housing expenses.")
    else:
        insights.append(f"Healthy fixed needs ratio at {needs_pct}% (below the 50% target threshold).")
        
    if wants_pct > 30:
        insights.append(f"Discretionary spending is high at {wants_pct}% of net income. Found {len(detected_subscriptions)} recurring subscriptions totaling ${round(total_subscription_annual/12, 2)}/mo.")
    else:
        insights.append(f"Discretionary spending is well controlled at {wants_pct}% of net income.")
        
    if savings_pct >= 20:
        insights.append(f"Excellent savings rate of {savings_pct}%! This puts client well on track for wealth compounding.")
    elif savings_pct > 0:
        insights.append(f"Current savings rate is {savings_pct}%. Aim to increase this towards 20% by redirecting unneeded recurring subscriptions.")
    else:
        insights.append(f"Current net cash flow is negative (-${abs(round(savings_actual, 2))}/mo). Immediate cash-burn mitigation recommended.")

    return {
        "total_spent": round(total_spent, 2),
        "monthly_income": round(monthly_income, 2),
        "net_cashflow": round(savings_actual, 2),
        "category_breakdown": {k: round(v, 2) for k, v in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)},
        "fifty_thirty_twenty": {
            "needs": {"amount": round(class_totals["Needs"], 2), "percent": needs_pct, "target_percent": 50},
            "wants": {"amount": round(class_totals["Wants"], 2), "percent": wants_pct, "target_percent": 30},
            "savings": {"amount": round(max(0, savings_actual), 2), "percent": max(0, savings_pct), "target_percent": 20}
        },
        "budget_score": score,
        "subscriptions": detected_subscriptions,
        "total_subscription_annual": round(total_subscription_annual, 2),
        "insights": insights,
        "transactions": categorized_txs
    }
