import pytest
import pandas as pd
import numpy as np

from data_validator import DataValidator
from portfolio_optimizer import PortfolioOptimizer

@pytest.fixture
def load_data():
    profiles_df = pd.read_csv("investor_profiles.csv")
    products_df = pd.read_csv("investment_products.csv")
    return profiles_df, products_df

def test_allocation_sum_100(load_data):
    profiles_df, products_df = load_data
    optimizer = PortfolioOptimizer(products_df)
    clean_p, _, _ = DataValidator.validate_profile(profiles_df.iloc[0])
    
    alloc_df, _ = optimizer.optimize(clean_p)
    total_weight = alloc_df['weight'].sum()
    assert pytest.approx(total_weight, abs=0.001) == 1.0

def test_non_negative_weights(load_data):
    profiles_df, products_df = load_data
    optimizer = PortfolioOptimizer(products_df)
    clean_p, _, _ = DataValidator.validate_profile(profiles_df.iloc[1])
    
    alloc_df, _ = optimizer.optimize(clean_p)
    assert (alloc_df['weight'] >= -1e-6).all()

def test_lock_in_horizon_rule(load_data):
    profiles_df, products_df = load_data
    optimizer = PortfolioOptimizer(products_df)
    
    short_p = profiles_df[profiles_df['horizon_months'] < 36].iloc[0]
    clean_p, _, _ = DataValidator.validate_profile(short_p)
    
    alloc_df, _ = optimizer.optimize(clean_p)
    elss_weight = alloc_df[alloc_df['product_id'] == 'PROD07']['weight'].sum()
    assert elss_weight == 0.0

def test_risk_cap_rule(load_data):
    profiles_df, products_df = load_data
    optimizer = PortfolioOptimizer(products_df)
    
    for _, raw_p in profiles_df.iterrows():
        clean_p, _, _ = DataValidator.validate_profile(raw_p)
        if clean_p:
            alloc_df, summary = optimizer.optimize(clean_p)
            allowed_max_risk = clean_p['risk_tolerance_score'] + 0.25
            assert summary['blended_risk'] <= allowed_max_risk + 1e-3

def test_malformed_profile_handling(load_data):
    profiles_df, _ = load_data
    malformed_p = profiles_df.iloc[0].copy().to_dict()
    malformed_p['goal_amount_inr'] = None
    
    clean_p, errors, warnings = DataValidator.validate_profile(malformed_p)
    assert clean_p is None
    assert len(errors) > 0