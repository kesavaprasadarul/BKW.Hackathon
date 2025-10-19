# bki_processor.py
# This module uses regex or an LLM to enrich BKI data by extracting power ratings.

import os
import re
import json
import time

def extract_power_with_regex(item_title: str) -> dict:
    """
    Extracts a power rating (single or range) from a string using regex.
    """
    # Pattern for ranges like "70 bis 150kW" or "70-150 kW"
    range_match = re.search(r'(\d+[\.,]?\d*)\s*(?:bis|-)\s*(\d+[\.,]?\d*)\s*kW', item_title, re.IGNORECASE)
    if range_match:
        min_power = float(range_match.group(1).replace(',', '.'))
        max_power = float(range_match.group(2).replace(',', '.'))
        return {'min': min_power, 'max': max_power}

    # Pattern for single values like "bis 25kW" or "25 kW"
    single_match = re.search(r'(\d+[\.,]?\d*)\s*kW', item_title, re.IGNORECASE)
    if single_match:
        power = float(single_match.group(1).replace(',', '.'))
        return {'min': power, 'max': power}

    return {'min': 0, 'max': 0}

def call_gemini_api_in_batch(batch: list) -> list:
    """
    (Placeholder) Simulates a batch call to a structured output LLM.
    The goal is to send multiple items and get a structured response for all of them.
    """
    print(f"(LLM Placeholder) Processing a batch of {len(batch)} items...")
    # In a real implementation, you would construct a single prompt with all item titles
    # and ask the LLM to return a JSON array of power ranges.
    # For now, we simulate this by processing each item with the regex function.
    results = []
    for item in batch:
        power_range = extract_power_with_regex(item.get('title', ''))
        # The response should map back to the original item, e.g., using its index or a unique ID.
        results.append({
            'original_index': item['original_index'],
            'power_range': power_range
        })
    return results


def enrich_bki_data_with_power(bki_data: list, cache_path: str, use_llm: bool = False, batch_size: int = 50) -> list:
    """
    Enriches BKI data by adding 'leistung_min_kw' and 'leistung_max_kw' fields.
    Uses a cache to avoid re-processing the entire file on every run.
    """
    if os.path.exists(cache_path):
        print(f"Loading enriched BKI data from cache: {cache_path}")
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    print(f"Enriching BKI data using {'LLM (in batches)' if use_llm else 'Regex'}. This may take a while...")
    
    enriched_data = [item.copy() for item in bki_data]
    power_relevant_kgs = ["KG 421", "KG 434"] 

    items_to_process = []
    for i, item in enumerate(enriched_data):
        # Skip items that have no price data
        if not item.get('preise', {}).get('mittel_netto'):
            continue
        # Check if item needs power extraction
        if item.get('kostengruppe') in power_relevant_kgs:
            item['original_index'] = i # Add index to map results back
            items_to_process.append(item)

    if use_llm:
        # Process items in batches
        for i in range(0, len(items_to_process), batch_size):
            batch = items_to_process[i:i + batch_size]
            batch_results = call_gemini_api_in_batch(batch)
            
            # Map results back to the main data list
            for result in batch_results:
                original_index = result['original_index']
                power_range = result['power_range']
                enriched_data[original_index]['leistung_min_kw'] = power_range['min']
                enriched_data[original_index]['leistung_max_kw'] = power_range['max']
                enriched_data[original_index]['leistung_kw'] = power_range['max']
            
            time.sleep(1) # API rate limiting between batches
    else:
        # Process with regex
        for item in items_to_process:
            power_range = extract_power_with_regex(item.get('title', ''))
            enriched_data[item['original_index']]['leistung_min_kw'] = power_range['min']
            enriched_data[item['original_index']]['leistung_max_kw'] = power_range['max']
            enriched_data[item['original_index']]['leistung_kw'] = power_range['max']

    # Clean up temporary index key before saving
    for item in enriched_data:
        item.pop('original_index', None)

    print(f"Saving enriched data to cache: {cache_path}")
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(enriched_data, f, indent=4, ensure_ascii=False)

    return enriched_data

