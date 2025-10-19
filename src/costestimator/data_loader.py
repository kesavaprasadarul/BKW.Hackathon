# data_loader.py
# This module handles loading data from various file formats.

import pandas as pd
import json
import os

def load_performance_data(file_path: str) -> pd.DataFrame:
    """
    Loads performance data from a specific Excel sheet, handling potential errors.
    """
    try:
        # Load the specific sheet, skip initial non-data rows
        df = pd.read_excel(file_path, skiprows=4, header=1)

        required_columns = ['Gesamt Kühllast', 'Gesamt Heizlast', 'Fläche', "Raum-Nr."]
        
        # Check if all required columns are present
        if not all(col in df.columns for col in required_columns):
            print("Error: One or more required columns are missing from the Excel sheet.")
            print(f"Columns found: {df.columns.tolist()}")
            return None
        
        # Drop rows where 'Raum-Nr.' is missing, as they are not valid rooms
        df.dropna(subset=["Raum-Nr."], inplace=True)

        return df
    except FileNotFoundError:
        print(f"Error: The file was not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
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

