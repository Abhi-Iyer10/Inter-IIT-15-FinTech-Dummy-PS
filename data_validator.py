import pandas as pd
import numpy as np

class DataValidator:
    REQUIRED_PROFILE_FIELDS = [
        'investor_id', 'goal_amount_inr', 'horizon_months', 
        'existing_investment_inr', 'monthly_sip_inr', 
        'risk_tolerance_score', 'emergency_fund_months'
    ]

    REQUIRED_PRODUCT_FIELDS = [
        'product_id', 'product_name', 'asset_class', 'risk_score',
        'assumed_annual_return', 'annual_expense_ratio', 
        'liquidity_days', 'lock_in_months'
    ]

    @classmethod
    def validate_profile(cls, profile_dict):
        """Validates individual persona and returns clean profile + warning flags."""
        errors = []
        warnings = []
        clean_profile = dict(profile_dict)

        # 1. Required fields check
        for field in cls.REQUIRED_PROFILE_FIELDS:
            if field not in clean_profile or pd.isna(clean_profile[field]):
                errors.append(f"Missing required field: {field}")

        if errors:
            return None, errors, warnings

        # 2. Type conversions
        try:
            clean_profile['goal_amount_inr'] = float(clean_profile['goal_amount_inr'])
            clean_profile['horizon_months'] = int(clean_profile['horizon_months'])
            clean_profile['existing_investment_inr'] = float(clean_profile['existing_investment_inr'])
            clean_profile['monthly_sip_inr'] = float(clean_profile['monthly_sip_inr'])
            clean_profile['risk_tolerance_score'] = int(clean_profile['risk_tolerance_score'])
            clean_profile['emergency_fund_months'] = float(clean_profile['emergency_fund_months'])
            clean_profile['liquidity_need_inr'] = float(clean_profile.get('liquidity_need_inr', 0.0))
        except ValueError as e:
            errors.append(f"Invalid numeric input detected: {str(e)}")
            return None, errors, warnings

        if clean_profile['horizon_months'] <= 0 or clean_profile['goal_amount_inr'] <= 0:
            errors.append("Goal amount and horizon must be strictly positive.")

        # 3. Emergency Buffer Check (< 3 months)
        if clean_profile['emergency_fund_months'] < 3.0:
            warnings.append(
                f"EMERGENCY BUFFER WARNING: Profile has only {clean_profile['emergency_fund_months']:.1f} months "
                f"of liquidity (recommended: >= 3.0 months). Allocate capital to liquid buffer before long-term goals."
            )

        # 4. Short Horizon vs High Risk Tolerance Check
        if clean_profile['horizon_months'] <= 36 and clean_profile['risk_tolerance_score'] >= 4:
            warnings.append(
                f"HORIZON MISMATCH WARNING: High risk tolerance ({clean_profile['risk_tolerance_score']}) "
                f"for short timeline ({clean_profile['horizon_months']}m). Regulatory limits will cap high-risk assets at 10%."
            )

        return clean_profile, errors, warnings

    @classmethod
    def validate_products(cls, products_df):
        """Validates product dataset completeness and integrity."""
        errors = []
        missing_cols = [col for col in cls.REQUIRED_PRODUCT_FIELDS if col not in products_df.columns]
        
        if missing_cols:
            errors.append(f"Product dataset missing required column(s): {missing_cols}")
            return False, errors

        if products_df[cls.REQUIRED_PRODUCT_FIELDS].isna().any().any():
            errors.append("Product dataset contains empty/null values.")
            
        return len(errors) == 0, errors