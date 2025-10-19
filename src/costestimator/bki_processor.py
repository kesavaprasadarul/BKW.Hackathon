# bki_processor.py
# This module handles the pre-processing and enrichment of BKI data.

import json
import re
import os

def enrich_bki_data_with_power(bki_data: list, cache_path: str, use_llm: bool = False) -> list:
    """
    Enriches BKI data by extracting power (Leistung) from the title into structured fields.
    Uses a cached version if available.
    """
    if os.path.exists(cache_path):
        print(f"Loading enriched BKI data from cache: {cache_path}")
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    if use_llm:
        # Placeholder for batch processing with a real LLM API
        # enriched_data = process_with_llm_in_batches(bki_data, batch_size=LLM_BATCH_SIZE)
        pass # Fallback to regex for now
    
    # --- Regex-based enrichment ---
    enriched_data = []
    for item in bki_data:
        title = item.get("title", "")
        # FIX: Create a copy of the original item to preserve all fields
        enriched_item = item.copy()

        # Regex to find ranges like "70 bis 150kW" or single values like "bis 60kW"
        range_match = re.search(r"(\d+)\s+bis\s+(\d+)\s*kW", title, re.IGNORECASE)
        single_match = re.search(r"bis\s+(\d+)\s*kW", title, re.IGNORECASE)

        min_kw, max_kw = 0, 0
        if range_match:
            min_kw = int(range_match.group(1))
            max_kw = int(range_match.group(2))
        elif single_match:
            max_kw = int(single_match.group(1))
        
        enriched_item['leistung_min_kw'] = min_kw
        enriched_item['leistung_max_kw'] = max_kw
        
        enriched_data.append(enriched_item)

    # Cache the enriched data for future runs
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(enriched_data, f, ensure_ascii=False, indent=4)
    
    return enriched_data

