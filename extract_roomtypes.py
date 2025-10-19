from __future__ import annotations
import argparse
from pathlib import Path
from src.roomtypes.extract import extract_to_csv


def main():
    p = argparse.ArgumentParser(description="Extract (Nr, Roomtype) from workbook.")
    p.add_argument("input_xlsx", type=Path, help="Path to input .xlsx")
    p.add_argument("output_csv", type=Path, help="Path to output .csv")
    p.add_argument("--max-scan-rows", type=int, default=30, help="Header scan depth")
    args = p.parse_args()

    df = extract_to_csv(
        args.input_xlsx, args.output_csv, max_scan_rows=args.max_scan_rows
    )
    print(f"Wrote {len(df)} rows to {args.output_csv}")


if __name__ == "__main__":
    main()
