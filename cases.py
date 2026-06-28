import pandas as pd
from config import (BuildingInputs, ClimateInputs, InsulationInputs,
                    WindowInputs, HVACInputs, TS825Limits)
from geometry import compute_building_geometry
from thermal import (compute_wall_U, compute_roof_U,
                     compute_window_U_with_movable_insulation,
                     compute_total_UA, compute_heating_and_cooling_loads,
                     compute_furnace_fuel_use, compute_ac_electricity_use)


def build_envelope_cases(
        building, climate, insulation, windows, ts825) -> pd.DataFrame:
    """
    Build all envelope combinations:
    3 insulation thicknesses × 3 window types × 2 movable states = 18 rows.
    """
    geom = compute_building_geometry(building)
    records = []
    for thickness_m in insulation.thicknesses_m:
        wall_U = compute_wall_U(thickness_m, insulation)
        roof_U = compute_roof_U(thickness_m, insulation)
        for window in windows.options:
            for movable in [False, True]:
                # Heating: movable insulation applied (closed at night)
                window_U_heating = (
                    compute_window_U_with_movable_insulation(
                        window.U_W_m2K,
                        windows.movable_insulation_R_m2K_W)
                    if movable else window.U_W_m2K
                )
                # Cooling: movable not applied (windows open/unshaded)
                window_U_cooling = (
                    window_U_heating
                    if windows.movable_insulation_applies_in_cooling
                    else window.U_W_m2K
                )
                UA_heating = compute_total_UA(
                    wall_U, roof_U, window_U_heating,
                    geom['opaque_wall_area_m2'],
                    geom['roof_area_m2'],
                    geom['window_area_m2'])
                UA_cooling = compute_total_UA(
                    wall_U, roof_U, window_U_cooling,
                    geom['opaque_wall_area_m2'],
                    geom['roof_area_m2'],
                    geom['window_area_m2'])
                loads = compute_heating_and_cooling_loads(
                    UA_heating, UA_cooling, climate)
                records.append({
                    'insulation_cm':        thickness_m * 100.0,
                    'window_type':          window.name,
                    'movable_insulation':   movable,
                    'wall_U':               round(wall_U, 4),
                    'roof_U':               round(roof_U, 4),
                    'window_U_heating':     round(window_U_heating, 4),
                    'window_U_cooling':     round(window_U_cooling, 4),
                    'UA_heating_W_K':       round(UA_heating, 2),
                    'UA_cooling_W_K':       round(UA_cooling, 2),
                    'heating_load_kWh_yr':  round(loads['heating_load_kWh_yr'], 1),
                    'cooling_load_kWh_yr':  round(loads['cooling_load_kWh_yr'], 1),
                    'wall_TS825_ok':  wall_U   <= ts825.wall_U_max_W_m2K,
                    'roof_TS825_ok':  roof_U   <= ts825.roof_U_max_W_m2K,
                    'window_TS825_ok': window_U_heating <= ts825.window_U_max_W_m2K,
                })
    df = pd.DataFrame(records)
    df['all_TS825_ok'] = (
        df['wall_TS825_ok'] & df['roof_TS825_ok'] & df['window_TS825_ok'])
    return df.sort_values(
        ['insulation_cm', 'window_type', 'movable_insulation']
    ).reset_index(drop=True)


def build_combination_cases(
        envelope_df: pd.DataFrame,
        hvac: HVACInputs,
        reference_filter: dict) -> pd.DataFrame:
    """Cross envelope cases with all HVAC efficiency combinations."""
    df = envelope_df.copy()
    for k, v in reference_filter.items():
        df = df[df[k] == v]
    records = []
    for _, row in df.iterrows():
        for eff in hvac.furnace_efficiencies:
            for cop in hvac.ac_cops:
                records.append({
                    'insulation_cm':        row['insulation_cm'],
                    'window_type':          row['window_type'],
                    'movable_insulation':   row['movable_insulation'],
                    'heating_load_kWh_yr':  row['heating_load_kWh_yr'],
                    'cooling_load_kWh_yr':  row['cooling_load_kWh_yr'],
                    'furnace_efficiency':   eff,
                    'gas_use_kWh_yr': compute_furnace_fuel_use(
                        row['heating_load_kWh_yr'], eff),
                    'ac_COP': cop,
                    'ac_electricity_kWh_yr': compute_ac_electricity_use(
                        row['cooling_load_kWh_yr'], cop),
                    'all_TS825_ok': row['all_TS825_ok'],
                })
    return pd.DataFrame(records)
