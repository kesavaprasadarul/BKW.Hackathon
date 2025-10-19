# metrics_calculator.py
# This module calculates key project metrics from the raw data.

import pandas as pd

def calculate_project_metrics(performance_df: pd.DataFrame) -> dict:
    """
    Calculates total heating load, cooling load, and area from the performance DataFrame.
    """
    if performance_df is None:
        return {}

    # Convert relevant columns to numeric, coercing errors to NaN, then filling with 0
    numeric_cols = ['Gesamt Kühllast', 'Gesamt Heizlast', 'Fläche']
    for col in numeric_cols:
        performance_df[col] = pd.to_numeric(performance_df[col], errors='coerce').fillna(0)

    # Calculate metrics
    heating_load_kw = performance_df['Gesamt Heizlast'].sum()
    cooling_load_kw = performance_df['Gesamt Kühllast'].sum()
    total_area_m2 = performance_df['Fläche'].sum()

    return {
        "Total Heating Load (kW)": heating_load_kw,
        "Total Cooling Load (kW)": cooling_load_kw,
        "Total Area (m^2)": total_area_m2,
    }

