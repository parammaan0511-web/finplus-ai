"""
Unit and Integration Tests for FinPulse AI Core
"""

import unittest
from core.budgeting import analyze_transactions, categorize_transaction, build_tailored_budget_plan
from core.forecasting import run_monte_carlo_simulation, calculate_fire_metrics
from core.debt_planner import compare_debt_strategies, calculate_debt_payoff
from core.risk_profiler import get_risk_profile
from core.report_generator import generate_client_report
from core.advisor_engine import answer_financial_query
from core.mock_data import CLIENT_PROFILES, get_client_profile

class TestFinPulseCore(unittest.TestCase):

    def test_transaction_categorization(self):
        self.assertEqual(categorize_transaction("Trader Joe's groceries", 50.0), "Groceries")
        self.assertEqual(categorize_transaction("Whole Foods Market", 120.0), "Groceries")
        self.assertEqual(categorize_transaction("Netflix Subscription", 19.99), "Subscriptions")
        self.assertEqual(categorize_transaction("Chevron Gas Station", 45.0), "Transportation")
        self.assertEqual(categorize_transaction("Federal Student Loan", 250.0), "Debt Payments")

    def test_budget_analysis(self):
        client = get_client_profile("alex_chen")
        analysis = analyze_transactions(client["transactions"], client["monthly_net_income"])
        self.assertGreater(analysis["total_spent"], 0)
        self.assertIn("fifty_thirty_twenty", analysis)
        self.assertIn("needs", analysis["fifty_thirty_twenty"])
        self.assertIn("wants", analysis["fifty_thirty_twenty"])
        self.assertIn("savings", analysis["fifty_thirty_twenty"])
        self.assertGreater(len(analysis["subscriptions"]), 0)

    def test_monte_carlo_simulation(self):
        mc = run_monte_carlo_simulation(
            current_wealth=50000.0,
            monthly_contribution=1000.0,
            years_to_retirement=20,
            years_in_retirement=30,
            annual_retirement_spend=60000.0,
            num_simulations=200
        )
        self.assertIn("probability_of_success", mc)
        self.assertGreaterEqual(mc["probability_of_success"], 0)
        self.assertLessEqual(mc["probability_of_success"], 100)
        self.assertEqual(len(mc["p50_trajectory"]), 51)
        self.assertGreater(mc["median_at_retirement"], 50000)

    def test_fire_metrics(self):
        fire = calculate_fire_metrics(
            annual_expenses=60000.0,
            current_net_worth=300000.0,
            annual_savings=24000.0
        )
        self.assertEqual(fire["fire_target"], 1500000.0) # 60000 / 0.04
        self.assertGreater(fire["current_progress_pct"], 0)
        self.assertLessEqual(fire["current_progress_pct"], 100)

    def test_debt_avalanche_vs_snowball(self):
        debts = [
            {"name": "High APR Card", "balance": 4000.0, "apr": 24.0, "min_payment": 100.0},
            {"name": "Low APR Loan", "balance": 15000.0, "apr": 5.0, "min_payment": 200.0}
        ]
        result = compare_debt_strategies(debts, extra_monthly_payment=300.0)
        # Avalanche should pay less or equal total interest than snowball
        self.assertLessEqual(result["avalanche"]["total_interest_paid"], result["snowball"]["total_interest_paid"])
        self.assertGreaterEqual(result["interest_saved_vs_minimums"], 0)

    def test_report_generation(self):
        client = get_client_profile("alex_chen")
        report = generate_client_report(client)
        self.assertIn("scorecard", report)
        self.assertIn("overall_health", report["scorecard"])
        self.assertIn("action_items", report)
        self.assertGreater(len(report["action_items"]), 0)

    def test_advisor_chatbot_intents(self):
        client = get_client_profile("alex_chen")
        
        # Test 1: Health snapshot
        res1 = answer_financial_query("How am I doing financially?", client)
        self.assertIn("Financial Health Snapshot", res1["response"])
        
        # Test 2: Home purchase
        res2 = answer_financial_query("Can I afford to buy a $600k house?", client)
        self.assertIn("Home Affordability Assessment", res2["response"])
        self.assertIn("Target Home Price", res2["key_metrics"])
        
        # Test 3: Retirement
        res3 = answer_financial_query("Can I retire at 55?", client)
        self.assertIn("Retirement & FIRE Analysis", res3["response"])
        
        # Test 4: Debt query
        res4 = answer_financial_query("What debt should I pay off first?", client)
        self.assertIn("Avalanche", res4["response"])
        
        # Test 5: CFP Flagging
        res5 = answer_financial_query("How do I set up an irrevocable trust fund for estate tax?", client)
        self.assertTrue(res5["needs_human_cfp"])

    def test_tailored_budget_high_fixed_costs(self):
        # 67% scenario: 20,000 out of 30,000
        plan = build_tailored_budget_plan(30000.0, 20000.0)
        self.assertFalse(plan["fits_standard_50_30_20"])
        self.assertEqual(plan["fixed_pct"], 66.7)
        self.assertEqual(plan["remaining_amount"], 10000.0)
        self.assertIn("50/30/20 rule will not fit", plan["rule_acknowledgment"])
        
        # Tailored allocation for remaining $10,000
        alloc = plan["tailored_allocation"]
        self.assertEqual(alloc["savings_debt"]["amount"], 6000.0)
        self.assertEqual(alloc["discretionary_wants"]["amount"], 4000.0)
        self.assertEqual(plan["emergency_3mo_target"], 60000.0)
        self.assertEqual(plan["months_to_emergency_fund"], 10.0)
        self.assertEqual(len(plan["action_steps"]), 3)

    def test_advisor_behavior_guidelines(self):
        client = get_client_profile("alex_chen")
        query = "My fixed costs take up 67% of income ($20,000 out of $30,000). What should I do?"
        res = answer_financial_query(query, client)
        resp_text = res["response"]

        # Rule 1 & 4: Concrete numbers, simple math, acknowledge 50/30/20 mismatch & tailored remaining plan
        self.assertIn("$20,000", resp_text)
        self.assertIn("$30,000", resp_text)
        self.assertIn("50/30/20", resp_text)
        self.assertIn("won't fit", resp_text)
        self.assertIn("$10,000", resp_text)
        self.assertIn("$6,000", resp_text)
        self.assertIn("$4,000", resp_text)

        # Rule 2: Do NOT repeat user question back word-for-word
        self.assertNotIn(f"Thank you for your question: *'{query}'*", resp_text)
        self.assertNotIn("What should I do?", resp_text)

        # Rule 3: Do NOT recite generic capability list
        self.assertNotIn("As your **AI Financial Advisor**, I can assist you with:", resp_text)

        # Rule 5: End with 1 concise, relevant follow-up question
        self.assertTrue(resp_text.strip().endswith("?"))

        # Capability check: only recite when explicitly asked
        cap_res = answer_financial_query("What can you do?", client)
        self.assertIn("capabilities", cap_res["response"].lower())

if __name__ == "__main__":
    unittest.main()
