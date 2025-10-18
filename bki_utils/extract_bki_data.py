import re
import json

def extract_product_info(file_content):
    """
    Parses the BKI Baukosten markdown file with a robust and corrected
    method for extracting prices and other data.

    Args:
        file_content: A string containing the content of the markdown file.

    Returns:
        A list of dictionaries, where each dictionary represents a product.
    """
    # Split the content by the main product header '## ' followed by a number
    product_blocks = re.split(r'(?m)^##\s\d+', file_content)
    products = []

    for block in product_blocks:
        # Skip empty blocks that can result from the split
        if not block.strip():
            continue

        # The title is the first line of the block
        title_search = re.search(r'^(.*?)\n', block.strip(), re.MULTILINE)
        title_line = title_search.group(1).strip() if title_search else "N/A"

        kg_group_match = re.search(r'KG\s(\d+)', block)
        pos_num_match = re.search(r'(\d{3}\.\d{3}\.\d{3})', block)

        # --- CORRECTED PRICE EXTRACTION LOGIC ---
        # This robust regex finds lines containing ONLY a price.
        # It captures the number, ignoring surrounding whitespace and the optional Euro symbol.
        price_matches = re.findall(r'(?m)^\s*([\d\.,]+)\s*€+?\s*$', block)

        # Clean the matched prices by removing thousand separators (.)
        cleaned_prices = [p.replace('.', '') for p in price_matches]

        prices = {
            "min": None,
            "von": None,
            "mittel_netto": None,
            "bis": None,
            "max": None,
        }

        # Assign prices based on the count found
        if len(cleaned_prices) == 5:
            prices["min"], prices["von"], prices["mittel_netto"], prices["bis"], prices["max"] = cleaned_prices
        elif len(cleaned_prices) == 3:
            prices["von"], prices["mittel_netto"], prices["bis"] = cleaned_prices
        elif len(cleaned_prices) == 1:
            prices["mittel_netto"] = cleaned_prices[0]

        # --- Attribute Extraction ---
        attributes = {}
        # Pattern to find 'Key: Value' pairs on separate lines
        attribute_pattern = re.compile(r'^\s*([^:\n]+?):\s*(.*?)\s*$', re.MULTILINE)
        for attr_match in attribute_pattern.finditer(block):
            key = attr_match.group(1).strip()
            value = attr_match.group(2).strip()
            # A simple filter to avoid capturing long descriptive lines as keys
            if len(key.split()) < 8:
                 attributes[key] = value

        products.append({
            "title": title_line,
            "kostengruppe": f"KG {kg_group_match.group(1)}" if kg_group_match else None,
            "positionsnummer": pos_num_match.group(1) if pos_num_match else None,
            "preise": prices,
            "attributes": attributes
        })

    return products

# --- How to use the script ---

# 1. Read the file with the correct legacy encoding.
try:
    with open(r'C:\Repos\BKW.Hackathon\data\Daten TUM.AI x BEN\00_Allgemein\BKI_Baukosten_Neubau_2024_Positionen.md', 'r', encoding='utf-8') as f:
        file_content = f.read()
except FileNotFoundError:
    print("Error: The specified file was not found.")
    file_content = ""

# 2. Extract and clean the data.
if file_content:
    extracted_data = extract_product_info(file_content)

    # 3. Define the output file path.
    output_file_path = 'products_output_2024.json'

    # 4. Save the result to a new JSON file using UTF-8 encoding.
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Data successfully saved to {output_file_path}")