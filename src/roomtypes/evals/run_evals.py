import pandas as pd
import unicodedata
from pathlib import Path


def _norm(s: str) -> str:
    if pd.isna(s):
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    return s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")


def evaluate(gt_csv: Path, report_csv: Path, mapping_csv: Path):
    gt = pd.read_csv(gt_csv, dtype=str).fillna("")
    gt["ID"] = gt["ID"].astype(str).str.strip()
    gt["room_norm"] = gt["Roomtype"].map(_norm)

    mp = pd.read_csv(mapping_csv, dtype=str).fillna("")
    mp["Nr"] = mp["Nr"].astype(str).str.strip()
    mp["Roomtype"] = mp["Roomtype"].astype(str).str.strip()
    id_to_room = dict(zip(mp["Nr"], mp["Roomtype"]))

    gt_by_id = gt.drop_duplicates(subset=["ID"]).set_index("ID")["room_norm"].to_dict()
    gt_by_name = (
        gt.drop_duplicates(subset=["room_norm"]).set_index("room_norm")["ID"].to_dict()
    )

    rep = pd.read_csv(report_csv, dtype=str).fillna("")
    rep["Nr_str"] = rep["Nr"].astype(str).str.strip()
    rep["pred_room_norm"] = rep["MatchedRoomtype"].map(_norm)

    def as_int_like(x):
        try:
            f = float(str(x).replace(",", "."))
            return int(f) if f.is_integer() else None
        except ValueError:
            return None

    rep["Nr_int"] = rep["Nr_str"].map(as_int_like)
    rep["Nr_valid"] = rep["Nr_int"].map(
        lambda i: str(i) in gt_by_id if i is not None else False
    )
    rep["GT_ID"] = gt["ID"].tolist()[: len(rep)]

    rep["Text_valid"] = rep["pred_room_norm"].map(lambda n: n in gt_by_name)

    rep["Expected_name_from_ID"] = rep["Nr_int"].map(
        lambda i: gt_by_id.get(str(i)) if i is not None else None
    )
    rep["Expected_ID_from_name"] = rep["pred_room_norm"].map(
        lambda n: gt_by_name.get(n)
    )

    rep["Consistent"] = (
        rep["Nr_valid"]
        & rep["Text_valid"]
        & (rep["Expected_name_from_ID"] == rep["pred_room_norm"])
    )

    total = len(rep)
    strict_acc = rep["Consistent"].mean() if total else 0.0
    id_only_acc = rep["Nr_valid"].mean() if total else 0.0
    text_only_acc = rep["Text_valid"].mean() if total else 0.0

    print("=== Evaluation Summary (per report row) ===")
    print(f"{'rows':>16}: {total}")
    print(f"{'strict_accuracy':>16}: {strict_acc:.4f}  (ID↔Name must agree)")
    print(f"{'id_valid_rate':>16}: {id_only_acc:.4f}")
    print(f"{'text_valid_rate':>16}: {text_only_acc:.4f}")

    mism = rep[~rep["Consistent"]].copy()
    mism["Expected_room_from_mapping"] = mism["GT_ID"].map(id_to_room)
    cols = [
        "RowIndex",
        "Raum-Bezeichnung",
        "MatchedRoomtype",
        "Nr",
        "GT_ID",
        "Expected_room_from_mapping",
    ]
    print("\n=== Sample mismatches (up to 20) ===")
    print(mism[cols].head(20).to_string(index=False))

    conf = (
        rep.assign(
            gt_norm=rep["Expected_name_from_ID"], pred_norm=rep["pred_room_norm"]
        )
        .value_counts(["gt_norm", "pred_norm"])
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    return rep, conf


if __name__ == "__main__":
    gt_path = Path("data/roomtype_evals/gt/5.csv")
    report_path = Path("data/roomtype_evals/preds/match_report_5.csv")
    mapping_path = Path("mapping.csv")

    detailed, confusion = evaluate(gt_path, report_path, mapping_path)
    print("\n=== Top (gt_norm, pred_norm) pairs ===")
    print(confusion.head(15).to_string(index=False))
