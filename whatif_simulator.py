from goal_projector import GoalProjector

class ScenarioSimulator:
    @staticmethod
    def run_scenario(profile, blended_return, scenario_type="market_shock_15"):
        sim_profile = profile.copy()

        if scenario_type == "market_shock_15":
            sim_profile['existing_investment_inr'] *= 0.85
            desc = "15% Market Shock applied to existing investment."

        elif scenario_type == "sip_reduction_20":
            sim_profile['monthly_sip_inr'] *= 0.80
            desc = "20% reduction in monthly SIP contribution."

        elif scenario_type == "shorter_horizon_25":
            sim_profile['horizon_months'] = int(sim_profile['horizon_months'] * 0.75)
            desc = "25% reduction in goal horizon timeline."

        else:
            desc = "Baseline projection (no shock)."

        proj = GoalProjector.project_goal(sim_profile, blended_return)
        proj['scenario_description'] = desc
        return proj