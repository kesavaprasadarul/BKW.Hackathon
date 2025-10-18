import os
from pathlib import Path
from src.roomtypes.models import Cfg
from src.roomtypes.service import process


def main():
    cfg = Cfg()
    mapping_csv = Path("mapping.csv")
    target_xlsx = Path("proj_5_test.xlsx")
    output_xlsx = Path("proj_5_test_output.xlsx")
    report_csv = Path("match_report.csv")

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY not set (check .env.local or environment)")

    process(mapping_csv, target_xlsx, output_xlsx, report_csv, cfg)


if __name__ == "__main__":
    main()
