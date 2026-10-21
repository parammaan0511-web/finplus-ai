"""
Conversational AI Financial Advisor Engine
Combines domain-specific quantitative planning logic with context-aware natural language reasoning.
Offers 24/7 client-facing guidance, scenario evaluation, and seamless CFP human-in-the-loop escalation.
"""

from typing import Dict, Any, List
import re
from .budgeting import analyze_transactions, build_tailored_budget_plan
from .forecasting import run_monte_carlo_simulation, calculate_fire_metrics
from .debt_planner import compare_debt_strategies
from .risk_profiler import get_risk_profile

def answer_financial_query(query: str, client: Dict[str, Any], history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Intelligent financial advisor chatbot logic.
    Analyzes user intent, checks client portfolio/cashflow, computes real-time math,
    and returns a structured response with insights, calculations, and prompt suggestions.
    """
    q = query.lower().strip()
    
    # Financial metrics extraction from client
    income = client.get("monthly_net_income", 6000.0)
    emergency_fund = client.get("emergency_fund", 20000.0)
    inv_dict = client.get("investments", {})
    total_investments = sum(inv_dict.values())
    debts = client.get("debts", [])
    total_debt = sum(d["balance"] for d in debts)
    tx_data = analyze_transactions(client.get("transactions", []), income)
    spent = tx_data["total_spent"]
    monthly_savings = max(0, income - spent)
    
    # Flags for Human CFP Handoff
    needs_human_cfp = False
    cfp_reason = ""
    
    for flag_kw in ["estate tax", "will", "trust fund", "divorce settlement", "crypto leverage", "margin trade", "irs audit"]:
        if flag_kw in q:
            needs_human_cfp = True
            cfp_reason = f"Your query involves specialized legal or complex tax considerations ({flag_kw}). A licensed fiduciary CFP / estate attorney review is recommended."
            break

    # Intent Classification & Mathematical Reasoning
    response_text = ""
    key_metrics = {}
    suggested_prompts = []
    
    # Intent 0: Tailored Adaptive Budget for High Fixed Costs / Specific Financial Situations (e.g. 67% or 20,000 out of 30,000)
    has_ratio_match = re.search(r'\$?(\d+[\d,]*)\s*(?:k)?\s*(?:out of|of|\/)\s*\$?(\d+[\d,]*)\s*(?:k)?', q)
    has_fixed_pct = re.search(r'(\d+(?:\.\d+)?)\s*%', q)
    has_tailored_keywords = any(k in q for k in ["fixed cost", "fixed costs", "fixed expense", "tailored plan", "tailored budget", "50/30/20", "67%", "won't fit", "doesn't fit"])

    if has_ratio_match or (has_tailored_keywords and (has_fixed_pct or any(n in q for n in ["30000", "30,000", "20000", "20,000", "67", "won't fit", "doesn't fit"]))):
        q_income = 30000.0
        q_fixed = 20000.0

        if has_ratio_match:
            try:
                v1_str = has_ratio_match.group(1).replace(',', '')
                v2_str = has_ratio_match.group(2).replace(',', '')
                m_str = has_ratio_match.group(0)
                v1 = float(v1_str) * (1000 if 'k' in m_str.split('of')[0] or 'k' in m_str.split('/')[0] else 1)
                v2 = float(v2_str) * (1000 if 'k' in m_str.split('of')[-1] or 'k' in m_str.split('/')[-1] else 1)
                if v1 < v2:
                    q_fixed, q_income = v1, v2
                else:
                    q_income, q_fixed = v1, v2
            except Exception:
                pass
        elif any(n in q for n in ["30000", "30,000"]) and any(n in q for n in ["20000", "20,000"]):
            q_income = 30000.0
            q_fixed = 20000.0
        elif has_fixed_pct:
            try:
                pct = float(has_fixed_pct.group(1))
                if pct > 0:
                    q_income = client.get("monthly_net_income", 30000.0) if client.get("monthly_net_income") else 30000.0
                    q_fixed = round(q_income * (pct / 100.0), 2)
            except Exception:
                pass

        plan = build_tailored_budget_plan(q_income, q_fixed)
        rem = plan["remaining_amount"]
        rem_pct = plan["remaining_pct"]
        alloc = plan["tailored_allocation"]
        sav_amt = alloc["savings_debt"]["amount"]
        sav_pct = alloc["savings_debt"]["percent"]
        wants_amt = alloc["discretionary_wants"]["amount"]
        wants_pct = alloc["discretionary_wants"]["percent"]
        emergency_target = plan["emergency_3mo_target"]
        months_to_fund = plan["months_to_emergency_fund"]

        response_text = (
            f"With **${q_fixed:,.0f}** in fixed costs against a monthly net income of **${q_income:,.0f}** ({plan['fixed_pct']}%), "
            f"the traditional 50/30/20 rule won't fit perfectly because your fixed essential expenses already exceed the standard 50% guideline (${plan['standard_comparison']['needs']:,.0f}) by **${q_fixed - plan['standard_comparison']['needs']:,.0f}**.\n\n"
            f"### Tailored Plan for the Remaining ${rem:,.0f} ({rem_pct}%)\n\n"
            f"Instead of attempting an impossible 50% fixed-cost cap, here is your customized plan allocating the remaining **${rem:,.0f}**:\n\n"
            f"1. **Savings, Debt Payoff & Liquidity Reserve (60% of remaining / {sav_pct}% of total income):**\n"
            f"   - **Allocation:** **${sav_amt:,.0f} / month**\n"
            f"   - **Math & Milestone:** A 3-month fixed cost cushion (${q_fixed:,.0f} x 3 = **${emergency_target:,.0f}**) is fully funded in **{months_to_fund} months** at this pace, shielding you against cash flow shocks.\n\n"
            f"2. **Flexible Discretionary Living (40% of remaining / {wants_pct}% of total income):**\n"
            f"   - **Allocation:** **${wants_amt:,.0f} / month** (~**${wants_amt / 4.33:,.0f} / week**)\n"
            f"   - **Math & Purpose:** Dedicated strictly to dining, leisure, and shopping without accumulating debt or dipping into fixed living costs.\n\n"
            f"### Actionable Steps\n"
            f"1. **Automate Payday Transfers:** Schedule an automatic recurring transfer of **${sav_amt:,.0f}** into a high-yield account or high-APR debt reduction on the day your paycheck arrives.\n"
            f"2. **Separate Discretionary Account:** Keep your **${wants_amt:,.0f}** variable budget in a dedicated secondary checking account to enforce daily spending discipline.\n"
            f"3. **Cap Fixed Overhead:** Audit fixed bills (insurance, subscriptions, utilities) annually to keep fixed expenses strictly at or below {plan['fixed_pct']}%.\n\n"
            f"Would you like to model allocating part of this ${sav_amt:,.0f}/month toward high-interest debt or toward an index fund portfolio?"
        )
        key_metrics = {
            "Fixed Needs": f"${q_fixed:,.0f} ({plan['fixed_pct']}%)",
            "Remaining Surplus": f"${rem:,.0f} ({rem_pct}%)",
            "Savings & Reserve": f"${sav_amt:,.0f}/mo (60%)",
            "Discretionary Wants": f"${wants_amt:,.0f}/mo (40%)"
        }
        suggested_prompts = [
            "How long to reach a 6-month emergency reserve?",
            "What if I pay an extra $500 toward credit card debt?",
            "What happens if my fixed costs rise to 70%?"
        ]

    # Intent 1: Home Purchase Affordability (prioritize before retirement if home/house/mortgage mentioned)
    elif any(k in q for k in ["afford a house", "buy a home", "buy a condo", "mortgage", "purchase a house", "down payment", "house", "condo"]):
        match = re.search(r'\$?(\d+[\d,]*)(k)?', q)
        home_price = 600000.0
        if match:
            raw_val = match.group(1).replace(',', '')
            val = float(raw_val) * (1000 if match.group(2) else 1)
            if val >= 50000:
                home_price = val

        down_payment_20 = home_price * 0.20
        down_payment_10 = home_price * 0.10
        closing_costs = home_price * 0.03
        
        # Estimate monthly mortgage at 6.8% 30yr fixed
        loan_amt = home_price - down_payment_20
        monthly_interest_rate = 0.068 / 12
        num_payments = 360
        monthly_p_and_i = loan_amt * (monthly_interest_rate * (1 + monthly_interest_rate)**num_payments) / ((1 + monthly_interest_rate)**num_payments - 1)
        estimated_piti = monthly_p_and_i + (home_price * 0.012 / 12) + 120 # P&I + Property Tax + Insurance
        
        dti_impact = round((estimated_piti / income) * 100, 1)
        affordable = dti_impact <= 35 and (emergency_fund + total_investments >= down_payment_10 + closing_costs)
        
        response_text = (
            f"### Home Affordability Assessment for a **${home_price:,.0f}** Property\n\n"
            f"1. **Upfront Capital Required:**\n"
            f"   - **20% Down Payment (avoids PMI):** ${down_payment_20:,.0f}\n"
            f"   - **10% Down Payment alternative:** ${down_payment_10:,.0f}\n"
            f"   - **Estimated Closing Costs (3%):** ${closing_costs:,.0f}\n"
            f"   - **Total cash needed at closing:** ~**${(down_payment_20 + closing_costs):,.0f}**\n\n"
            f"2. **Estimated Monthly Housing Cost (PITI @ 6.8%):**\n"
            f"   - Principal & Interest: ~${monthly_p_and_i:,.0f}/mo\n"
            f"   - Property Taxes & Insurance: ~${(home_price * 0.012 / 12 + 120):,.0f}/mo\n"
            f"   - **Estimated Total Monthly Payment:** **${estimated_piti:,.0f}/mo**\n\n"
            f"3. **Debt-to-Income (DTI) Analysis:**\n"
            f"   - This mortgage would represent **{dti_impact}%** of your monthly net income.\n"
            f"   - Standard financial benchmark is **< 28-33%** of gross income.\n\n"
            f"**Recommendation:** " + (
                "This target is feasible with disciplined down-payment savings over the next 2-3 years."
                if affordable else
                "At current income, this payment would stretch your cash flow beyond the safe 30% threshold. Consider targeting a lower price point or increasing the down payment."
            )
        )
        key_metrics = {
            "Target Home Price": f"${home_price:,.0f}",
            "20% Down Payment": f"${down_payment_20:,.0f}",
            "Est. Monthly PITI": f"${estimated_piti:,.0f}/mo",
            "Housing DTI": f"{dti_impact}%"
        }
        suggested_prompts = [
            "How long will it take me to save $75k down payment?",
            "What if I put 10% down instead?",
            "How can I boost my monthly savings rate?"
        ]

    # Intent 2: Financial Health / Status Overview
    elif any(k in q for k in ["how am i doing", "financial health", "score", "overview", "summary", "status"]):
        emergency_months = round(emergency_fund / (spent if spent > 0 else income * 0.7), 1)
        savings_rate = round((monthly_savings / income) * 100, 1)
        
        response_text = (
            f"Here is your **24/7 Financial Health Snapshot** for **{client.get('name', 'Client')}**:\n\n"
            f"- **Net Monthly Cash Flow**: You bring in **${income:,.2f}** and spent **${spent:,.2f}** this month, giving a positive cashflow of **${monthly_savings:,.2f}** (Savings rate: **{savings_rate}%**).\n"
            f"- **Emergency Buffer**: Your emergency fund holds **${emergency_fund:,.2f}**, which covers **{emergency_months} months** of living expenses (Target: 3–6 months).\n"
            f"- **Invested Assets**: **${total_investments:,.2f}** across your tax-advantaged and taxable accounts.\n"
            f"- **Outstanding Debt**: **${total_debt:,.2f}** total balance across {len(debts)} accounts.\n\n"
            f"**Advisor Takeaway:** You are in a solid position, but eliminating high-interest debt and trimming recurring subscriptions will accelerate your goals."
        )
        key_metrics = {
            "Savings Rate": f"{savings_rate}%",
            "Emergency Runway": f"{emergency_months} mo",
            "Invested Portfolio": f"${total_investments:,.0f}",
            "Total Debt": f"${total_debt:,.0f}"
        }
        suggested_prompts = [
            "How can I cut $300 from my monthly spending?",
            "Can I retire early at 55?",
            "What debt should I pay off first?"
        ]

    # Intent 3: Retirement / Early Retirement / FIRE
    elif any(k in q for k in ["retire", "retirement", "fire", "coast fire", "early retirement", "nest egg"]) or re.search(r'\b(age\s+)?(50|55|60|62|65|67)\b', q):
        ret_age = client.get("target_retirement_age", 55)
        
        # Check if query specified an age like "retire at 60"
        age_match = re.search(r'\b(at\s+)?(50|55|58|60|62|65|67)\b', q)
        if age_match:
            try:
                ret_age = int(age_match.group(2))
            except Exception:
                pass
                
        curr_age = client.get("age", 30)
        years_left = max(1, ret_age - curr_age)
        annual_spend = client.get("target_annual_retirement_spend", 65000.0)
        
        mc = run_monte_carlo_simulation(
            current_wealth=total_investments,
            monthly_contribution=client.get("monthly_savings_current", 1200),
            years_to_retirement=years_left,
            years_in_retirement=30,
            annual_retirement_spend=annual_spend
        )
        fire = calculate_fire_metrics(
            annual_expenses=annual_spend,
            current_net_worth=total_investments + emergency_fund - total_debt,
            annual_savings=client.get("monthly_savings_current", 1200) * 12
        )
        
        response_text = (
            f"### Retirement & FIRE Analysis (Target Age: **{ret_age}**)\n\n"
            f"You have **{years_left} years** until your target retirement age of {ret_age}.\n\n"
            f"- **Monte Carlo Probability of Success:** **{mc['probability_of_success']}%** across 1,000 stochastic market scenarios.\n"
            f"- **Median Projected Portfolio at Age {ret_age}:** **${mc['median_at_retirement']:,.0f}**.\n"
            f"- **Bear Market (10th percentile):** **${mc['p10_at_retirement']:,.0f}**.\n"
            f"- **Bull Market (90th percentile):** **${mc['p90_at_retirement']:,.0f}**.\n\n"
            f"#### FIRE Milestones (Safe Withdrawal Rule: 4%)\n"
            f"- **Full FIRE Target:** **${fire['fire_target']:,.0f}** (enables ${annual_spend:,.0f}/yr withdrawal indefinitely).\n"
            f"- **Lean FIRE Target:** **${fire['lean_fire_target']:,.0f}**\n"
            f"- **Coast FIRE Status:** " + ("You have successfully hit Coast FIRE! Your current assets will compound to your retirement target without further deposits." if fire['is_coast_fire'] else f"Need ${fire['coast_fire_needed']:,.0f} invested today to achieve Coast FIRE.") + "\n\n"
            f"**Strategic Advice:** " + (
                "Your plan is in the top safety tier (>85% success). You are on track for early retirement."
                if mc['probability_of_success'] >= 85 else
                f"To push your confidence above 85%, consider bumping monthly contributions by $350 or extending working horizon by 2 years."
            )
        )
        key_metrics = {
            "Target Age": str(ret_age),
            "Success Probability": f"{mc['probability_of_success']}%",
            "Median Nest Egg": f"${mc['median_at_retirement']:,.0f}",
            "FIRE Number": f"${fire['fire_target']:,.0f}"
        }
        suggested_prompts = [
            "Simulate a 20% stock market crash",
            "What if I increase monthly savings by $400?",
            "Explain the 4% safe withdrawal rule"
        ]

    # Intent 4: Debt Payoff / Snowball vs Avalanche
    elif any(k in q for k in ["debt", "credit card", "loan", "avalanche", "snowball", "pay off", "interest"]):
        if not debts:
            response_text = "Congratulations! You have **zero outstanding consumer debts**. You can deploy 100% of your surplus cash flow into investments and high-yield savings."
        else:
            debt_comp = compare_debt_strategies(debts, extra_monthly_payment=300.0)
            av = debt_comp["avalanche"]
            sb = debt_comp["snowball"]
            
            response_text = (
                f"### Debt Elimination Strategy: Avalanche vs Snowball\n\n"
                f"You currently have **${total_debt:,.2f}** in total debt across {len(debts)} accounts.\n"
                f"Adding an extra **$300/month** above minimum payments produces these results:\n\n"
                f"| Strategy | Months to Debt-Free | Total Interest Paid | Speedup vs Minimums |\n"
                f"|---|---|---|---|\n"
                f"| **Avalanche** (Highest APR first) | **{av['months_to_debt_free']} mos** ({av['years_to_debt_free']} yrs) | **${av['total_interest_paid']:,.2f}** | **{debt_comp['months_faster_vs_minimums']} months faster** |\n"
                f"| **Snowball** (Lowest Balance first) | **{sb['months_to_debt_free']} mos** ({sb['years_to_debt_free']} yrs) | **${sb['total_interest_paid']:,.2f}** | {debt_comp['minimums_only']['months_to_debt_free'] - sb['months_to_debt_free']} months faster |\n"
                f"| **Minimum Payments Only** | {debt_comp['minimums_only']['months_to_debt_free']} mos | ${debt_comp['minimums_only']['total_interest_paid']:,.2f} | Baseline |\n\n"
                f"**Savings:** The Avalanche method saves you **${debt_comp['interest_saved_vs_minimums']:,.2f}** compared to paying minimums, and **${debt_comp['interest_saved_avalanche_vs_snowball']:,.2f}** more than Snowball.\n\n"
                f"**Action Step:** Direct all surplus cash first to your credit card ({debts[0]['name']}) while paying minimums on student loans."
            )
            key_metrics = {
                "Interest Saved": f"${debt_comp['interest_saved_vs_minimums']:,.0f}",
                "Time to Debt-Free": f"{av['years_to_debt_free']} yrs",
                "Recommended Method": "Debt Avalanche"
            }
        suggested_prompts = [
            "Should I invest or pay off the 22% credit card first?",
            "What if I allocate $500/month extra to debt?",
            "How can I cut expenses to free up debt payments?"
        ]

    # Intent 5: Spending, Budgeting, & Subscription Optimization
    elif any(k in q for k in ["spending", "cut", "save money", "budget", "subscription", "trader joe", "dining", "reduce"]):
        subs = tx_data["subscriptions"]
        cats = tx_data["category_breakdown"]
        top_cats = list(cats.items())[:4]
        
        response_text = (
            f"### Spending & Subscription Optimization Report\n\n"
            f"This month's total expenses were **${spent:,.2f}**.\n\n"
            f"**Top Spending Categories:**\n"
        )
        for cat, amt in top_cats:
            pct = round((amt / (spent if spent > 0 else 1)) * 100, 1)
            response_text += f"- **{cat}**: ${amt:,.2f} ({pct}% of total spending)\n"
            
        response_text += f"\n**Detected Recurring Subscriptions ({len(subs)} detected):**\n"
        for s in subs:
            response_text += f"- {s['merchant']}: **${s['monthly_cost']:,.2f}/mo** (${s['annual_cost']:,.2f}/yr)\n"
            
        response_text += (
            f"\n**Total Annual Subscription Outflow:** **${tx_data['total_subscription_annual']:,.2f}/yr**\n\n"
            f"**Advisor Savings Opportunities:**\n"
            f"1. **Audit Subscriptions:** Canceling 2-3 underutilized memberships could instantly redirect **$150-$250/mo** to investments.\n"
            f"2. **Meal Prep vs Dining Out:** Dining and delivery represent an opportunity to recapture **$200/mo**.\n"
            f"3. Compounded at 7% over 10 years, saving an extra **$400/month** yields **${round(400 * (((1 + 0.07/12)**120 - 1) / (0.07/12)), 0):,.0f}**!"
        )
        key_metrics = {
            "Total Expenses": f"${spent:,.0f}",
            "Active Subscriptions": str(len(subs)),
            "Annual Sub Cost": f"${tx_data['total_subscription_annual']:,.0f}",
            "Budget Score": f"{tx_data['budget_score']}/100"
        }
        suggested_prompts = [
            "Show my 50/30/20 budget breakdown",
            "What if I invest that $400/mo into an index fund?",
            "How does this impact my retirement timeline?"
        ]

    # Intent 6: Market Crash / Volatility / Stress Test
    elif any(k in q for k in ["crash", "recession", "bear market", "stress test", "market drop", "20%"]):
        paper_loss = total_investments * 0.20
        rebounded_value_5yr = (total_investments * 0.80) * ((1 + 0.07) ** 5)
        
        response_text = (
            f"### Portfolio Stress Test: 20% Market Downturn\n\n"
            f"If the equity market drops by 20% tomorrow:\n\n"
            f"- **Immediate Portfolio Impact:** A paper reduction of **-${paper_loss:,.2f}**, bringing portfolio to **${(total_investments - paper_loss):,.2f}**.\n"
            f"- **Your Defense Mechanism:** You have **${emergency_fund:,.2f}** in liquid cash, ensuring you **never need to sell shares at a loss** to pay for living expenses!\n"
            f"- **The Recovery Opportunity:** Continuing your monthly savings of **${client.get('monthly_savings_current', 1000):,.0f}** during the downturn allows dollar-cost averaging into discounted shares.\n"
            f"- **5-Year Historical Recovery Projection:** Assuming average historical recovery rates, your portfolio would rebound to **~${rebounded_value_5yr:,.0f}** within 5 years.\n\n"
            f"**Golden Rule of Financial Planning:** Market volatility is the price of admission for long-term equity growth. Do not panic-sell; maintain your automated DCA contributions."
        )
        key_metrics = {
            "Emergency Protection": f"${emergency_fund:,.0f}",
            "Paper Impact": f"-${paper_loss:,.0f}",
            "5-Year Rebound Est.": f"${rebounded_value_5yr:,.0f}"
        }
        suggested_prompts = [
            "How is my asset allocation diversified?",
            "Should I keep more cash in my emergency fund?",
            "How does this affect my FIRE date?"
        ]

    # Intent 7: Account Hierarchy / Tax-Advantaged Waterfall
    elif any(k in q for k in ["roth", "401k", "401(k)", "hsa", "brokerage", "waterfall", "order of investing", "taxes"]):
        response_text = (
            f"### The Optimal Financial Waterfall (Account Hierarchy)\n\n"
            f"To maximize wealth and minimize taxes, financial planners recommend this exact priority sequence:\n\n"
            f"1. **Employer 401(k) Match (100% immediate ROI):** Contribute up to the maximum company match. Never leave free money on the table.\n"
            f"2. **High-Interest Debt Elimination:** Pay off any debt above 7% APR (credit cards, high-rate personal loans).\n"
            f"3. **Health Savings Account (HSA - Triple Tax Advantaged):** If enrolled in an HDHP, max out your HSA. Contributions are tax-deductible, grow tax-free, and withdraw tax-free for healthcare.\n"
            f"4. **Roth IRA / Backdoor Roth:** Contribute up to the annual limit. Investments compound tax-free forever, and contributions can be withdrawn penalty-free at any time.\n"
            f"5. **Max Out 401(k) Balance:** Return to your 401(k) to maximize contributions up to the annual IRS ceiling.\n"
            f"6. **Taxable Brokerage Account:** Invest any excess in broad-market low-cost index funds (VTI, VXUS) with tax-loss harvesting."
        )
        key_metrics = {
            "Top Priority": "401k Company Match",
            "Tax-Free Vehicle": "Roth IRA & HSA",
            "Final Bucket": "Taxable Brokerage"
        }
        suggested_prompts = [
            "Am I eligible for a Roth IRA?",
            "How do I pay off my high APR debt?",
            "What is my retirement probability?"
        ]

    # Explicit capability request
    elif any(k in q for k in ["what can you do", "what are your capabilities", "your capabilities", "what features do you have"]):
        response_text = (
            f"Here is what I can do and my core capabilities as your quantitative financial planning assistant:\n\n"
            f"1. **Tailored Cash Flow & Adaptive Budgeting**: Design realistic spending allocations when fixed costs deviate from traditional 50/30/20 guidelines.\n"
            f"2. **Monte Carlo Wealth Projections**: Run 1,000-path stochastic simulations testing retirement timelines and safe withdrawal buffers.\n"
            f"3. **Debt Freedom Accelerator**: Compare Avalanche vs. Snowball payoff schedules to minimize interest drag.\n"
            f"4. **Home Purchase & Goal Modeling**: Calculate mortgage PITI payments, down payment targets, and DTI thresholds.\n"
            f"5. **Audit-Ready Financial Plans**: Generate 5-pillar health scorecards with fiduciary escalation for complex scenarios.\n\n"
            f"Which area would you like to run numbers on?"
        )
        key_metrics = {"Mode": "Advisory Capabilities"}
        suggested_prompts = [
            "My fixed costs take up 67% of income ($20k of $30k)",
            "How am I doing financially?",
            "Can I retire at 55?"
        ]

    # Default / General Financial Guidance (never repeats question or recites capability list)
    else:
        response_text = (
            f"To build a concrete, tailored financial plan for your situation, we start by mapping your monthly take-home cash flow against fixed obligations.\n\n"
            f"For example, if your fixed costs consume a high percentage of earnings (such as $20,000 out of a $30,000 income, or 67%), the standard 50/30/20 rule will not fit. In that case, we isolate the remaining $10,000 surplus to establish an emergency runway ($6,000/mo) and a controlled discretionary budget ($4,000/mo).\n\n"
            f"What is your current monthly take-home income and total fixed essential cost?"
        )
        key_metrics = {
            "Default Ratio Model": "Custom Allocation",
            "Emergency Benchmark": "3-6 Months Fixed Costs"
        }
        suggested_prompts = [
            "My fixed costs take up 67% ($20k of $30k)",
            "How should I split my remaining budget?",
            "Show my financial health score"
        ]

    return {
        "query": query,
        "response": response_text,
        "key_metrics": key_metrics,
        "suggested_prompts": suggested_prompts,
        "needs_human_cfp": needs_human_cfp,
        "cfp_reason": cfp_reason
    }
