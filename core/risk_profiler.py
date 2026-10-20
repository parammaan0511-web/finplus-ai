"""
Risk Profiling & Asset Allocation Optimizer
Maps investor risk tolerance to optimal diversified portfolios and capital market return assumptions.
"""

from typing import Dict, Any

RISK_MODELS = {
    "Conservative": {
        "score": 1,
        "description": "Priority on capital preservation with minimal drawdown tolerance.",
        "expected_return": 0.048, # 4.8%
        "volatility": 0.065,      # 6.5%
        "allocation": {
            "US Equities": 20,
            "International Equities": 10,
            "Fixed Income / Bonds": 55,
            "Cash & Equivalents": 15
        }
    },
    "Moderately Conservative": {
        "score": 2,
        "description": "Steady income generation with modest capital appreciation.",
        "expected_return": 0.058,
        "volatility": 0.09,
        "allocation": {
            "US Equities": 30,
            "International Equities": 15,
            "Fixed Income / Bonds": 45,
            "Cash & Equivalents": 10
        }
    },
    "Moderate": {
        "score": 3,
        "description": "Balanced growth and preservation, classic 60/40 balanced benchmark.",
        "expected_return": 0.070,
        "volatility": 0.12,
        "allocation": {
            "US Equities": 45,
            "International Equities": 20,
            "Fixed Income / Bonds": 30,
            "Cash & Equivalents": 5
        }
    },
    "Growth": {
        "score": 4,
        "description": "Long-term wealth accumulation, willing to absorb short-term equity volatility.",
        "expected_return": 0.082,
        "volatility": 0.155,
        "allocation": {
            "US Equities": 55,
            "International Equities": 25,
            "Fixed Income / Bonds": 15,
            "Cash & Equivalents": 5
        }
    },
    "Aggressive Growth": {
        "score": 5,
        "description": "Maximum compounding power, high equity exposure, long investment horizon.",
        "expected_return": 0.092,
        "volatility": 0.185,
        "allocation": {
            "US Equities": 65,
            "International Equities": 25,
            "Fixed Income / Bonds": 5,
            "Cash & Equivalents": 5
        }
    }
}

def get_risk_profile(profile_name: str) -> Dict[str, Any]:
    """Returns risk profile model configuration."""
    return RISK_MODELS.get(profile_name, RISK_MODELS["Moderate"])
