import numpy as np
import pandas as pd
from scipy.optimize import minimize

class PortfolioOptimizer:
    def __init__(self, products_df):
        self.products = products_df.copy()

    def optimize(self, profile):
        """Calculates optimal asset weights maximizing returns subject to suitability guardrails."""
        horizon = profile['horizon_months']
        risk_tol = profile['risk_tolerance_score']

        # Determine Horizon Limits
        if horizon <= 36:
            max_high_risk = 0.10  # Risk 4-5
            min_low_risk = 0.70   # Risk 1-2
        elif 37 <= horizon <= 84:
            max_high_risk = 0.30
            min_low_risk = 0.45
        else:
            max_high_risk = 0.55
            min_low_risk = 0.25

        n = len(self.products)
        returns = self.products['assumed_annual_return'].values
        risks = self.products['risk_score'].values
        lock_ins = self.products['lock_in_months'].values

        high_risk_mask = (risks >= 4).astype(float)
        low_risk_mask = (risks <= 2).astype(float)

        def objective(w):
            return -np.dot(w, returns)

        # Bounds: Lock-in check & Single-product cap (<= 40%)
        bounds = []
        for i in range(n):
            if lock_ins[i] > horizon:
                bounds.append((0.0, 0.0))  # Exclude lock-in beyond horizon
            else:
                bounds.append((0.0, 0.40))  # Diversification cap: max 40%

        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},  # Weights sum to 1.0
            {'type': 'ineq', 'fun': lambda w: (risk_tol + 0.25) - np.dot(w, risks)},  # Weighted risk cap
            {'type': 'ineq', 'fun': lambda w: max_high_risk - np.dot(w, high_risk_mask)},  # High risk cap
            {'type': 'ineq', 'fun': lambda w: np.dot(w, low_risk_mask) - min_low_risk}   # Low risk floor
        ]

        x0 = np.ones(n) / n
        res = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)

        fallback_used = False
        if res.success and np.isclose(np.sum(res.x), 1.0, atol=1e-3):
            weights = np.round(res.x, 4)
            weights = weights / np.sum(weights)
        else:
            # Safer Fallback Mechanism: Allocate 100% to safest liquid asset
            fallback_used = True
            weights = np.zeros(n)
            eligible_indices = [i for i in range(n) if lock_ins[i] <= horizon]
            safest_idx = min(eligible_indices, key=lambda i: (risks[i], self.products.iloc[i]['liquidity_days']))
            weights[safest_idx] = 1.0

        # Construct allocation table
        alloc_df = self.products.copy()
        alloc_df['weight'] = weights
        alloc_df['allocated_amount_inr'] = np.round(weights * profile['existing_investment_inr'], 2)
        alloc_df['allocation_pct'] = np.round(weights * 100, 2)

        # Metrics
        blended_return = float(np.dot(weights, returns))
        blended_risk = float(np.dot(weights, risks))
        blended_ter = float(np.dot(weights, self.products['annual_expense_ratio'].values))
        annual_cost_inr = blended_ter * profile['existing_investment_inr']

        summary = {
            'blended_return': blended_return,
            'blended_risk': blended_risk,
            'blended_ter': blended_ter,
            'annual_cost_inr': annual_cost_inr,
            'fallback_used': fallback_used
        }

        return alloc_df, summary