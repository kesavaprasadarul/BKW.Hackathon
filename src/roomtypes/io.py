"""IO"""

from pathlib import Path
import pandas as pd


def read_sheets(xlsx_path: Path):
    """Read sheets from Excel file"""
    xls = pd.ExcelFile(xlsx_path)
    for sheet in xls.sheet_names:
        raw = pd.read_excel(xlsx_path, sheet_name=sheet, header=None)
        yield sheet, raw


def write_output(out_sheets: list[tuple[str, pd.DataFrame]], output_xlsx: Path) -> None:
    """Write output to Excel file"""
    with pd.ExcelWriter(output_xlsx, engine="openpyxl") as w:
        for sheet, df in out_sheets:
            df.to_excel(w, sheet_name=sheet, index=False)


def write_report(rows: list[dict], report_csv: Path) -> None:
    """Write report to CSV file"""
    pd.DataFrame(rows).to_csv(report_csv, index=False, encoding="utf-8-sig")
