import numpy as np

class GoalProjector:
    @staticmethod
    def calculate_fv(P, S, r, n):
        if n <= 0:
            return P
        if r == 0:
            return P + S * n
        monthly_r = r / 12.0
        fv_capital = P * ((1.0 + monthly_r) ** n)
        fv_sip = S * (((1.0 + monthly_r) ** n - 1.0) / monthly_r)
        return float(fv_capital + fv_sip)

    @classmethod
    def project_goal(cls, profile, blended_return):
        P = profile['existing_investment_inr']
        S = profile['monthly_sip_inr']
        n = profile['horizon_months']
        target = profile['goal_amount_inr']

        r_base = blended_return
        r_cons = max(blended_return - 0.03, 0.01)
        r_opt = blended_return + 0.03

        fv_base = cls.calculate_fv(P, S, r_base, n)
        fv_cons = cls.calculate_fv(P, S, r_cons, n)
        fv_opt = cls.calculate_fv(P, S, r_opt, n)

        gap_base = target - fv_base
        is_achievable = gap_base <= 0

        adjustments = []
        if not is_achievable:
            monthly_r = r_base / 12.0
            fv_p = P * ((1.0 + monthly_r) ** n)
            needed_from_sip = target - fv_p
            if needed_from_sip > 0:
                req_sip = needed_from_sip * monthly_r / (((1.0 + monthly_r) ** n) - 1.0)
                sip_delta = req_sip - S
                adjustments.append(f"Increase monthly SIP by ₹{sip_delta:,.0f} (to ₹{req_sip:,.0f}/month).")

            for ext_n in range(n + 1, n + 180):
                fv_ext = cls.calculate_fv(P, S, r_base, ext_n)
                if fv_ext >= target:
                    adjustments.append(f"Extend horizon by {ext_n - n} months (to {ext_n} months total).")
                    break
        else:
            adjustments.append("Goal target is fully achievable under base return projections.")

        return {
            'fv_base': round(fv_base, 2),
            'fv_conservative': round(fv_cons, 2),
            'fv_optimistic': round(fv_opt, 2),
            'goal_gap_inr': round(gap_base, 2),
            'is_achievable': is_achievable,
            'adjustments': adjustments
        }