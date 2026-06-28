from config import (BuildingInputs, ClimateInputs, InsulationInputs,
                    WindowInputs, HVACInputs, TS825Limits, CostInputs)
from cases import build_envelope_cases, build_combination_cases
from lcc import build_lcc_cases
from reporting import (plot_heating_vs_insulation, plot_cooling_vs_insulation,
                       plot_window_heating, plot_cost_vs_performance,
                       plot_ua_breakdown, plot_furnace_efficiency_impact,
                       plot_ac_cop_impact, plot_movable_insulation_benefit,
                       draw_hvac_flow_diagram)


def main():
    building   = BuildingInputs()
    climate    = ClimateInputs()   # T_winter=-3°C, T_summer=+33°C, f_n=0.45
    insulation = InsulationInputs()
    windows    = WindowInputs()
    hvac       = HVACInputs()
    ts825      = TS825Limits()
    costs      = CostInputs()
    envelope_df = build_envelope_cases(
        building, climate, insulation, windows, ts825)
    combination_df = build_combination_cases(envelope_df, hvac, {})
    cost_df = build_lcc_cases(combination_df, building, costs)
    scored_df = cost_df.copy()
    scored_df['total_energy_kWh_yr'] = (
        scored_df['heating_load_kWh_yr'] + scored_df['cooling_load_kWh_yr'])

    output_cols = [
        'insulation_thickness_cm', 'window_type', 'movable_insulation',
        'boiler_efficiency', 'ac_cop',
        'heating_load_kWh_yr', 'cooling_load_kWh_yr',
        'capex_TL', 'annual_total_opex_TL', 'total_cost_TL',
    ]

    # Top 20 by lowest total energy
    perf_top20 = scored_df.sort_values('total_energy_kWh_yr').head(20)
    perf_top20 = perf_top20[output_cols].reset_index(drop=True)

    # Top 20 by composite cost-performance score
    cost_range   = (scored_df['total_cost_TL'].max()
                    - scored_df['total_cost_TL'].min())
    energy_range = (scored_df['total_energy_kWh_yr'].max()
                    - scored_df['total_energy_kWh_yr'].min())
    scored_df['score'] = (
        (scored_df['total_cost_TL']
         - scored_df['total_cost_TL'].min()) / cost_range
        + (scored_df['total_energy_kWh_yr']
           - scored_df['total_energy_kWh_yr'].min()) / energy_range
    )
    cost_perf_top20 = scored_df.sort_values('score').head(20)
    cost_perf_top20 = cost_perf_top20[output_cols].reset_index(drop=True)
    
    plot_heating_vs_insulation(envelope_df)       # Figure 1
    plot_cooling_vs_insulation(envelope_df)       # Figure 2
    plot_window_heating(envelope_df)              # Figure 3
    plot_cost_vs_performance(cost_df)             # Figure 4
    plot_ua_breakdown(envelope_df)                # Figure 5
    plot_furnace_efficiency_impact(combination_df) # Figure 6
    plot_ac_cop_impact(combination_df)            # Figure 7
    plot_movable_insulation_benefit(envelope_df)  # Figure 8
    draw_hvac_flow_diagram()                      # Figure 9

    print('All analysis complete. Results in outputs/ folder.')
    return perf_top20, cost_perf_top20


if __name__ == '__main__':
    main()
