"""
Merge heating (Heizung) and ventilation (Raumlüftung) Excel files
based on room identification columns.
Uses AI-powered structure detection to handle messy Excel files.
"""

import pandas as pd
from typing import Optional, Tuple, List
import asyncio
import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
import openpyxl
from functools import lru_cache
import hashlib
import time

load_dotenv()

class ExcelAnalysis(BaseModel):
    header_row_num: int
    data_start_row: int
    room_type_col_name: Optional[str] = None

async def analyze_excel(df: pd.DataFrame, sample_rows: int = 20, sample_cols: int = 15) -> ExcelAnalysis:
    """
    Analyze a DataFrame structure using Gemini to determine the header row and data start row.
    
    Args:
        df: DataFrame to analyze (should be read with header=None to preserve raw structure)
        sample_rows: Number of rows to sample for analysis (default: 20)
        sample_cols: Number of columns to sample for analysis (default: 15)
    
    Returns:
        ExcelAnalysis with detected header_row_num and data_start_row
    """
    try:
        # Sample the dataframe for analysis
        max_row = min(sample_rows, len(df))
        max_col = min(sample_cols, len(df.columns))
        
        # Create a text representation of the DataFrame structure
        excel_preview = []
        for row_idx in range(max_row):
            row_data = []
            for col_idx in range(max_col):
                value = str(df.iloc[row_idx, col_idx]) if pd.notna(df.iloc[row_idx, col_idx]) else ""
                row_data.append(value[:30])  # Limit cell content length
            excel_preview.append(f"Row {row_idx}: {' | '.join(row_data)}")
        
        preview_text = "\n".join(excel_preview)

        print(preview_text)
        
        # Initialize Gemini with vision capabilities
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            api_key=os.getenv("GOOGLE_GEMINI_API_KEY"),
        )
        
        llm_with_structured_output = llm.with_structured_output(ExcelAnalysis)
        
        prompt = f"""You are analyzing an Excel file structure to identify the correct header row and data start row.

**Your Task:**
Analyze the following Excel file preview and determine:
1. **header_row_num**: The row number (0-indexed) that contains the column headers/field names. Look for rows with descriptive text like "Geschoss", "Raum-Nr.", "Fläche", "Volumen", "Nummer Raumtyp", etc.
2. **data_start_row**: The row number (0-indexed) where actual data begins (first row after the header).

**What to look for:**
- Header row typically contains German technical terms like:
  - "Geschoss" (floor)
  - "Raum-Nr." (room number)
  - "Raum-Bezeichnung" (room description)
  - "Nummer Raumtyp" (room type number)
  - "Fläche" (area)
  - "Volumen" (volume)
  - "spez. Wärmebedarf" (specific heating demand)
  - "spez. Kältebedarf" (specific cooling demand)
  
- Data rows contain actual values (numbers, room names, etc.)
- There might be title rows or empty rows before the header
- The header row is usually bold or has different formatting

**Excel File Preview (first {max_row} rows):**
{preview_text}

Return the 0-indexed row numbers for the header and data start."""

        response = await llm_with_structured_output.ainvoke(prompt)
        return response
        
    except Exception as e:
        print(f"Error analyzing DataFrame structure: {e}")
        # Return default values if analysis fails
        return ExcelAnalysis(header_row_num=0, data_start_row=1)

async def merge_heating_ventilation_excel(
    heating_path: str,
    ventilation_path: str,
    header_row: Optional[int] = None,
    merge_keys: Optional[List[str]] = None,
    how: str = 'outer',
    auto_detect_structure: bool = True,
    types: Optional[dict] = None
) -> pd.DataFrame:
    """
    Merge heating and ventilation Excel files based on room identification.
    Uses AI-powered structure analysis to handle messy Excel files automatically.
    
    The function merges two technical building equipment (TGA) Excel files:
    - Heizung (heating/cooling loads)
    - Raumlüftung (ventilation data)
    
    Args:
        heating_path (str): Path to the heating Excel file (.xlsm or .xlsx)
        ventilation_path (str): Path to the ventilation Excel file (.xlsm or .xlsx)
        header_row (Optional[int]): Row number containing the column headers (0-indexed). 
            If None and auto_detect_structure=True, will use AI to detect. Default is None.
        merge_keys (Optional[List[str]]): List of column names to use for merging.
            Default: ['Geschoss', 'Raum-Nr.', 'Raum-Bezeichnung', 'Nummer Raumtyp']
        how (str): Type of merge to perform. Options:
            - 'inner': Only keep rooms present in both files
            - 'outer': Keep all rooms from both files (default)
            - 'left': Keep all rooms from heating file
            - 'right': Keep all rooms from ventilation file
        auto_detect_structure (bool): If True, uses AI to detect Excel structure automatically.
            Handles title rows, merged cells, and inconsistent formatting. Default is True.
    
    Returns:
        pd.DataFrame: Merged dataframe with columns from both heating and ventilation files.
            Columns with the same name will have suffixes '_heating' and '_ventilation'.
    
    Example:
        >>> # Async usage (auto-detects structure)
        >>> merged_df = await merge_heating_ventilation_excel(
        ...     'data/p5-lp2-input-heizung.xlsm',
        ...     'data/p5-lp2-input-raumluftung.xlsm'
        ... )
        >>> 
        >>> # With manual header row
        >>> merged_df = await merge_heating_ventilation_excel(
        ...     'heating.xlsm', 'ventilation.xlsm',
        ...     header_row=5, auto_detect_structure=False
        ... )
    
    Notes:
        - This function is now async to support AI structure analysis
        - Automatically handles NaN values in merge keys
        - Duplicate column names get suffixes to distinguish between sources
        - Empty rows (all NaN in merge keys) are filtered out before merging
        - Works with messy Excel files (title rows, merged cells, etc.)
    """
    
    if merge_keys is None:
        # Default merge keys that identify unique rooms
        merge_keys = ['Geschoss', 'Raum-Nr.', 'Raum-Bezeichnung', 'Nummer Raumtyp']
    
    # Read both Excel files with structure detection
    print(f"📖 Reading heating file: {heating_path}")
    
    # Auto-detect structure if requested
    if auto_detect_structure and header_row is None:
        print(f"   🔍 Auto-detecting Excel structure for heating file...")
        df_heating_raw = pd.read_excel(heating_path, header=None)
        heating_analysis = await analyze_excel(df_heating_raw)
        heating_header_row = heating_analysis.header_row_num
        heating_data_start = heating_analysis.data_start_row
        print(f"   ✓ Detected header at row {heating_header_row}, data starts at row {heating_data_start}")
        
        # Re-read with correct structure
        df_heating = pd.read_excel(heating_path, header=heating_header_row, skiprows=None)
        df_heating = df_heating.iloc[heating_data_start - heating_header_row - 1:].reset_index(drop=True)
    else:
        # Use provided header_row or default to 5
        actual_header_row = header_row if header_row is not None else 5
        df_heating = pd.read_excel(heating_path, header=actual_header_row)
    
    print(f"   Shape: {df_heating.shape}")
    
    print(f"📖 Reading ventilation file: {ventilation_path}")
    
    # Auto-detect structure if requested
    if auto_detect_structure and header_row is None:
        print(f"   🔍 Auto-detecting Excel structure for ventilation file...")
        df_ventilation_raw = pd.read_excel(ventilation_path, header=None)
        ventilation_analysis = await analyze_excel(df_ventilation_raw)
        ventilation_header_row = ventilation_analysis.header_row_num
        ventilation_data_start = ventilation_analysis.data_start_row
        print(f"   ✓ Detected header at row {ventilation_header_row}, data starts at row {ventilation_data_start}")
        
        # Re-read with correct structure
        df_ventilation = pd.read_excel(ventilation_path, header=ventilation_header_row, skiprows=None)
        df_ventilation = df_ventilation.iloc[ventilation_data_start - ventilation_header_row - 1:].reset_index(drop=True)
    else:
        # Use provided header_row or default to 5
        actual_header_row = header_row if header_row is not None else 5
        df_ventilation = pd.read_excel(ventilation_path, header=actual_header_row)
    
    print(f"   Shape: {df_ventilation.shape}")
    
    # Filter out rows where all merge keys are NaN (empty rows)
    heating_valid = df_heating[merge_keys].notna().any(axis=1)
    ventilation_valid = df_ventilation[merge_keys].notna().any(axis=1)
    
    df_heating_filtered = df_heating[heating_valid].copy()
    df_ventilation_filtered = df_ventilation[ventilation_valid].copy()
    
    print(f"\n🔍 After filtering empty rows:")
    print(f"   Heating: {len(df_heating_filtered)} valid rooms")
    print(f"   Ventilation: {len(df_ventilation_filtered)} valid rooms")
    
    # Create composite key for better matching
    # This handles cases where individual fields might have slight variations
    for df, name in [(df_heating_filtered, 'heating'), (df_ventilation_filtered, 'ventilation')]:
        df['_merge_key'] = (
            df['Geschoss'].fillna('').astype(str) + '|' +
            df['Raum-Nr.'].fillna('').astype(str) + '|' +
            df['Raum-Bezeichnung'].fillna('').astype(str)
        )
    
    # Merge the dataframes
    print(f"\n🔗 Merging files using keys: {merge_keys}")
    print(f"   Merge type: {how}")
    
    merged_df = pd.merge(
        df_heating_filtered,
        df_ventilation_filtered,
        on=merge_keys,
        how=how,
        suffixes=('_heating', '_ventilation'),
        indicator=True  # Adds column showing source of each row
    )
    
    # Report merge statistics
    merge_stats = merged_df['_merge'].value_counts()
    print(f"\n📊 Merge Statistics:")
    if 'both' in merge_stats.index:
        print(f"   ✓ Rooms in both files: {merge_stats['both']}")
    if 'left_only' in merge_stats.index:
        print(f"   ← Only in heating: {merge_stats['left_only']}")
    if 'right_only' in merge_stats.index:
        print(f"   → Only in ventilation: {merge_stats['right_only']}")
    
    print(f"\n✅ Merged dataframe shape: {merged_df.shape}")
    print(f"   Total columns: {len(merged_df.columns)}")
    
    return merged_df


def get_heating_columns(merged_df: pd.DataFrame) -> List[str]:
    """
    Extract columns that came from the heating file.
    
    Args:
        merged_df: Merged dataframe from merge_heating_ventilation_excel()
    
    Returns:
        List of column names from heating file
    """
    return [col for col in merged_df.columns if col.endswith('_heating') or 
            (not col.endswith('_ventilation') and col not in ['_merge', '_merge_key'])]


def get_ventilation_columns(merged_df: pd.DataFrame) -> List[str]:
    """
    Extract columns that came from the ventilation file.
    
    Args:
        merged_df: Merged dataframe from merge_heating_ventilation_excel()
    
    Returns:
        List of column names from ventilation file
    """
    return [col for col in merged_df.columns if col.endswith('_ventilation') or 
            (not col.endswith('_heating') and col not in ['_merge', '_merge_key'])]


def create_unified_performance_table(
    merged_df: pd.DataFrame,
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Create a unified performance table with heating, cooling, and ventilation data.
    
    Args:
        merged_df: Merged dataframe from merge_heating_ventilation_excel()
        output_path: Optional path to save the table as Excel file
    
    Returns:
        pd.DataFrame with key room identifiers and performance metrics
    """
    
    # Select key columns for the performance table
    key_columns = ['Geschoss', 'Raum-Nr.', 'Raum-Bezeichnung', 'Nummer Raumtyp', 'Bezeichnung Raumtyp']
    
    # Heating/cooling specific columns
    heating_metrics = []
    for col in merged_df.columns:
        if any(keyword in col.lower() for keyword in ['wärmebedarf', 'heizlast', 'kältebedarf', 'kühllast']):
            if not col.startswith('Unnamed'):
                heating_metrics.append(col)
    
    # Ventilation specific columns
    ventilation_metrics = []
    for col in merged_df.columns:
        if any(keyword in col.lower() for keyword in ['luftmenge', 'luftwechsel', 'zuluft']):
            if not col.startswith('Unnamed'):
                ventilation_metrics.append(col)
    
    # Area and volume
    area_volume_cols = ['Fläche_heating', 'Volumen_heating'] if 'Fläche_heating' in merged_df.columns else ['Fläche', 'Volumen']
    
    # Combine all relevant columns
    performance_columns = key_columns + area_volume_cols + heating_metrics + ventilation_metrics
    
    # Filter to only existing columns
    performance_columns = [col for col in performance_columns if col in merged_df.columns]
    
    performance_table = merged_df[performance_columns].copy()
    
    # Remove rows with no performance data
    performance_table = performance_table.dropna(subset=['Raum-Nr.'], how='all')
    
    print(f"\n📋 Created performance table:")
    print(f"   Rows: {len(performance_table)}")
    print(f"   Columns: {len(performance_table.columns)}")
    print(f"   Heating/Cooling metrics: {len(heating_metrics)}")
    print(f"   Ventilation metrics: {len(ventilation_metrics)}")
    
    if output_path:
        performance_table.to_excel(output_path, index=False)
        print(f"\n💾 Saved performance table to: {output_path}")
    
    return performance_table


def merge_heating_ventilation_excel_sync(
    heating_path: str,
    ventilation_path: str,
    header_row: Optional[int] = 5,
    merge_keys: Optional[List[str]] = None,
    how: str = 'outer'
) -> pd.DataFrame:
    """
    Synchronous wrapper for merge_heating_ventilation_excel.
    Uses manual header_row without AI detection for backward compatibility.
    
    For auto-detection with messy Excel files, use the async version:
    merged = await merge_heating_ventilation_excel(heating, ventilation)
    
    Args:
        heating_path: Path to heating Excel file
        ventilation_path: Path to ventilation Excel file  
        header_row: Row number with headers (default: 5)
        merge_keys: Columns to merge on
        how: Merge type ('inner', 'outer', 'left', 'right')
    
    Returns:
        Merged DataFrame
    """
    return asyncio.run(merge_heating_ventilation_excel(
        heating_path,
        ventilation_path,
        header_row=header_row,
        merge_keys=merge_keys,
        how=how,
        auto_detect_structure=False  # Disable AI detection for sync version
    ))


if __name__ == "__main__":
    # Example usage
    import sys
    
    # Default file paths
    heating_file = "data/p5-lp2-input-heizung.xlsm"
    ventilation_file = "data/p5-lp2-input-raumluftung.xlsm"
    
    # Allow command line arguments
    if len(sys.argv) > 2:
        heating_file = sys.argv[1]
        ventilation_file = sys.argv[2]
    
    async def main():
        # Merge the files with auto-detection
        print("🚀 Using AI-powered structure detection...")
        merged = await merge_heating_ventilation_excel(
            heating_file,
            ventilation_file,
            how='outer',  # Keep all rooms from both files
            auto_detect_structure=True  # Use AI to detect structure
        )
        
        # Create performance table
        performance = create_unified_performance_table(
            merged,
            output_path="merged_performance_table.xlsx"
        )
        
        # Display sample results
        print("\n📊 Sample of merged data:")
        print(merged[['Geschoss', 'Raum-Nr.', 'Raum-Bezeichnung', 'Nummer Raumtyp']].head(10))
        
        print("\n✅ Merge complete!")
        return merged
    
    # Run async main
    asyncio.run(main())
