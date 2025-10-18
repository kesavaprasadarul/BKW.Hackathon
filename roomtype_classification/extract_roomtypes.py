import sys
import pandas as pd
import re
from pathlib import Path


def normalize_header(x):
    if pd.isna(x):
        return ""
    s = str(x).strip().lower()
    s = re.sub(r"[\s\.\:\;\-\_\/]+", "", s)
    return s


def find_header_positions(df, max_scan_rows=30):
    for r in range(min(max_scan_rows, len(df))):
        row_vals = df.iloc[r, :]
        norm_map = {c: normalize_header(v) for c, v in row_vals.items()}
        nr_candidates = [c for c, v in norm_map.items() if v in {"nr", "nummer"}]
        bez_candidates = [c for c, v in norm_map.items() if v in {"bezeichnung"}]
        if nr_candidates and bez_candidates:
            nr_col = sorted(
                nr_candidates,
                key=lambda c: c if isinstance(c, int) else df.columns.get_loc(c),
            )[0]
            bez_col = sorted(
                bez_candidates,
                key=lambda c: c if isinstance(c, int) else df.columns.get_loc(c),
            )[0]
            return r, nr_col, bez_col
    return None, None, None


def postprocess_data(block):
    block = block.copy()
    for col in block.columns:
        block[col] = block[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    mask_nonempty = block.apply(
        lambda row: any(
            [
                (isinstance(v, str) and v.strip() != "")
                or (pd.notna(v) and str(v).strip() != "")
                for v in row
            ]
        ),
        axis=1,
    )
    block = block[mask_nonempty]
    if "Nr" in block.columns:
        block["Nr"] = block["Nr"].apply(
            lambda x: (
                str(int(x))
                if isinstance(x, (int, float)) and pd.notna(x) and float(x).is_integer()
                else (str(x).strip() if pd.notna(x) else x)
            )
        )
    if "Roomtype" in block.columns:
        block["Roomtype"] = block["Roomtype"].apply(
            lambda x: str(x).strip() if pd.notna(x) else x
        )
    return block


def extract(xlsx_path: Path, out_csv: Path) -> pd.DataFrame:
    xls = pd.ExcelFile(xlsx_path)
    df = pd.read_excel(xlsx_path, header=None)
    header_row, nr_col, bez_col = find_header_positions(df, max_scan_rows=30)
    if header_row is None:
        raise ValueError("No header found")
    data = df.iloc[header_row + 1 :, [nr_col, bez_col]]
    data.columns = ["Nr", "Roomtype"]
    data = postprocess_data(data)
    if len(data) == 0:
        raise ValueError("No data found")

    data.to_csv(out_csv, index=False, encoding="utf-8-sig")
    return data


def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_roomtypes.py <input_xlsx> <output_csv>")
        sys.exit(1)
    xlsx_path = Path(sys.argv[1])
    out_csv = Path(sys.argv[2])
    df = extract(xlsx_path, out_csv)
    print(f"Wrote {len(df)} rows to {out_csv}")


if __name__ == "__main__":
    main()
