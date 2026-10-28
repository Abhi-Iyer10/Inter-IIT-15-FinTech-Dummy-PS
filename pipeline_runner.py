import pandas as pd
from data_validator import DataValidator
from portfolio_optimizer import PortfolioOptimizer
from goal_projector import GoalProjector

def process_all_profiles(profiles_csv_path, products_csv_path):
    profiles_df = pd.read_csv(profiles_csv_path)
    products_df = pd.read_csv(products_csv_path)

    valid, prod_errors = DataValidator.validate_products(products_df)
    if not valid:
        raise ValueError(f"Product data validation failed: {prod_errors}")

    optimizer = PortfolioOptimizer(products_df)
    all_allocations = []
    all_summaries = []

    for _, raw_profile in profiles_df.iterrows():
        clean_p, errors, warnings = DataValidator.validate_profile(raw_profile)
        if errors:
            print(f"Skipping profile {raw_profile.get('investor_id')} due to errors: {errors}")
            continue

        alloc_df, summary = optimizer.optimize(clean_p)
        proj = GoalProjector.project_goal(clean_p, summary['blended_return'])

        for _, row in alloc_df[alloc_df['weight'] > 0].iterrows():
            all_allocations.append({
                'investor_id': clean_p['investor_id'],
                'product_id': row['product_id'],
                'product_name': row['product_name'],
                'allocation_pct': row['allocation_pct'],
                'allocated_amount_inr': row['allocated_amount_inr']
            })

        liquid_amount = alloc_df[alloc_df['liquidity_days'] <= 3]['allocated_amount_inr'].sum()
        liq_status = "Sufficient" if liquid_amount >= clean_p['liquidity_need_inr'] else "Deficit"

        all_summaries.append({
            'investor_id': clean_p['investor_id'],
            'goal_label': clean_p.get('goal_label', 'Goal'),
            'target_amount_inr': clean_p['goal_amount_inr'],
            'horizon_months': clean_p['horizon_months'],
            'blended_return_pct': round(summary['blended_return'] * 100, 2),
            'weighted_risk_score': round(summary['blended_risk'], 2),
            'weighted_ter_pct': round(summary['blended_ter'] * 100, 3),
            'annual_cost_inr': round(summary['annual_cost_inr'], 2),
            'fv_base_inr': proj['fv_base'],
            'fv_cons_inr': proj['fv_conservative'],
            'fv_opt_inr': proj['fv_optimistic'],
            'goal_gap_inr': proj['goal_gap_inr'],
            'liquidity_status': liq_status,
            'warnings_count': len(warnings),
            'fallback_used': summary['fallback_used']
        })

    pd.DataFrame(all_allocations).to_csv("allocation_recommendations.csv", index=False)
    pd.DataFrame(all_summaries).to_csv("summary_projections.csv", index=False)
    print("Execution complete. Output CSV files generated.")

if __name__ == "__main__":
    process_all_profiles("investor_profiles.csv", "investment_products.csv")