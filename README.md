# SmartWealth: Goal-Based Wealth Technology Platform

SmartWealth is an explainable, goal-based wealth technology engine developed for **NiveshNow**. It transforms investor profiles and product catalogs into suitable, cost-aware investment plans without relying on black-box predictions.

---

## Key Features & Core Engines

* **Data Ingestion & Guardrail Engine (`data_validator.py`)**: Validates missing or malformed profile fields, enforces minimum numeric bounds, flags emergency fund runway deficiencies ($< 3$ months), and catches horizon-risk mismatches.
* **Constrained SLSQP Optimization Engine (`portfolio_optimizer.py`)**: Formulates allocation as a convex optimization problem in `scipy.optimize`. Enforces single-product diversification ($\le 40\%$), product lock-in constraints against goal horizons, weighted risk caps ($\le \text{Risk Tolerance} + 0.25$), and regulatory horizon limits. Includes an automatic safe fallback to liquid cash reserves if constraints conflict.
* **Future Value & Goal Gap Engine (`goal_projector.py`)**: Computes discrete monthly compounding future values across conservative ($-3\%$), base, and optimistic ($+3\%$) return bands. Calculates exact goal shortfalls in INR and derives actionable adjustments for monthly SIP increases ($\Delta S$) or horizon extensions ($\Delta n$).
* **Explainability & Cost Engine (`explainability_engine.py`)**: Reports weighted Total Expense Ratio (TER), annual product costs in INR, and liquidity coverage status. Generates plain-language compliance rationales detailing product choices, trade-offs, and reasons for excluding/capping high-yield alternatives.
* **What-If Scenario Simulator (`whatif_simulator.py`)**: Evaluates portfolio resilience under interactive stress tests, including a 15% market shock, a 20% SIP reduction, and a 25% goal horizon reduction.

---

## Repository Structure

```text
.
├── investor_profiles.csv          # Catalog of 12 synthetic investor personas
├── investment_products.csv        # Universe of 8 fictional product categories
├── synthetic_monthly_returns.csv  # 36 months of synthetic return time-series
├── data_validator.py              # Ingestion validation and emergency buffer checks
├── portfolio_optimizer.py         # SLSQP optimization engine & safe fallback logic
├── goal_projector.py              # Discrete compounding FV calculator & shortfall solver
├── explainability_engine.py       # Natural language compliance rationale generator
├── whatif_simulator.py            # Stress testing and scenario shock simulator
├── pipeline_runner.py             # CLI batch script generating submission CSVs
├── app.py                         # Interactive Streamlit dashboard
├── test_smartwealth.py            # Pytest suite with mandatory verification checks
├── requirements.txt               # Python package dependencies
└── README.md                      # Setup and execution guide
```

---

## Prerequisites & Dependencies

### System Requirements
* **Python**: `3.10` or higher
* **Package Manager**: `pip` or `conda`

### Package Dependencies (`requirements.txt`)
* `pandas>=2.0.0`
* `numpy>=1.24.0`
* `scipy>=1.10.0`
* `streamlit>=1.25.0`
* `pytest>=7.0.0`

---

## Setup & Installation

### 1. Clone or Download the Repository
Navigate to your project root folder:
```bash
cd "FinTech Dummy PS"
```

### 2. Create and Activate a Virtual Environment (Recommended)

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows (Command Prompt / PowerShell):
```cmd
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Usage Instructions

### 1. Execute Core Pipeline (CLI Batch Processing)
To run the end-to-end allocation engine across all personas in `investor_profiles.csv` and export output CSVs:
```bash
python pipeline_runner.py
```
**Output Artifacts Generated:**
* `allocation_recommendations.csv`: Granular product-level allocations (percentages and INR amounts) per investor.
* `summary_projections.csv`: Executive summary containing blended returns, weighted risk scores, expense ratios, annual costs, goal gap analysis, and liquidity statuses.

---

### 2. Launch Interactive Web Dashboard (Streamlit)
To review personas, visualize portfolio allocations, read compliance rationales, and simulate dynamic what-if scenarios:
```bash
streamlit run app.py
```
Once launched, open your web browser at `http://localhost:8501`.

---

### 3. Run Automated Pytest Suite
Execute the 5 automated verification checks (allocation sum to 100%, non-negative weights, lock-in vs horizon rule, risk cap compliance, and malformed profile handling):
```bash
pytest test_smartwealth.py -v
```

---

## Input & Output Specification

### Input Files

| File Name | Mandatory Columns | Description |
| :--- | :--- | :--- |
| `investor_profiles.csv` | `investor_id`, `goal_amount_inr`, `horizon_months`, `existing_investment_inr`, `monthly_sip_inr`, `risk_tolerance_score`, `emergency_fund_months` | Profile parameters and constraints per persona |
| `investment_products.csv` | `product_id`, `product_name`, `asset_class`, `risk_score`, `assumed_annual_return`, `annual_expense_ratio`, `liquidity_days`, `lock_in_months` | Product universe parameters and limits |

### Output Files Generated by Pipeline

| File Name | Key Metrics Covered |
| :--- | :--- |
| `allocation_recommendations.csv` | `investor_id`, `product_id`, `product_name`, `allocation_pct`, `allocated_amount_inr` |
| `summary_projections.csv` | `investor_id`, `blended_return_pct`, `weighted_risk_score`, `weighted_ter_pct`, `annual_cost_inr`, `fv_base_inr`, `goal_gap_inr`, `liquidity_status`, `fallback_used` |