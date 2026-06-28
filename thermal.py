from config import InsulationInputs, ClimateInputs


def compute_R_insulation(thickness_m: float, k_W_mK: float) -> float:
    """R_ins = L / k     [m²K/W]"""
    if thickness_m < 0:
        raise ValueError('Insulation thickness cannot be negative.')
    if k_W_mK <= 0:
        raise ValueError('Thermal conductivity must be positive.')
    return thickness_m / k_W_mK if thickness_m > 0 else 0.0


def compute_U_from_R(R_total_m2K_W: float) -> float:
    """U = 1 / R_total     [W/m²K]"""
    if R_total_m2K_W <= 0:
        raise ValueError('Total thermal resistance must be positive.')
    return 1.0 / R_total_m2K_W


def compute_wall_U(thickness_m: float, ins: InsulationInputs) -> float:
    """U_wall = 1 / (R_fixed_wall + L/k)"""
    return compute_U_from_R(
        ins.wall_R_fixed_m2K_W
        + compute_R_insulation(thickness_m, ins.k_W_mK)
    )


def compute_roof_U(thickness_m: float, ins: InsulationInputs) -> float:
    """U_roof = 1 / (R_fixed_roof + L/k)"""
    return compute_U_from_R(
        ins.roof_R_fixed_m2K_W
        + compute_R_insulation(thickness_m, ins.k_W_mK)
    )


def compute_window_U_with_movable_insulation(
        base_U: float, movable_R: float) -> float:
    """
    Apply movable insulation in series with window.
    R_total = R_window + R_movable = 1/U_base + R_add
    U_eff = 1 / R_total

    This approximates a six-pane glazing system (U_eff ≈ 0.57–0.71 W/m²K).
    """
    base_R = 1.0 / base_U
    return 1.0 / (base_R + movable_R)


def compute_total_UA(
        wall_U, roof_U, window_U,
        wall_area, roof_area, window_area) -> float:
    """
    UA_total = U_wall*A_opaque + U_roof*A_roof + U_window*A_window  [W/K]
    """
    return (wall_U * wall_area
            + roof_U * roof_area
            + window_U * window_area)


def compute_seasonal_load_kWh(
        UA_W_K: float, delta_T_C: float, hours: float) -> float:
    """
    Q = UA * ΔT * t / 1000    [kWh/yr]
    Applies to heating and cooling seasons only.
    Neutral season load is zero by definition (ΔT ≈ 0).
    """
    return UA_W_K * delta_T_C * hours / 1000.0


def compute_heating_and_cooling_loads(
        UA_heating_W_K: float,
        UA_cooling_W_K: float,
        climate: ClimateInputs) -> dict:
    heating_load = compute_seasonal_load_kWh(
        UA_heating_W_K,
        climate.winter_delta_T,   # 23.0 K
        climate.winter_hours      # 2628 h/yr
    )
    cooling_load = compute_seasonal_load_kWh(
        UA_cooling_W_K,
        climate.summer_delta_T,   # 9.0 K
        climate.summer_hours      # 2190 h/yr
    )
    return {
        'heating_load_kWh_yr': heating_load,
        'cooling_load_kWh_yr': cooling_load,
    }


def compute_furnace_fuel_use(
        heating_load_kWh: float,
        furnace_efficiency: float) -> float:
    """E_gas = Q_heating / eta    [kWh_thermal/yr]"""
    return heating_load_kWh / furnace_efficiency


def compute_ac_electricity_use(
        cooling_load_kWh: float, cop: float) -> float:
    """E_elec = Q_cooling / COP    [kWh_electric/yr]"""
    return cooling_load_kWh / cop
