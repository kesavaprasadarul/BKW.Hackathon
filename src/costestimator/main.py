# main.py
# This script serves as the main entry point for the cost estimation engine.

import json
from collections import defaultdict
from data_loader import load_performance_data, load_bki_data
from metrics_calculator import calculate_project_metrics
from cost_estimator import estimate_cost_from_assembly
from bki_processor import enrich_bki_data_with_power

# --- CONFIGURATION ---
USE_LLM_ENRICHMENT = False
LLM_BATCH_SIZE = 50

# Represents the complexity of the internal distribution network.
# 1.0 = Medium (Standard Office), 1.3 = High (Labs/Hospitals), 0.8 = Low (Warehouse)
PIPING_COMPLEXITY_FACTOR = 1.0 

COST_FACTORS = {
    "regional_factor_munich": 1.15,
    "time_index_factor": 1.05,
    "labor_factor": 0.90,
    "overhead_profit_factor": 0.15,
    "piping_complexity_factor": PIPING_COMPLEXITY_FACTOR
}


def main():
    """
    Main function to run the cost estimation process.
    """
    print("Starting the cost estimation process...")

    # Define file paths
    performance_file_path = r'C:\Repos\BKW.Hackathon\data\Daten TUM.AI x BEN\Projekt 5\LP2\Technisches Raumbuch\ABP_Leistungsermittlung KLT_HZG - mit Raumtypen_20231.xlsm'
    bki_file_path = r'C:\Repos\BKW.Hackathon\static\bki\products_output_2024.json'
    assembly_template_path = 'assembly_templates.json'
    cache_suffix = 'llm' if USE_LLM_ENRICHMENT else 'regex'
    enriched_bki_file_path = f'bki_data_enriched_{cache_suffix}.json'

    # --- Step 1: Load and Process Data ---
    performance_df = load_performance_data(performance_file_path)
    bki_data = load_bki_data(bki_file_path)

    if performance_df is not None and bki_data is not None:
        enriched_bki_data = enrich_bki_data_with_power(
            bki_data,
            enriched_bki_file_path,
            use_llm=USE_LLM_ENRICHMENT,
            batch_size=LLM_BATCH_SIZE
        )
        
        print(f"\nSuccessfully loaded {len(performance_df)} rooms from the performance file.")
        print(f"Successfully loaded and processed {len(enriched_bki_data)} items from the BKI data file.")

        # --- Step 2: Calculate Core Metrics ---
        project_metrics = calculate_project_metrics(performance_df)
        print("\nCalculated Project Metrics:")
        for key, value in project_metrics.items():
            print(f"- {key}: {value:.2f}")

        # --- Step 3: Estimate Costs using Assemblies ---
        print("\n--- Cost Estimation from Assembly ---")
        
        with open(assembly_template_path, 'r', encoding='utf-8') as f:
            assembly_templates = json.load(f)

        kg420_template = assembly_templates.get("KG420_Heat_Pump_System")

        if kg420_template:
            detailed_estimate = estimate_cost_from_assembly(project_metrics, enriched_bki_data, kg420_template, COST_FACTORS)

            if detailed_estimate:
                # Group items by subgroup for structured printing
                subgroup_costs = defaultdict(lambda: {'items': [], 'total': 0.0})
                for item in detailed_estimate["line_items"]:
                    key = (item['subgroup_kg'], item['subgroup_title'])
                    subgroup_costs[key]['items'].append(item)
                    subgroup_costs[key]['total'] += item['total_final_price']

                print("\nGenerated Bill of Quantities for KG 420:")
                header = f"{'Description':<50} {'Qty':>6} {'Unit':<5} {'Material/Unit':>15} {'Total Material':>15} {'Total Final':>15}"
                
                # Sort subgroups by KG number
                sorted_subgroups = sorted(subgroup_costs.items(), key=lambda x: x[0][0])

                for (kg, title), data in sorted_subgroups:
                    print("\n" + "=" * 105)
                    print(f"KG {kg} {title.upper():<88} {data['total']:>15.2f}")
                    print("=" * 105)
                    print(header)
                    print("-" * 105)
                    for item in data['items']:
                         print(f"  {item['description']:<48} {item['quantity']:>6.1f} {item['unit']:<5} {item['material_unit_price']:>15.2f} {item['total_material_price']:>15.2f} {item['total_final_price']:>15.2f}")
                
                print("\n" + "="*105)
                print(f"{'GRAND TOTAL KG 420:':>88} {detailed_estimate['total_final_cost']:>15.2f}")
                print("="*105)

                # --- Step 4: Export to JSON ---
                export_file_path = 'cost_estimate_export.json'
                try:
                    with open(export_file_path, 'w', encoding='utf-8') as f:
                        json.dump(detailed_estimate, f, ensure_ascii=False, indent=4)
                    print(f"\nSuccessfully exported detailed estimate to {export_file_path}")
                except Exception as e:
                    print(f"\nError exporting to JSON: {e}")

    else:
        print("Could not proceed due to data loading errors.")


if __name__ == "__main__":
    main()

