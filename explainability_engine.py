class ExplainabilityEngine:
    @staticmethod
    def generate_rationales(profile, alloc_df, summary, products_df):
        rationales = []
        horizon = profile['horizon_months']
        risk_tol = profile['risk_tolerance_score']

        if summary['fallback_used']:
            rationales.append(
                "**Fallback Active**: Constraints (horizon/risk limit) conflicted with product minimums. "
                "Allocated 100% to liquid cash reserve to preserve principal."
            )
        else:
            rationales.append(
                f"**Strategy Overview**: Recommended portfolio balances an expected return of "
                f"**{summary['blended_return']*100:.2f}%** with a weighted risk score of **{summary['blended_risk']:.2f}** "
                f"(strictly within risk tolerance of {risk_tol}.0)."
            )

        active_alloc = alloc_df[alloc_df['weight'] > 0.0001]
        for _, row in active_alloc.iterrows():
            p_name = row['product_name']
            w_pct = row['allocation_pct']
            r_score = row['risk_score']

            if r_score <= 2:
                role = "provides capital preservation and meets near-term stability requirements"
                downside = "yields lower growth during strong market rallies"
            elif r_score == 3:
                role = "delivers balanced growth and volatility dampening"
                downside = "experiences mild temporary drawdowns during market pullbacks"
            else:
                role = "drives long-term inflation-beating wealth creation"
                downside = "exhibits elevated short-term price volatility"

            rationales.append(f"- **{p_name} ({w_pct:.1f}%)**: Included because it {role}. *Key Trade-off*: {downside}.")

        excluded_lockin = products_df[products_df['lock_in_months'] > horizon]
        for _, row in excluded_lockin.iterrows():
            rationales.append(
                f"**Excluded ({row['product_name']})**: Excluded because its lock-in of {row['lock_in_months']} months "
                f"exceeds your goal timeline of {horizon} months."
            )

        if horizon <= 36:
            rationales.append(
                "**Regulatory Guardrail Applied**: Combined high-risk equity products (Risk 4-5) capped at <= 10% "
                "due to short horizon (<= 36 months) to protect against capital loss."
            )

        return rationales