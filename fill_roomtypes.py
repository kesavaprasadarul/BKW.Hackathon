import os
from pathlib import Path
from src.roomtypes.models import Cfg
from src.roomtypes.service import process


def main():
    project_number = "8"

    cfg = Cfg()
    mapping_csv = Path(f"static/evals/mappings/mapping_{project_number}.csv")
    target_xlsx = Path(f"static/evals/input_excel/proj_{project_number}_test.xlsx")
    output_xlsx = Path(
        f"static/evals/output_excel/proj_{project_number}_test_output.xlsx"
    )
    report_csv = Path(f"static/evals/preds/preds_{project_number}.csv")

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY not set (check .env.local or environment)")

    process(mapping_csv, target_xlsx, output_xlsx, report_csv, cfg)


if __name__ == "__main__":
    main()
