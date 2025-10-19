# cost_estimator.py
# This module contains the core logic for estimating costs using assemblies.

import math
import re

def find_best_component(required_load: float, components: list) -> dict:
    """
    Finds the best component from a list based on the required load and power range.
    The "best" component is the smallest one that can meet the required load.
    """
    suitable_components = []
    for comp in components:
        min_kw = comp.get('leistung_min_kw', 0)
        max_kw = comp.get('leistung_max_kw', 0)
        # Check for a range
        if min_kw > 0 and max_kw > 0:
            if min_kw <= required_load <= max_kw:
                suitable_components.append(comp)
        # Check for a single value
        elif min_kw == max_kw and max_kw >= required_load:
             suitable_components.append(comp)

    if not suitable_components:
        return None
    # Find the component with the smallest capacity that still meets the load
    return min(suitable_components, key=lambda x: x.get('leistung_max_kw', float('inf')))


def find_component_by_keywords(keywords: list, components: list) -> dict:
    """
    Finds the first component that contains any of the specified keywords, with a preference for matching all keywords.
    """
    # First, try to find a component that matches ALL keywords
    for comp in components:
        title = comp.get('title', '').lower()
        if all(keyword.lower() in title for keyword in keywords):
            return comp
    # Fallback: if no component matches all keywords, try matching ANY keyword
    for comp in components:
        title = comp.get('title', '').lower()
        if any(keyword.lower() in title for keyword in keywords):
            return comp
    return None

def calculate_quantity(rule: str, metrics: dict, factors: dict, component_type: str = None) -> float:
    """
    Calculates the quantity for a line item based on a rule and project metrics.
    Applies a complexity factor for piping components.
    """
    quantity = 0
    try:
        # Generalized rule parser for "X per Y unit of metric"
        match = re.search(r"(\d+\.?\d*)\s+per\s+(\d+\.?\d*)\s+(kW|m2)", rule)
        if match:
            value_per_unit = float(match.group(1))
            unit_size = float(match.group(2))
            unit_type = match.group(3)

            if unit_type == "kW":
                total_metric = metrics.get("Total Heating Load (kW)", 0)
            elif unit_type == "m2":
                total_metric = metrics.get("Total Area (m^2)", 0)
            else:
                total_metric = 0
            
            if unit_size > 0:
                quantity = math.ceil((total_metric / unit_size) * value_per_unit)

        elif "*" in rule:
            parts = rule.split('*')
            factor = float(parts[0].strip())
            metric_key = parts[1].strip()
            metric_map = {"total_area_m2": "Total Area (m^2)"}
            metric_value = metrics.get(metric_map.get(metric_key), 0)
            quantity = factor * metric_value
        
        else:
            quantity = float(rule)

        # Apply complexity factor if the component is of type 'piping'
        if component_type == 'piping':
            quantity *= factors.get('piping_complexity_factor', 1.0)
            
        return quantity

    except Exception:
        print(f"Warning: Could not evaluate rule '{rule}'. Defaulting to 0.")
        return 0

def estimate_cost_from_assembly(project_metrics: dict, bki_data: list, assembly_template: dict, factors: dict) -> dict:
    """
    Generates a detailed, fully-loaded cost estimate using an assembly template and cost factors.
    """
    line_items = []
    heating_load_kw = project_metrics.get("Total Heating Load (kW)", 0)

    # First pass: Calculate costs for all items except percentage-based ones
    for component_template in assembly_template.get("components", []):
        if component_template.get("calculation_method") == "percentage_of_subgroup":
            continue # Skip for now

        quantity, material_unit_price, found_component = 0, 0, None
        component_type = component_template.get("type")
        
        bki_search_method = component_template.get("bki_search_method")
        
        if bki_search_method == "find_best_match_by_load":
            components_in_kg = [item for item in bki_data if item.get('kostengruppe') == component_template.get("bki_kostengruppe")]
            quantity = calculate_quantity(component_template.get("quantity_rule"), project_metrics, factors, component_type)
            load_per_unit = heating_load_kw / quantity if quantity > 0 else 0
            found_component = find_best_component(load_per_unit, components_in_kg)

        elif bki_search_method == "find_by_keywords":
            keywords = component_template.get("bki_keywords")
            components_in_kg = [item for item in bki_data if item.get('kostengruppe') == component_template.get("bki_kostengruppe")]
            found_component = find_component_by_keywords(keywords, components_in_kg)
            if found_component:
                 quantity = calculate_quantity(component_template.get("quantity_rule"), project_metrics, factors, component_type)

        if found_component and found_component.get('preise', {}).get('mittel_netto'):
            try:
                material_unit_price = float(found_component.get('preise', {}).get('mittel_netto', 0))
            except (ValueError, TypeError):
                material_unit_price = 0
        
        line_items.append({
            "component_template": component_template,
            "quantity": quantity,
            "material_unit_price": material_unit_price,
            "total_material_price": quantity * material_unit_price,
            "bki_component_title": found_component['title'] if found_component else "N/A"
        })

    # Second pass: Calculate percentage-based items
    final_line_items = []
    # Calculate all subgroup totals first
    subgroup_material_totals = {
        kg: sum(li['total_material_price'] for li in line_items if li['component_template'].get("subgroup_kg") == kg) 
        for kg in set(ct.get("subgroup_kg") for ct in assembly_template.get("components"))
    }
    # Calculate the grand total of all standard items
    total_kg_material_cost = sum(subgroup_material_totals.values())


    # Add the standard items to the final list first
    for li in line_items:
        final_line_items.append({**li, **li.pop("component_template")})

    # Now calculate and add the percentage-based items
    for component_template in assembly_template.get("components", []):
        if component_template.get("calculation_method") == "percentage_of_subgroup":
            basis_kg = component_template.get("calculation_basis_kg")
            
            basis_cost = 0
            if basis_kg == "420_total":
                basis_cost = total_kg_material_cost
            else:
                basis_cost = subgroup_material_totals.get(basis_kg, 0)

            percentage = component_template.get("percentage_value", 0)
            material_unit_price = basis_cost * percentage
            quantity = 1 # Pauschal items are always quantity 1
            
            final_line_items.append({
                **component_template,
                "quantity": quantity,
                "material_unit_price": material_unit_price,
                "total_material_price": material_unit_price,
                "bki_component_title": "N/A (Percentage Based)"
            })

    # Final calculation of total costs and applying factors
    processed_line_items = []
    for item in sorted(final_line_items, key=lambda x: x.get('subgroup_kg', '')):
        total_material_price = item.get("total_material_price", 0)
        
        labor_cost = total_material_price * factors.get("labor_factor", 0)
        subtotal = total_material_price + labor_cost
        markup = subtotal * factors.get("overhead_profit_factor", 0)
        regional_adjusted = (subtotal + markup) * factors.get("regional_factor_munich", 1)
        final_price = regional_adjusted * factors.get("time_index_factor", 1)
        
        item["total_final_price"] = final_price
        processed_line_items.append(item)

    return {"line_items": processed_line_items, "total_final_cost": sum(item['total_final_price'] for item in processed_line_items)}

