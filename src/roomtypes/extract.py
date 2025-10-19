"""Extract Roomtypes from Excel files"""

from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet
import csv

from src.roomtypes.io import load_wb, detect_header_mapping, iter_data_rows


def _strip(s):
    if s is None:
        return ""
    return str(s).strip()


def _nr_to_str(x) -> str:
    """Return integer-like numbers as canonical int-string, else trimmed string."""
    s = _strip(x).replace(",", ".")
    if not s:
        return ""
    try:
        f = float(s)
        if f.is_integer():
            n = int(f)
            if 0 <= n < 1_000_000_000:
                return str(n)
        return _strip(x)
    except ValueError:
        return _strip(x)


def _extract_from_sheet(ws: Worksheet, max_scan_rows: int = 30) -> pd.DataFrame | None:
    header_row, nr_col, roomtype_col = detect_header_mapping(ws, max_scan_rows)
    if header_row is None or roomtype_col is None:
        return None

    rows: List[Tuple[str, str]] = []
    for r in iter_data_rows(ws, header_row):
        rt = ws.cell(row=r, column=roomtype_col).value
        roomtype_s = _strip(rt)
        if not roomtype_s:
            continue
        if nr_col is not None:
            nr = ws.cell(row=r, column=nr_col).value
            nr_s = _nr_to_str(nr)
        else:
            nr_s = ""
        rows.append((nr_s, roomtype_s))

    df = pd.DataFrame(rows, columns=["Nr", "Roomtype"])
    df["Nr"] = df["Nr"].fillna("").astype(str).map(_strip)
    df["Roomtype"] = df["Roomtype"].fillna("").astype(str).map(_strip)
    df = df[(df["Nr"] != "") | (df["Roomtype"] != "")]
    df = df.drop_duplicates(subset=["Nr", "Roomtype"]).reset_index(drop=True)
    return df if len(df) else None


def extract_workbook(xlsx_path: Path, max_scan_rows: int = 30) -> pd.DataFrame:
    """Extracts (Nr, Roomtype) from all sheets that have recognizable headers."""
    wb = load_wb(xlsx_path)
    parts: List[pd.DataFrame] = []
    for ws in wb.worksheets:
        df = _extract_from_sheet(ws, max_scan_rows=max_scan_rows)
        if df is not None and len(df):
            parts.append(df)
    if not parts:
        raise ValueError("No sheets with recognizable headers (Nr/Bezeichnung) found.")
    out = pd.concat(parts, axis=0, ignore_index=True)
    out = out.drop_duplicates(subset=["Nr", "Roomtype"]).reset_index(drop=True)
    return out


def extract_to_csv(
    xlsx_path: Path, out_csv: Path, max_scan_rows: int = 30
) -> pd.DataFrame:
    df = extract_workbook(xlsx_path, max_scan_rows=max_scan_rows)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_ALL)
    return df
