import pandas as pd
from pathlib import Path
from typing import Optional


def _to_int_or_none(x) -> Optional[int]:
    if pd.isna(x):
        return None
    s = str(x).strip()
    if not s:
        return None
    s = s.replace(",", ".")
    try:
        f = float(s)
        if f.is_integer():
            return int(f)
    except Exception:
        pass
    ds = "".join(ch for ch in s if ch.isdigit())
    return int(ds) if ds.isdigit() else None


def _canon_id_str(x) -> str:
    i = _to_int_or_none(x)
    return str(i) if i is not None else ""


def evaluate(gt_csv: Path, preds_csv: Path):
    gt = pd.read_csv(gt_csv, dtype=str).fillna("")
    pr = pd.read_csv(preds_csv, dtype=str).fillna("")

    if "ID" not in gt.columns:
        raise ValueError("gt.csv must have column 'ID'")
    if "Nr" not in pr.columns:
        raise ValueError("preds.csv must have column 'Nr'")

    n = min(len(gt), len(pr))
    if len(gt) != len(pr):
        print(
            f"Length mismatch: gt={len(gt)} rows, preds={len(pr)} rows. Comparing first {n} rows in order."
        )

    gt_can = gt.loc[: n - 1, "ID"].map(_canon_id_str)
    pr_can = pr.loc[: n - 1, "Nr"].map(_canon_id_str)

    same = gt_can == pr_can
    valid_mask = gt_can != ""
    same_valid = same[valid_mask]

    acc = float(same_valid.mean()) if same_valid.size else 0.0
    n_valid = int(valid_mask.sum())

    print("=== Evaluation Summary (order-only, ID vs Nr) ===")
    print(f"{'rows_compared':>16}: {n}")
    print(f"{'valid_gt_rows':>16}: {n_valid}")
    print(f"{'match_rate':>16}: {acc:.4f}")

    out = pd.DataFrame(
        {
            "Row": range(n),
            "GT_ID_raw": gt.loc[: n - 1, "ID"].to_list(),
            "PRED_Nr_raw": pr.loc[: n - 1, "Nr"].to_list(),
            "GT_ID": gt_can.to_list(),
            "PRED_Nr": pr_can.to_list(),
            "Match": same.to_list(),
        }
    )

    for col in ["Raum-Bezeichnung", "MatchedRoomtype"]:
        if col in pr.columns:
            out[col] = pr.loc[: n - 1, col].to_list()

    mism = out[~out["Match"]].copy()

    print("\n=== Sample mismatches (up to 20) ===")
    show_cols = [
        c
        for c in ["Row", "GT_ID", "PRED_Nr", "Raum-Bezeichnung", "MatchedRoomtype"]
        if c in out.columns
    ]
    if mism.empty:
        print("(none)")
    else:
        print(mism[show_cols].head(20).to_string(index=False))

    conf = (
        out.assign(gt_id=out["GT_ID"], pred_id=out["PRED_Nr"])
        .value_counts(["gt_id", "pred_id"])
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    return out, conf


if __name__ == "__main__":
    project_number = "8"
    gt_path = Path(f"static/evals/gt/gt_{project_number}.csv")
    preds_path = Path(f"static/evals/preds/preds_{project_number}.csv")

    detailed, confusion = evaluate(gt_path, preds_path)
    print("\nTop (GT_ID, PRED_Nr) pairs")
    print(confusion.head(15).to_string(index=False))
