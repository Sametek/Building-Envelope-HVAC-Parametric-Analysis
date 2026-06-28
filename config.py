from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class BuildingInputs:
    floor_area_m2: float = 1000.0
    ceiling_height_m: float = 3.0
    window_fraction_of_wall: float = 0.20
    floor_heat_transfer: bool = False   # Floor is adiabatic (neglected)
    roof_area_m2: Optional[float] = None


@dataclass
class ClimateInputs:
    location_name: str = 'Istanbul (Tuzla)'
    winter_fraction: float = 0.30    # 30% of year at design winter temperature
    summer_fraction: float = 0.25    # 25% of year at design summer temperature
    neutral_fraction: float = 0.45   # 45% of year — no net heat transfer (Q=0)
    indoor_winter_C: float = 20.0
    indoor_summer_C: float = 24.0
    outdoor_winter_C: float = -3.0   # Istanbul winter design temp
    outdoor_summer_C: float = 33.0   # Istanbul summer design temp

    @property
    def winter_delta_T(self) -> float:
        return max(0.0, self.indoor_winter_C - self.outdoor_winter_C)
        # = 20.0 - (-3.0) = 23.0 K

    @property
    def summer_delta_T(self) -> float:
        return max(0.0, self.outdoor_summer_C - self.indoor_summer_C)
        # = 33.0 - 24.0 = 9.0 K

    @property
    def winter_hours(self) -> float:
        return self.winter_fraction * 8760.0   # = 2628 h/yr

    @property
    def summer_hours(self) -> float:
        return self.summer_fraction * 8760.0   # = 2190 h/yr


@dataclass
class InsulationInputs:
    material_name: str = 'Glass Fiber'
    k_W_mK: float = 0.040                    # Thermal conductivity [W/m·K]
    wall_R_fixed_m2K_W: float = 0.17          # Rsi(0.13) + Rso(0.04)
    roof_R_fixed_m2K_W: float = 0.14          # Rsi(0.10) + Rso(0.04)
    thicknesses_m: List[float] = field(default_factory=lambda: [0.03, 0.05, 0.10])


@dataclass
class WindowOption:
    name: str
    U_W_m2K: float


@dataclass
class WindowInputs:
    options: List[WindowOption] = field(default_factory=lambda: [
        WindowOption('Single Pane', 5.0),
        WindowOption('Double Pane', 2.7),
        WindowOption('Triple Pane', 1.8),
    ])
    # Movable insulation adds R_add in series with window resistance.
    # R_add = 1.20 m²K/W is chosen so that U_eff of triple-pane + movable
    # ≈ 0.57 W/m²K, approximating a six-pane glazing system equivalent.
    movable_insulation_R_m2K_W: float = 1.20
    # Movable insulation is applied in HEATING season only (closed at night).
    # During cooling, windows are open/unshaded — no R_add applied.
    movable_insulation_applies_in_cooling: bool = False


@dataclass
class HVACInputs:
    furnace_efficiencies: List[float] = field(
        default_factory=lambda: [0.70, 0.80, 0.90, 0.95])
    ac_cops: List[float] = field(
        default_factory=lambda: [2.5, 3.0, 3.5, 4.0])


@dataclass
class TS825Limits:
    degree_day_region: int = 2           # Istanbul = Region 2
    wall_U_max_W_m2K: float = 0.60
    roof_U_max_W_m2K: float = 0.40
    window_U_max_W_m2K: float = 2.40


@dataclass
class CostInputs:
    insulation_cost_TL_m2_by_cm: Dict[float, float] = field(
        default_factory=lambda: {3.0: 120.0, 5.0: 200.0, 10.0: 350.0})
    window_cost_TL_m2_by_type: Dict[str, float] = field(
        default_factory=lambda: {
            'Single Pane': 500.0,
            'Double Pane': 1350.0,
            'Triple Pane': 2500.0,
        })
    movable_insulation_cost_TL_m2: float = 600.0
    boiler_cost_TL_by_efficiency: Dict[float, float] = field(
        default_factory=lambda: {
            0.70: 25000.0, 0.80: 37500.0,
            0.90: 35000.0, 0.95: 80000.0,
        })
    ac_cost_TL_by_cop: Dict[float, float] = field(
        default_factory=lambda: {
            2.5: 21500.0, 3.0: 32500.0,
            3.5: 45000.0, 4.0: 62500.0,
        })
    electricity_TL_per_kWh: float = 3.50
    gas_TL_per_m3: float = 12.74
    gas_kWh_per_m3: float = 10.7
