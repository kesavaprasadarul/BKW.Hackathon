import asyncio
import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd
from pydantic import BaseModel
from functools import lru_cache
import time

# Load environment variables
load_dotenv()

class RoomPowerEstimate(BaseModel):
    """Power estimates for a single room"""
    room_nr: str
    heating_W_per_m2: int
    cooling_W_per_m2: int
    ventilation_m3_per_h: int

class OutputAnalysis(BaseModel):
    """Analysis results for multiple rooms of the same type"""
    values_per_trade: list[RoomPowerEstimate]


class ExcelAnalysis(BaseModel):
    header_row_num: int
    data_start_row: int

class RoomTypeMapping(BaseModel):
    """Single mapping entry from room type name to historic data key"""
    room_type_name: str
    historic_key: str

class HistoricDataEntry(BaseModel):
    """Collection of room type mappings"""
    mappings: list[RoomTypeMapping]

async def generate_room_type_mapping(room_type_names, historic_data: dict) -> dict:
    """Generate a mapping for room type names to historic data keys using gemini."""
    print(f"\n🔍 Generating room type mapping for: {room_type_names}")
    
    keys = list(historic_data.keys())

    prompt = f"""You are an expert in data mapping and classification. 

Given these room type names: {room_type_names}

Map each room type to the MOST appropriate key from this list of historic data keys: {keys}

For each room type, find the best matching historic key based on similarity in meaning and function.
You must provide at least one mapping per room type name.

Examples:
- "WCs" should map to "WC's" 
- "Einzel-/Zweierbüros" should map to "Büros und Räume ähnlicher Nutzung"
- "Verkehrsflächen, Flure" should map to "Verkehrsflächen, Flure"
"""

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        temperature=0.2,
        api_key=os.getenv("GOOGLE_GEMINI_API_KEY"),
        max_retries=3,
    ).with_structured_output(HistoricDataEntry)

    response = await llm.ainvoke(prompt)
    print(f"✓ Mapping response: {response}")
    
    # Convert list of mappings to dict
    mapping_dict = {m.room_type_name: m.historic_key for m in response.mappings}
    return mapping_dict

async def test_cost_analysis(df: pd.DataFrame, skip_structure_analysis: bool = False, types: dict[int, str] = None):
    """
    Analyze room data and estimate power requirements per trade.
    
    Args:
        df: DataFrame containing room data
        skip_structure_analysis: If True, assumes df already has proper column names (from merge).
                                 If False, will analyze structure and extract headers from raw data.
    
    Returns:
        Dictionary mapping room numbers to power estimates
    """
    print(f"\nDataFrame shape: {df.shape} (rows, columns)")
    print(f"Column names: {list(df.columns[:10])}...")  # Show first 10 columns

    # Load historic data
    with open("context.json", "r", encoding="utf-8") as f:
        historic_data = json.load(f)
    
    # Initialize Google GenAI chat model with optimized settings
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        temperature=0.2,
        api_key=os.getenv("GOOGLE_GEMINI_API_KEY"),
        max_retries=3,
    )

    llm_with_structured_output = llm.with_structured_output(OutputAnalysis)

    seen_types = set()
    print(f"\n{'='*60}")
    print("Starting room type analysis...")
    print(f"{'='*60}")
    
    # Check if 'Nummer Raumtyp' column exists
    if "Nummer Raumtyp" in df.columns:
        print(f"✓ Found 'Nummer Raumtyp' column")
        print(f"Sample values: {df['Nummer Raumtyp'].dropna().unique()}")
    else:
        print(f"⚠ 'Nummer Raumtyp' column not found!")
        print(f"Available columns: {list(df.columns)}")
        return {}
    
    # Collect all unique room types and prepare batch data
    unique_room_types = df['Nummer Raumtyp'].dropna().unique()
    unique_room_types = [int(rt) for rt in unique_room_types if isinstance(rt, (int, float)) and 0 <= rt < 100]
    
    print(f"\n📊 Found {len(unique_room_types)} unique room types to process")
    print(f"   Room types: {sorted(unique_room_types)}")
    
    start_time = time.time()
    
    # Prepare batch prompts for all room types
    batch_prompts = []
    batch_metadata = []

    room_type_names = [types.get(rt, "Unknown") for rt in unique_room_types]

    mapping = await generate_room_type_mapping(room_type_names, historic_data)
    print(f"✓ Generated mapping: {mapping}")
    
    for room_type in unique_room_types:
        df_filtered = df[df["Nummer Raumtyp"] == room_type]
        room_type_name = types.get(room_type, "Unknown")
        historic_key = mapping.get(room_type_name, room_type_name)  # Use room_type_name as fallback
        filtered_historic = historic_data.get(historic_key, [])

        if not filtered_historic:
            print(f"⚠ Skipping room type {room_type} - no historic data")
            continue
        
        print(f"✓ Prepared batch for room type {room_type} ({room_type_name}): {len(df_filtered)} rooms")
        
        prompt = f"""You are an expert in Technical Building Equipment (TGA - Technische Gebäudeausrüstung) and MEP (Mechanical, Electrical, and Plumbing) engineering, specializing in German/Swiss construction standards. You have extensive experience in calculating heating loads, cooling loads, and ventilation requirements according to DIN EN 12831, DIN EN 16798, and VDI 2078 standards.

        Your task is to analyze room data and estimate the power requirements per trade (Gewerk) for each room. You will receive:

        1. **Historic data** from similar room types (room type {room_type_name}) from completed projects, which contains:
        - spez. Wärmebedarf pro m² (specific heating demand per m²)
        - spez. Kältebedarf pro m² (specific cooling demand per m²)
        - spez. Luftmenge pro m² (specific air volume per m²)
        - Gesamt Heizlast (total heating load)
        - Gesamt Kühllast (total cooling load)
        - Other relevant parameters

        2. **Current room data** for room type {room_type_name} that you need to analyze, including:
        - Fläche (area in m²)
        - Volumen (volume in m³)
        - Geschoss (floor level)
        - Raum-Bezeichnung (room name)
        - Other characteristics

        **Historic Data for Room Type {room_type_name}:**
        {filtered_historic}

        **Current Room Data to Analyze:**
        {df_filtered.to_json(orient='records', force_ascii=False, indent=2)}

        Based on the historic data patterns and the characteristics of each current room, provide your estimated power requirements for each room.

        Return a list of power estimates (one per room in the same order as the current room data) with:
        - room_nr: Use 'Raum-Nr.' field, or 'Raum-Bezeichnung' if 'Raum-Nr.' is empty/NaN
        - heating_W_per_m2: Specific heating demand in Watts per square meter
        - cooling_W_per_m2: Specific cooling demand in Watts per square meter  
        - ventilation_m3_per_h: Ventilation air volume in cubic meters per hour

        Consider factors such as:
        - Floor area and volume
        - Floor level (ground floor vs. upper floors vs. basement)
        - Historic averages for this room type
        - Typical ranges for this room type (e.g., offices: 20-80 W/m² heating, 30-100 W/m² cooling)

        Provide realistic estimates based on the historic data and engineering best practices."""

        batch_prompts.append(prompt)
        batch_metadata.append({
            'room_type': room_type,
            'room_type_name': room_type_name,
            'df_filtered': df_filtered
        })
    
    if not batch_prompts:
        print("❌ No valid room types to process")
        return {}
    
    # Process all room types in parallel using batch
    print(f"\n🚀 Processing {len(batch_prompts)} room types in parallel...")
    print(f"   Using batched API calls with max_concurrency=5")
    
    try:
        # Use abatch for async batch processing with concurrency control
        batch_responses = await llm_with_structured_output.abatch(
            batch_prompts,
            config={"max_concurrency": 5}  # Limit parallel requests to avoid rate limits
        )
        
        elapsed_time = time.time() - start_time
        print(f"✅ Batch processing complete in {elapsed_time:.2f}s!")
        print(f"   Average time per room type: {elapsed_time/len(batch_prompts):.2f}s")
        
        # Process results
        power_estimates_results = {}
        for response, metadata in zip(batch_responses, batch_metadata):
            room_type_name = metadata['room_type_name']
            print(f"\n📊 Results for {room_type_name}:")
            
            for power_estimate in response.values_per_trade:
                power_estimates_results[power_estimate.room_nr] = {
                    "room_type": metadata['room_type'],
                    "heating_W_per_m2": power_estimate.heating_W_per_m2,
                    "cooling_W_per_m2": power_estimate.cooling_W_per_m2,
                    "ventilation_m3_per_h": power_estimate.ventilation_m3_per_h
                }
            
            print(f"   ✓ Processed {len(response.values_per_trade)} rooms")

        # Save results to Excel
        output_df = pd.DataFrame.from_dict(power_estimates_results, orient='index')
        output_df.to_excel(f"performance_table.xlsx", index_label="Raum-Nr.")
        print(f"\n💾 Results saved to: performance_table.xlsx")
        
        return power_estimates_results
        
    except Exception as e:
        print(f"An error occurred during analysis: {e}")

if __name__ == "__main__":
    # Import here to avoid circular dependency
    from merge_excel_files import merge_heating_ventilation_excel
    
    async def main():
        types = {
            1: "Flex-/ Co-Work/",
            2: "Einzel-/Zweierbüros",
            3: "Technikum",
            4: "Smart Farming",
            5: "Robotik",
            6: "Verkehrsflächen, Flure",
            7: "Teeküchen",
            8: "WCs",
            9: "ELT-Zentrale",
            10: "Putzmittel/ Lager",
            11: "Lager innenliegend",
            12: "TGA-Zentrale",
            13: "Etagenverteiler",
            14: "ELT-Schacht",
            15: "Batterieräume",
            16: "Drucker-/Kopierräume",
            17: "Treppenhäuser/Magistrale",
            18: "Schächte",
            19: "Aufzüge",
            20: "Serminarraum",
            21: "Diele"
        }

        # Merge heating and ventilation data with AI-powered structure detection
        merged_df = await merge_heating_ventilation_excel(
            'data/p5-lp2-input-heizung.xlsm',
            'data/p5-lp2-input-raumluftung.xlsm',
            auto_detect_structure=True  # Use AI to handle messy Excel files
        )
        
        # Analyze the merged DataFrame (skip structure analysis since merge already has proper columns)
        power_generated_results = await test_cost_analysis(merged_df, skip_structure_analysis=True, types=types)
        

        # Add the power estimates back into the Excel file under the appropriate columns
        for room_nr, estimates in power_generated_results.items():
            room_mask = merged_df['Raum-Nr.'] == room_nr
            if not room_mask.any():
                continue  # Skip if room number not found
            
            merged_df.loc[room_mask, 'Heizlast (W/m²)'] = estimates['heating_W_per_m2']
            merged_df.loc[room_mask, 'Kälteleistung (W/m²)'] = estimates['cooling_W_per_m2']
            merged_df.loc[room_mask, 'Luftvolumenstrom (m³/h)'] = estimates['ventilation_m3_per_h']

        # Save the updated DataFrame back to Excel
        merged_df.to_excel('data/p5-lp2-output-heizung.xlsm', index=False)

    # Run the async main function
    asyncio.run(main())
