# cost_estimator.py
# This module contains the core logic for estimating costs using assemblies.

import math
import re

def find_best_component(required_load: float, components: list, verbose: bool = False) -> dict:
    """
    Finds the best component from a list based on the required load and power range.
    The "best" component is the smallest one that can meet the required load.
    """
    suitable_components = []
    if verbose: print(f"    > Searching for component to handle {required_load:.2f} kW load...")
    for comp in components:
        min_kw = comp.get('leistung_min_kw', 0)
        max_kw = comp.get('leistung_max_kw', 0)
        
        if max_kw > 0 and max_kw >= required_load:
            if min_kw > 0:
                if required_load >= min_kw:
                    suitable_components.append(comp)
            else:
                suitable_components.append(comp)

    if not suitable_components:
        if verbose: print("    > !! No suitable component found by load.")
        return None
        
    best_fit = min(suitable_components, key=lambda x: x.get('leistung_max_kw', float('inf')))
    if verbose: print(f"    > Found best fit: '{best_fit.get('title')}' with max load {best_fit.get('leistung_max_kw')} kW")
    return best_fit


def find_component_by_keywords(keywords: list, components: list, verbose: bool = False) -> dict:
    """
    Finds the first component that contains any of the specified keywords, with a preference for matching all keywords.
    """
    if verbose: print(f"    > Searching for component with keywords: {keywords}")
    # First, try to find a component that matches ALL keywords
    for comp in components:
        title = comp.get('title', '').lower()
        if all(keyword.lower() in title for keyword in keywords):
            if verbose: print(f"    > Found a strong match (all keywords): '{comp.get('title')}'")
            return comp
            
    # Fallback: if no component matches all keywords, try matching ANY keyword
    for comp in components:
        title = comp.get('title', '').lower()
        if any(keyword.lower() in title for keyword in keywords):
            if verbose: print(f"    > Found a fallback match (any keyword): '{comp.get('title')}'")
            return comp
            
    if verbose: print("    > !! No component found by keywords.")
    return None

def calculate_quantity(rule: str, metrics: dict, factors: dict, component_type: str = None) -> float:
    quantity = 0
    try:
        match = re.search(r"(\d+\.?\d*)\s+per\s+(\d+\.?\d*)\s+(kW|m2|m3/h)", rule.lower())
        if match:
            value_per_unit, unit_size, unit_type = float(match.group(1)), float(match.group(2)), match.group(3)
            metric_map = {"kw": "Total Heating Load (kW)", "m2": "Total Area (m^2)", "m3/h": "Total Airflow (m3/h)"}
            total_metric = metrics.get(metric_map.get(unit_type), 0)
            quantity = math.ceil((total_metric / unit_size) * value_per_unit) if unit_size > 0 else 0
        elif "*" in rule:
            factor, metric_key = rule.split('*')
            metric_map = {"total_area_m2": "Total Area (m^2)"}
            metric_value = metrics.get(metric_map.get(metric_key.strip()), 0)
            quantity = float(factor.strip()) * metric_value
        else:
            quantity = float(rule)

        if component_type == 'piping': quantity *= factors.get('piping_complexity_factor', 1.0)
        elif component_type == 'ducting': quantity *= factors.get('ducting_complexity_factor', 1.0)
        return quantity
    except Exception:
        return 0

def estimate_cost_from_assembly(project_metrics: dict, bki_data: list, assembly_template: dict, factors: dict, verbose: bool = False) -> dict:
    standard_line_items, percentage_templates = [], []
    heating_load_kw = project_metrics.get("Total Heating Load (kW)", 0)

    for component_template in assembly_template.get("components", []):
        if verbose: print(f"\n  Processing component: '{component_template.get('description')}'")
        
        if component_template.get("calculation_method") == "percentage_of_subgroup":
            percentage_templates.append(component_template)
            if verbose: print("    > Identified as percentage-based. Will process later.")
            continue

        quantity = calculate_quantity(component_template.get("quantity_rule"), project_metrics, factors, component_template.get("type"))
        if verbose: print(f"    > Quantity Rule: '{component_template.get('quantity_rule')}' -> Calculated Qty: {quantity:.2f}")

        found_component = None
        if quantity > 0:
            bki_kostengruppe = component_template.get("bki_kostengruppe")
            # --- SAFEGUARD ---
            if not bki_kostengruppe:
                if verbose: print(f"    > !! Error: Missing 'bki_kostengruppe' in template for '{component_template.get('description')}'.")
                continue
            
            components_in_kg = [item for item in bki_data if item.get('kostengruppe') == "KG " + bki_kostengruppe]
            if verbose: print(f"    > Found {len(components_in_kg)} items in BKI data for KG {bki_kostengruppe}")

            bki_search_method = component_template.get("bki_search_method")
            if bki_search_method == "find_best_match_by_load":
                load_per_unit = heating_load_kw / quantity
                found_component = find_best_component(load_per_unit, components_in_kg, verbose)
            elif bki_search_method == "find_by_keywords":
                keywords = component_template.get("bki_keywords")
                found_component = find_component_by_keywords(keywords, components_in_kg, verbose)
        else:
            if verbose: print("    > Skipping BKI search as quantity is zero.")

        material_unit_price = 0
        if found_component and found_component.get('preise', {}).get('mittel_netto'):
            try:
                material_unit_price = float(found_component['preise']['mittel_netto'])
                if verbose: print(f"    > Extracted Material Price: {material_unit_price:.2f}")
            except (ValueError, TypeError):
                if verbose: print(f"    > !! Could not parse price for component: {found_component['title']}")
                material_unit_price = 0

        standard_line_items.append({
            **component_template, "quantity": quantity, "material_unit_price": material_unit_price,
            "total_material_price": quantity * material_unit_price,
            "bki_component_title": found_component['title'] if found_component else "N/A"
        })

    subgroup_material_totals = {
        kg: sum(li['total_material_price'] for li in standard_line_items if li.get("subgroup_kg") == kg)
        for kg in set(ct.get("subgroup_kg") for ct in assembly_template.get("components"))
    }
    total_kg_material_cost = sum(subgroup_material_totals.values())
    if verbose: print(f"\n  Subgroup Material Totals (before percentages): {subgroup_material_totals}")
    
    percentage_line_items = []
    for component_template in percentage_templates:
        if verbose: print(f"\n  Processing percentage component: '{component_template.get('description')}'")
        basis_kg = component_template.get("calculation_basis_kg")
        basis_cost = total_kg_material_cost if basis_kg == "420_total" else subgroup_material_totals.get(basis_kg, 0)
        percentage = component_template.get("percentage_value", 0)
        material_unit_price = basis_cost * percentage
        if verbose: print(f"    > Basis Cost ({basis_kg}): {basis_cost:.2f}, Percentage: {percentage:.2f} -> Price: {material_unit_price:.2f}")
        
        percentage_line_items.append({
            **component_template, "quantity": 1.0, "material_unit_price": material_unit_price,
            "total_material_price": material_unit_price,
            "bki_component_title": "N/A (Percentage Based)"
        })

    all_line_items = standard_line_items + percentage_line_items
    processed_boq = []
    for item in all_line_items:
        total_material = item.get("total_material_price", 0)
        labor_cost = total_material * factors.get("labor_factor", 0)
        markup = (total_material + labor_cost) * factors.get("overhead_profit_factor", 0)
        final_price = (total_material + labor_cost + markup) * factors.get("regional_factor_munich", 1) * factors.get("time_index_factor", 1)
        
        processed_boq.append({
            "description": item.get("description"), "subgroup_kg": item.get("subgroup_kg"), "subgroup_title": item.get("subgroup_title"),
            "quantity": item.get("quantity"), "unit": item.get("unit"), "material_unit_price": item.get("material_unit_price"),
            "total_material_price": total_material, "total_final_price": final_price,
            "bki_component_title": item.get("bki_component_title"), "type": item.get("type")
        })

    return {"line_items": processed_boq, "total_final_cost": sum(item['total_final_price'] for item in processed_boq)}

