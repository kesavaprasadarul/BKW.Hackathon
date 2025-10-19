# main.py
# This script serves as the main entry point and test harness for the cost estimation engine.

import json
from typing import Dict
from pydantic import BaseModel
from pathlib import Path

# Use explicit relative imports so this module works when imported from API layer
from .data_loader import load_bki_data
from .metrics_calculator import calculate_metrics_from_json
from .cost_estimator import estimate_cost_from_assembly
from .bki_processor import enrich_bki_data_with_power

# --- Pydantic Models for API Integration ---
class PowerEstimates(BaseModel):
    room_nr: str
    room_type: int
    heating_W_per_m2: float
    cooling_W_per_m2: float
    ventilation_m3_per_h: float
    area_m2: float | None
    volume_m3: float | None

class PowerRequirementsResponse(BaseModel):
    heating_file: str
    ventilation_file: str
    merged_rows: int
    merged_columns: int
    power_estimates: Dict[str, PowerEstimates]
    performance_table: str
    message: str


# --- CONFIGURATION ---
BKI_FILE_PATH = '../static/bki/products_output_2024.json'
# Assembly templates & enriched data are stored alongside this module
ASSEMBLY_TEMPLATE_PATH =  '../static/cost-estimator/assembly_templates.json'
ENRICHED_BKI_FILE_PATH =  '../static/cost-estimator/bki_data_enriched_regex.json'

PIPING_COMPLEXITY_FACTOR = 1.0 
DUCTING_COMPLEXITY_FACTOR = 1.0

COST_FACTORS = {
    "regional_factor_munich": 1.15,
    "time_index_factor": 1.05,
    "labor_factor": 0.90,
    "overhead_profit_factor": 0.15,
    "piping_complexity_factor": PIPING_COMPLEXITY_FACTOR,
    "ducting_complexity_factor": DUCTING_COMPLEXITY_FACTOR
}


def generate_cost_estimate(request: PowerRequirementsResponse) -> dict:
    """
    Main business logic function to generate a complete cost estimate.
    It loads necessary data internally and uses the request model as input.
    """
    # Load and process static data files
    bki_data = load_bki_data(str(BKI_FILE_PATH))
    with open(ASSEMBLY_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        assembly_templates = json.load(f)

    if not bki_data or not assembly_templates:
        raise FileNotFoundError("Could not load required BKI data or assembly templates.")

    # Enrich BKI data (can be cached)
    enriched_bki_data = enrich_bki_data_with_power(bki_data, str(ENRICHED_BKI_FILE_PATH), use_llm=False)

    # Step 1: Calculate metrics from the request's power estimates
    # We convert the Pydantic models back to a dict for the existing function
    power_estimates_dict = {k: v.model_dump() for k, v in request.power_estimates.items()}
    project_metrics = calculate_metrics_from_json(power_estimates_dict)

    # Step 2: Estimate costs for each trade using assembly templates
    all_line_items = []
    total_cost = 0

    # KG 420 - Heating
    kg420_template = assembly_templates.get("KG420_Heat_Pump_System")
    if kg420_template:
        kg420_estimate = estimate_cost_from_assembly(project_metrics, enriched_bki_data, kg420_template, COST_FACTORS)
        all_line_items.extend(kg420_estimate["line_items"])
        total_cost += kg420_estimate["total_final_cost"]

    # KG 430 - Ventilation
    kg430_template = assembly_templates.get("KG430_Ventilation_System")
    if kg430_template:
        kg430_estimate = estimate_cost_from_assembly(project_metrics, enriched_bki_data, kg430_template, COST_FACTORS)
        all_line_items.extend(kg430_estimate["line_items"])
        total_cost += kg430_estimate["total_final_cost"]
    
    # Step 3: Format the final JSON output
    summary = {
        "project_metrics": project_metrics,
        "grand_total_cost": total_cost,
        "cost_factors_applied": COST_FACTORS
    }
    sorted_boq = sorted(all_line_items, key=lambda x: x.get('subgroup_kg', ''))

    return {
        "summary": summary,
        "detailed_boq": sorted_boq
    }


# --- Test Harness ---
if __name__ == "__main__":
    print("Starting the cost estimation process...")
    input_json_path = 'power_estimates.json'
    output_export_path = 'final_estimate_output.json'

    try:
        # Load the raw input data from JSON
        with open(input_json_path, 'r', encoding='utf-8') as f:
            raw_input_data = json.load(f)
        
        # Create a Pydantic model instance from the raw data
        request_model = PowerRequirementsResponse(**raw_input_data)
        
        # --- Run the main estimation function ---
        final_estimate = generate_cost_estimate(request_model)

        # --- Print a user-friendly summary to the console ---
        print("\n--- ESTIMATION SUMMARY ---")
        for key, value in final_estimate['summary']['project_metrics'].items():
            print(f"- {key}: {value:,.2f}")
        print("-" * 30)
        print(f"GRAND TOTAL ESTIMATED COST: {final_estimate['summary']['grand_total_cost']:,.2f} EUR")
        
        # --- Save the complete JSON output ---
        with open(output_export_path, 'w', encoding='utf-8') as f:
            json.dump(final_estimate, f, ensure_ascii=False, indent=4)
        print(f"\nSuccessfully exported detailed estimate to {output_export_path}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_json_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

