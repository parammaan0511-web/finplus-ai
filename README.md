# FinPulse AI — Autonomous Financial Planning & Advisor Intelligence Suite

FinPulse AI is a comprehensive, production-grade financial planning platform designed to bridge the gap between **Certified Financial Planner (CFP) automation** and **24/7 accessible client-facing advisory**.

---

## 🌟 Dual-Core Architecture

### 1. Advisor Automation & Copilot Studio
* **Automated Transaction Categorization**: NLP & priority-rule classification sorting raw transactions into Housing, Utilities, Groceries, Dining, Subscriptions, and Debt Service.
* **Recurring Subscription Hunter**: Detects recurring recurring expenses and auto-renewals, quantifying total annual drag and immediate savings potential.
* **50/30/20 Budget Health Score**: Evaluates fixed needs ($\le 50\%$), discretionary wants ($\le 30\%$), and savings ($\ge 20\%$) with automated health scoring ($0-100$).
* **1-Click Executive Financial Plan Generator**: Instantly compiles audit-ready, client-facing PDF/print reviews with 5-pillar health scorecards, balance sheet reconciliations, and prioritized action steps.

### 2. 24/7 Customer-Facing AI Financial Advisor
* **Conversational Financial Intelligence**: Real-time natural language answers grounded in actual client balance sheets, cashflows, and tax brackets.
* **Major Life Goal Simulators**:
  * **Home Affordability**: Calculates 20% vs 10% down payments, closing costs, PITI mortgage payments, and front/back-end DTI thresholds.
  * **Retirement & FIRE Projections**: Computes Coast FIRE, Lean FIRE, Full FIRE (4% safe withdrawal rule), and projected retirement milestones.
  * **Stress Testing**: Simulates 20% equity drawdowns and tests emergency liquidity buffers to prevent panic selling.
  * **Account Hierarchy (Waterfall)**: Guides clients through 401(k) employer matches, high-APR debt payoff, HSAs, Roth IRAs, and taxable brokerage accounts.
* **Human-in-the-Loop CFP Escalation**: Automatically identifies complex legal, trust, or estate tax scenarios and provides a 1-click dossier handoff to a licensed fiduciary advisor.

### 3. Quantitative Financial Engine
* **Monte Carlo Stochastic Engine**: Simulates 1,000 randomized market trajectories incorporating Sequence of Returns Risk (SRR), calculating confidence percentiles ($90^{\text{th}}$ Bull, $50^{\text{th}}$ Median, $10^{\text{th}}$ Bear) and probability of plan success.
* **Debt Freedom Accelerator**: Amortization engine contrasting Debt Avalanche (highest APR first) versus Debt Snowball (lowest balance first), calculating months saved and exact dollar interest saved against minimum payments.

---

## 📁 Project Structure

```
finpulse_ai/
├── core/
│   ├── __init__.py
│   ├── budgeting.py         # Categorization, subscription hunter, 50/30/20 breakdown
│   ├── forecasting.py       # Monte Carlo 1,000-path stochastic engine & FIRE metrics
│   ├── debt_planner.py      # Avalanche vs Snowball payoff algorithm
│   ├── risk_profiler.py     # Capital market models & asset allocation
│   ├── report_generator.py  # 1-Click executive PDF/Print report generator
│   ├── advisor_engine.py    # Natural language financial intelligence & CFP routing
│   └── mock_data.py         # Preloaded client personas (Early tech, Family, Pre-retiree)
├── static/
│   ├── index.html           # Modern responsive dashboard & chatbot UI
│   ├── app.js               # Reactive frontend logic, Chart.js, live chat
│   └── style.css            # Dark/light fintech theme with print media styling
├── tests/
│   └── test_core.py         # Unit & integration test suite
├── app.py                   # FastAPI application & REST endpoints
├── run.py                   # Launcher script with automatic port selection
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Platform
```bash
python run.py
```
Then open your browser to:
```
http://127.0.0.1:8000
```

### 3. Run Test Suite
```bash
python -m unittest tests/test_core.py
```

---

## 📊 Pre-Loaded Personas

1. **Alex Chen (28, Software Engineer)**: Early career, aggressive growth investor, tackling credit card debt while saving for a first condo down payment and aiming for Coast FIRE.
2. **The Millers (42 & 41, Mid-Career Family)**: Dual-income household balancing 529 college savings for 2 kids, a 30-year home mortgage, and retirement acceleration.
3. **Elena Rostova (59, Pre-Retiree Corporate Director)**: Wealth preserver de-risking equity allocations into bond tents and evaluating Sequence of Returns Risk for retirement at 63.
