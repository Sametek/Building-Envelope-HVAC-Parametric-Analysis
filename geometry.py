import math
from config import BuildingInputs


def compute_building_geometry(building: BuildingInputs) -> dict:
    """
    For A_floor = 1000 m², H = 3 m:
      side_m          = sqrt(1000)      = 31.623 m
      perimeter_m     = 4 * 31.623      = 126.491 m
      gross_wall_area = 126.491 * 3.0   = 379.473 m²
      window_area     = 0.20 * 379.473  =  75.895 m²
      opaque_wall     = 379.473 - 75.895 = 303.578 m²
      roof_area       = 1000.0 m²
      volume          = 1000.0 * 3.0    = 3000.0 m³
    """
    side_m            = math.sqrt(building.floor_area_m2)
    perimeter_m       = 4.0 * side_m
    gross_wall_area_m2 = perimeter_m * building.ceiling_height_m
    window_area_m2    = gross_wall_area_m2 * building.window_fraction_of_wall
    opaque_wall_area_m2 = gross_wall_area_m2 - window_area_m2
    roof_area_m2      = (building.roof_area_m2
                         if building.roof_area_m2 is not None
                         else building.floor_area_m2)
    volume_m3         = building.floor_area_m2 * building.ceiling_height_m
    return {
        'side_m':              round(side_m, 3),
        'perimeter_m':         round(perimeter_m, 3),
        'gross_wall_area_m2':  round(gross_wall_area_m2, 3),
        'window_area_m2':      round(window_area_m2, 3),
        'opaque_wall_area_m2': round(opaque_wall_area_m2, 3),
        'roof_area_m2':        roof_area_m2,
        'volume_m3':           volume_m3,
    }
