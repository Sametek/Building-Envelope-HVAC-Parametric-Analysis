import pandas as pd
from config import BuildingInputs, CostInputs
from geometry import compute_building_geometry


def build_lcc_cases(
        combination_df: pd.DataFrame,
        building: BuildingInputs,
        costs: CostInputs) -> pd.DataFrame:
    """
    Compute CAPEX, annual OPEX, and total cost for every combination.

    CAPEX = insulation_area * unit_cost_ins
          + window_area * unit_cost_window
          + window_area * unit_cost_movable * (1 if movable else 0)
          + boiler_cost + ac_cost

    OPEX  = heating_gas_cost + cooling_electricity_cost
          = (Q_heat / eta / gas_kWh_m3) * P_gas
          + (Q_cool / COP) * P_elec
    """
    geom = compute_building_geometry(building)
    insulation_area_m2 = geom['opaque_wall_area_m2'] + geom['roof_area_m2']
    window_area_m2     = geom['window_area_m2']
    df = combination_df.copy()

    def map_cost(series, mapping, decimals=2):
        return series.round(decimals).map(mapping)

    df['insulation_cost_TL_m2'] = map_cost(
        df['insulation_cm'], costs.insulation_cost_TL_m2_by_cm)
    df['window_cost_TL_m2'] = df['window_type'].map(
        costs.window_cost_TL_m2_by_type)
    df['boiler_cost_TL'] = map_cost(
        df['furnace_efficiency'], costs.boiler_cost_TL_by_efficiency)
    df['ac_cost_TL'] = map_cost(
        df['ac_COP'], costs.ac_cost_TL_by_cop)

    df['capex_TL'] = (
        insulation_area_m2 * df['insulation_cost_TL_m2']
        + window_area_m2   * df['window_cost_TL_m2']
        + window_area_m2   * costs.movable_insulation_cost_TL_m2
                          * df['movable_insulation'].astype(float)
        + df['boiler_cost_TL']
        + df['ac_cost_TL']
    )
    df['annual_heating_cost_TL'] = (
        df['heating_load_kWh_yr']
        / df['furnace_efficiency']
        / costs.gas_kWh_per_m3
        * costs.gas_TL_per_m3
    )
    df['annual_cooling_cost_TL'] = (
        df['cooling_load_kWh_yr']
        / df['ac_COP']
        * costs.electricity_TL_per_kWh
    )
    df['annual_total_opex_TL'] = (
        df['annual_heating_cost_TL'] + df['annual_cooling_cost_TL'])
    df['total_cost_TL'] = df['capex_TL'] + df['annual_total_opex_TL']

    out = df.rename(columns={
        'insulation_cm':      'insulation_thickness_cm',
        'furnace_efficiency': 'boiler_efficiency',
        'ac_COP':             'ac_cop',
    })
    return out[[
        'insulation_thickness_cm', 'window_type', 'movable_insulation',
        'boiler_efficiency', 'ac_cop',
        'heating_load_kWh_yr', 'cooling_load_kWh_yr',
        'capex_TL', 'annual_heating_cost_TL',
        'annual_cooling_cost_TL', 'annual_total_opex_TL', 'total_cost_TL',
    ]].reset_index(drop=True)
