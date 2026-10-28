import streamlit as st
import pandas as pd
import numpy as np

from data_validator import DataValidator
from portfolio_optimizer import PortfolioOptimizer
from goal_projector import GoalProjector
from explainability_engine import ExplainabilityEngine
from whatif_simulator import ScenarioSimulator

st.set_page_config(page_title="SmartWealth | Goal-Based Engine", layout="wide")

st.title("SmartWealth: Goal-Based Wealth Platform")
st.caption("Powered by NiveshNow | Multi-Constraint Portfolio Strategy")

@st.cache_data
def load_data():
    profiles_df = pd.read_csv("investor_profiles.csv")
    products_df = pd.read_csv("investment_products.csv")
    return profiles_df, products_df

try:
    profiles_df, products_df = load_data()
except Exception as e:
    st.error(f"Error loading CSV files: {e}")
    st.stop()

st.sidebar.header("1. Select Investor Persona")
persona_options = profiles_df['investor_id'] + " - " + profiles_df.get('goal_label', 'Goal')
selected_option = st.sidebar.selectbox("Choose Persona", persona_options)
selected_id = selected_option.split(" - ")[0]

raw_profile = profiles_df[profiles_df['investor_id'] == selected_id].iloc[0].to_dict()
clean_profile, errors, warnings = DataValidator.validate_profile(raw_profile)

if errors:
    st.error(f"Cannot process profile due to validation errors: {errors}")
    st.stop()

if warnings:
    for w in warnings:
        st.warning(w)

st.subheader(f"Investor Profile: {clean_profile['investor_id']} ({clean_profile.get('goal_label', 'Goal')})")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Target Amount", f"₹{clean_profile['goal_amount_inr']:,.0f}")
c2.metric("Horizon", f"{clean_profile['horizon_months']} Months")
c3.metric("Existing Investment", f"₹{clean_profile['existing_investment_inr']:,.0f}")
c4.metric("Monthly SIP", f"₹{clean_profile['monthly_sip_inr']:,.0f}")
c5.metric("Risk Tolerance", f"{clean_profile['risk_tolerance_score']} / 5")

st.divider()

optimizer = PortfolioOptimizer(products_df)
alloc_df, summary = optimizer.optimize(clean_profile)

tab1, tab2, tab3, tab4 = st.tabs(["Portfolio Allocation", "Goal Feasibility", "Explainability & Costs", "What-If Simulator"])

with tab1:
    st.subheader("Recommended Portfolio Allocation")
    active_alloc = alloc_df[alloc_df['weight'] > 0.0001].copy()
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.dataframe(
            active_alloc[['product_id', 'product_name', 'asset_class', 'risk_score', 'allocation_pct', 'allocated_amount_inr', 'annual_expense_ratio']],
            column_config={
                "allocation_pct": st.column_config.NumberColumn("Allocation %", format="%.2f %%"),
                "allocated_amount_inr": st.column_config.NumberColumn("Allocated Amount", format="₹ %,.2f"),
                "annual_expense_ratio": st.column_config.NumberColumn("Expense Ratio", format="%.4f"),
                "risk_score": st.column_config.NumberColumn("Risk Score")
            },
            hide_index=True,
            use_container_width=True
        )
    with col_b:
        st.metric("Blended Expected Return", f"{summary['blended_return']*100:.2f}%")
        st.metric("Weighted Risk Score", f"{summary['blended_risk']:.2f} / 5.0")
        st.metric("Weighted TER", f"{summary['blended_ter']*100:.3f}%")
        st.metric("Estimated Annual Cost", f"₹{summary['annual_cost_inr']:,.2f}")
        if summary['fallback_used']:
            st.error("Safe Fallback Active (100% Liquid Reserve)")

with tab2:
    st.subheader("Future Value Projections & Goal Feasibility")
    projection = GoalProjector.project_goal(clean_profile, summary['blended_return'])
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Conservative FV (-3%)", f"₹{projection['fv_conservative']:,.0f}")
    m2.metric("Base FV (Projected)", f"₹{projection['fv_base']:,.0f}")
    m3.metric("Optimistic FV (+3%)", f"₹{projection['fv_optimistic']:,.0f}")
    
    gap_val = projection['goal_gap_inr']
    if gap_val > 0:
        m4.metric("Goal Shortfall", f"₹{gap_val:,.0f}", delta=f"-₹{gap_val:,.0f}", delta_color="inverse")
    else:
        m4.metric("Goal Surplus", f"₹{-gap_val:,.0f}", delta=f"+₹{-gap_val:,.0f}", delta_color="normal")

    st.markdown("### Actionable Goal Adjustments")
    for adj in projection['adjustments']:
        st.info(adj)

with tab3:
    st.subheader("Recommendation Rationales & Cost/Liquidity Analysis")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Annual Expense Breakdown")
        st.write(f"- **Weighted Expense Ratio (TER)**: {summary['blended_ter']*100:.3f}%")
        st.write(f"- **Estimated Annual Fee**: ₹{summary['annual_cost_inr']:,.2f}")
    with c2:
        st.markdown("#### Liquidity Readiness")
        liquid_alloc = active_alloc[active_alloc['liquidity_days'] <= 3]['allocated_amount_inr'].sum()
        req_liq = clean_profile['liquidity_need_inr']
        is_covered = liquid_alloc >= req_liq
        st.write(f"- **Near-term Liquidity Need**: ₹{req_liq:,.2f}")
        st.write(f"- **Liquid Product Allocation (<= 3 Days)**: ₹{liquid_alloc:,.2f}")
        if is_covered:
            st.success("Liquidity Condition Satisfied")
        else:
            st.warning("Liquidity Shortfall Flagged")

    st.markdown("#### Natural Language Rationale")
    rationales = ExplainabilityEngine.generate_rationales(clean_profile, alloc_df, summary, products_df)
    for r in rationales:
        st.markdown(r)

with tab4:
    st.subheader("What-If Stress Testing")
    scenario_choice = st.selectbox(
        "Select Stress Test Scenario", 
        [
            ("market_shock_15", "15% Market Crash on Existing Investment"),
            ("sip_reduction_20", "20% Reduction in Monthly SIP"),
            ("shorter_horizon_25", "25% Reduction in Goal Horizon")
        ],
        format_func=lambda x: x[1]
    )
    
    if st.button("Run Simulation"):
        sim_res = ScenarioSimulator.run_scenario(clean_profile, summary['blended_return'], scenario_type=scenario_choice[0])
        st.write(f"**Scenario Outcome**: {sim_res['scenario_description']}")
        
        s1, s2 = st.columns(2)
        s1.metric("Simulated Base FV", f"₹{sim_res['fv_base']:,.0f}")
        s2.metric("Simulated Goal Gap", f"₹{sim_res['goal_gap_inr']:,.0f}")
        
        st.write("**Simulated Action Adjustments Required:**")
        for a in sim_res['adjustments']:
            st.write(f"- {a}")