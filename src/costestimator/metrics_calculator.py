# metrics_calculator.py
# This module calculates key project metrics from the new JSON input.

def calculate_metrics_from_json(power_estimates: dict) -> dict:
    """
    Calculates total loads, area, volume, and airflow from the power_estimates dictionary.
    """
    if not power_estimates:
        return {}

    total_heating_w = 0
    total_cooling_w = 0
    total_area_m2 = 0
    total_volume_m3 = 0
    total_airflow_m3h = 0

    for room_data in power_estimates.values():
        # Rule 1: Drop rows with None values for area or volume, as they can't be calculated.
        area = room_data.get('area_m2')
        volume = room_data.get('volume_m3')
        if area is None or volume is None:
            continue

        # Safely get values, defaulting to 0 if they don't exist
        heating_w_per_m2 = room_data.get('heating_W_per_m2', 0) or 0
        cooling_w_per_m2 = room_data.get('cooling_W_per_m2', 0) or 0
        ventilation_m3_per_h = room_data.get('ventilation_m3_per_h', 0) or 0

        # Rule 2: Calculate total heating and cooling loads by multiplying by area
        total_heating_w += area * heating_w_per_m2
        total_cooling_w += area * cooling_w_per_m2
        
        # Sum up the direct metrics
        total_area_m2 += area
        total_volume_m3 += volume
        total_airflow_m3h += ventilation_m3_per_h

    return {
        # Convert from W to kW for consistency with our templates
        "Total Heating Load (kW)": total_heating_w / 1000,
        "Total Cooling Load (kW)": total_cooling_w / 1000,
        "Total Area (m^2)": total_area_m2,
        "Total Volume (m^3)": total_volume_m3,
        "Total Airflow (m3/h)": total_airflow_m3h,
    }

