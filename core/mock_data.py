"""
Mock Financial Datasets & Client Personas
Realistic multi-stage profiles for testing financial planning automation and AI advisory.
"""

CLIENT_PROFILES = {
    "alex_chen": {
        "id": "alex_chen",
        "name": "Alex Chen",
        "age": 28,
        "occupation": "Software Engineer",
        "monthly_net_income": 7500.0,
        "annual_gross_income": 125000.0,
        "risk_tolerance": "Growth",
        "emergency_fund": 22000.0,
        "investments": {
            "401k": 45000.0,
            "Roth IRA": 18000.0,
            "Taxable Brokerage": 12000.0,
            "Crypto": 3500.0
        },
        "monthly_savings_current": 1600.0,
        "target_retirement_age": 55,
        "target_annual_retirement_spend": 70000.0,
        "goals": [
            {"name": "Emergency Buffer (6 Mo)", "target": 25000.0, "current": 22000.0, "deadline": "2027-01"},
            {"name": "Condo Down Payment", "target": 75000.0, "current": 20000.0, "deadline": "2029-06"},
            {"name": "Coast FIRE at 35", "target": 350000.0, "current": 78500.0, "deadline": "2033-12"}
        ],
        "debts": [
            {"name": "Chase Sapphire Credit Card", "balance": 4200.0, "apr": 22.4, "min_payment": 120.0},
            {"name": "Federal Student Loan", "balance": 18500.0, "apr": 4.9, "min_payment": 210.0},
            {"name": "MacBook Financing", "balance": 1200.0, "apr": 0.0, "min_payment": 100.0}
        ],
        "transactions": [
            {"id": 1, "date": "2026-10-01", "description": "Apartment Rent & Parking", "amount": 2350.0, "category": "Housing"},
            {"id": 2, "date": "2026-10-02", "description": "Electric & Gas Utility", "amount": 145.0, "category": "Utilities"},
            {"id": 3, "date": "2026-10-02", "description": "Comcast Fiber Internet", "amount": 85.0, "category": "Utilities"},
            {"id": 4, "date": "2026-10-04", "description": "Trader Joe's Groceries", "amount": 165.0, "category": "Groceries"},
            {"id": 5, "date": "2026-10-05", "description": "Uber Eats Sushi Dinner", "amount": 68.0, "category": "Dining & Entertainment"},
            {"id": 6, "date": "2026-10-06", "description": "Blue Bottle Coffee", "amount": 24.0, "category": "Dining & Entertainment"},
            {"id": 7, "date": "2026-10-08", "description": "Whole Foods Market", "amount": 190.0, "category": "Groceries"},
            {"id": 8, "date": "2026-10-10", "description": "Equinox Fitness Gym", "amount": 260.0, "category": "Subscriptions"},
            {"id": 9, "date": "2026-10-10", "description": "Netflix Subscription", "amount": 22.0, "category": "Subscriptions"},
            {"id": 10, "date": "2026-10-11", "description": "Spotify Premium", "amount": 11.99, "category": "Subscriptions"},
            {"id": 11, "date": "2026-10-12", "description": "ChatGPT Plus OpenAI", "amount": 20.0, "category": "Subscriptions"},
            {"id": 12, "date": "2026-10-13", "description": "Amazon Online Purchase - Electronics", "amount": 185.0, "category": "Shopping & Discretionary"},
            {"id": 13, "date": "2026-10-14", "description": "Uber Rides Downtown Weekend", "amount": 92.0, "category": "Transportation"},
            {"id": 14, "date": "2026-10-15", "description": "Craft Cocktail Bar Night", "amount": 145.0, "category": "Dining & Entertainment"},
            {"id": 15, "date": "2026-10-16", "description": "DoorDash Thai Cuisine", "amount": 54.0, "category": "Dining & Entertainment"},
            {"id": 16, "date": "2026-10-18", "description": "Chevron Gas Station", "amount": 62.0, "category": "Transportation"},
            {"id": 17, "date": "2026-10-19", "description": "Federal Student Loan Payment", "amount": 210.0, "category": "Debt Payments"},
            {"id": 18, "date": "2026-10-19", "description": "Chase Credit Card Min Payment", "amount": 120.0, "category": "Debt Payments"},
            {"id": 19, "date": "2026-10-20", "description": "Apple iCloud Storage", "amount": 9.99, "category": "Subscriptions"},
            {"id": 20, "date": "2026-10-20", "description": "Zara Clothing", "amount": 135.0, "category": "Shopping & Discretionary"}
        ]
    },
    "millers_family": {
        "id": "millers_family",
        "name": "Sarah & David Miller",
        "age": 42,
        "occupation": "Product Director & Nurse Anesthetist",
        "monthly_net_income": 13800.0,
        "annual_gross_income": 225000.0,
        "risk_tolerance": "Moderate",
        "emergency_fund": 55000.0,
        "investments": {
            "David 401k": 280000.0,
            "Sarah 403b": 195000.0,
            "Roth IRAs": 65000.0,
            "529 College Savings": 48000.0,
            "Taxable Brokerage": 52000.0
        },
        "monthly_savings_current": 3200.0,
        "target_retirement_age": 62,
        "target_annual_retirement_spend": 95000.0,
        "goals": [
            {"name": "Kids College 529 Fund", "target": 120000.0, "current": 48000.0, "deadline": "2032-09"},
            {"name": "Retirement Portfolio ($2.2M)", "target": 2200000.0, "current": 640000.0, "deadline": "2046-06"},
            {"name": "Home Solar & Roof Upgrade", "target": 30000.0, "current": 18000.0, "deadline": "2027-08"}
        ],
        "debts": [
            {"name": "Primary Home Mortgage (3.2%)", "balance": 340000.0, "apr": 3.2, "min_payment": 2150.0},
            {"name": "Subaru Outback Auto Loan", "balance": 11500.0, "apr": 4.8, "min_payment": 340.0}
        ],
        "transactions": [
            {"id": 1, "date": "2026-10-01", "description": "Mortgage & Escrow Payment", "amount": 2150.0, "category": "Housing"},
            {"id": 2, "date": "2026-10-02", "description": "City Water & Sewer Utility", "amount": 160.0, "category": "Utilities"},
            {"id": 3, "date": "2026-10-03", "description": "Electric & Natural Gas", "amount": 240.0, "category": "Utilities"},
            {"id": 4, "date": "2026-10-04", "description": "Costco Wholesale Bulk Groceries", "amount": 480.0, "category": "Groceries"},
            {"id": 5, "date": "2026-10-05", "description": "Safeway Family Groceries", "amount": 220.0, "category": "Groceries"},
            {"id": 6, "date": "2026-10-07", "description": "Youth Soccer League & Gear", "amount": 280.0, "category": "Shopping & Discretionary"},
            {"id": 7, "date": "2026-10-08", "description": "Subaru Auto Loan Amortization", "amount": 340.0, "category": "Debt Payments"},
            {"id": 8, "date": "2026-10-09", "description": "Family Dinner Out Bistro", "amount": 185.0, "category": "Dining & Entertainment"},
            {"id": 9, "date": "2026-10-12", "description": "Auto Insurance Geico", "amount": 195.0, "category": "Transportation"},
            {"id": 10, "date": "2026-10-14", "description": "Streaming Bundle & Disney+", "amount": 35.0, "category": "Subscriptions"},
            {"id": 11, "date": "2026-10-15", "description": "Target Household Supplies", "amount": 175.0, "category": "Shopping & Discretionary"},
            {"id": 12, "date": "2026-10-18", "description": "Dental Copays & Pediatrician", "amount": 140.0, "category": "Healthcare"}
        ]
    },
    "elena_rostova": {
        "id": "elena_rostova",
        "name": "Elena Rostova",
        "age": 59,
        "occupation": "SVP Operations",
        "monthly_net_income": 12800.0,
        "annual_gross_income": 240000.0,
        "risk_tolerance": "Moderately Conservative",
        "emergency_fund": 90000.0,
        "investments": {
            "Traditional 401k": 1180000.0,
            "Rollover IRA": 320000.0,
            "Taxable Index Funds": 285000.0,
            "Treasury Bonds & CDs": 150000.0
        },
        "monthly_savings_current": 4500.0,
        "target_retirement_age": 63,
        "target_annual_retirement_spend": 90000.0,
        "goals": [
            {"name": "Retire at 63 with $2.1M", "target": 2100000.0, "current": 1935000.0, "deadline": "2030-10"},
            {"name": "Long-Term Healthcare Reserve", "target": 120000.0, "current": 90000.0, "deadline": "2028-05"}
        ],
        "debts": [], # Debt free!
        "transactions": [
            {"id": 1, "date": "2026-10-01", "description": "HOA Assessment & Maintenance", "amount": 620.0, "category": "Housing"},
            {"id": 2, "date": "2026-10-02", "description": "Property Taxes (Escrow reserve)", "amount": 850.0, "category": "Housing"},
            {"id": 3, "date": "2026-10-03", "description": "Utility Power & Water", "amount": 190.0, "category": "Utilities"},
            {"id": 4, "date": "2026-10-05", "description": "Whole Foods Organic Market", "amount": 340.0, "category": "Groceries"},
            {"id": 5, "date": "2026-10-08", "description": "Fine Dining & Wine Club", "amount": 290.0, "category": "Dining & Entertainment"},
            {"id": 6, "date": "2026-10-12", "description": "Symphony & Theater Tickets", "amount": 220.0, "category": "Dining & Entertainment"},
            {"id": 7, "date": "2026-10-15", "description": "Health Club & Pilates", "amount": 180.0, "category": "Subscriptions"}
        ]
    }
}

def get_client_profile(client_id: str):
    """Retrieves client by ID, default to Alex Chen."""
    return CLIENT_PROFILES.get(client_id, CLIENT_PROFILES["alex_chen"])
