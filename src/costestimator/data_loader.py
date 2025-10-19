# data_loader.py
# This module now handles loading the new JSON input and the BKI data.

import json

def load_input_data(file_path: str) -> dict:
    """
    Loads the main project data from the new, clean JSON format.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # We only need the 'power_estimates' part for calculation
        return data.get('power_estimates', {})
    except FileNotFoundError:
        print(f"Error: The input data file was not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: The input data file {file_path} is not a valid JSON.")
        return None

def load_bki_data(file_path: str) -> list:
    """
    Loads BKI data from a JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The BKI data file was not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: The BKI data file {file_path} is not a valid JSON.")
        return None

