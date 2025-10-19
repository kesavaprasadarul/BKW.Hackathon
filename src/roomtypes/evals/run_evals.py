import pandas as pd
import unicodedata
import re
from pathlib import Path
from typing import Optional, Tuple, Dict


def _strip_combining(s: str) -> str:
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


def _norm_text(s: str) -> str:
    """Robust text normalization: fold case, remove combining marks,
    transliterate German umlauts/ß, collapse whitespace."""
    if pd.isna(s):
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = _strip_combining(s)
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = re.sub(r"\s+", " ", s)
    return s


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
    ds = re.sub(r"\D", "", s)
    if ds.isdigit():
        return int(ds)
    return None


def _canon_id_str(x) -> Optional[str]:
    """Canonical ID as string: integer form without leading zeros (None if not int-like)."""
    i = _to_int_or_none(x)
    return str(i) if i is not None else None


def _build_gt_maps(
    gt_df: pd.DataFrame,
) -> Tuple[Dict[str, str], Dict[int, str], Dict[str, int]]:
    """Return:
      - gt_by_id_str: map '26' -> 'technikraume'
      - gt_by_id_int: map 26  -> 'technikraume'
      - gt_by_name   : map 'technikraume' -> 26
    using canonical normalization on both IDs and names.
    """
    tmp = gt_df.copy()
    tmp["ID_str"] = tmp["ID"].astype(str).str.strip()
    tmp["ID_int"] = tmp["ID_str"].map(_to_int_or_none)
    tmp["name_n"] = tmp["Roomtype"].map(_norm_text)

    gt_by_id_str: Dict[str, str] = {}
    gt_by_id_int: Dict[int, str] = {}
    gt_by_name: Dict[str, int] = {}
    for _, r in tmp.iterrows():
        name = r["name_n"]
        id_str = r["ID_str"]
        id_int = r["ID_int"]
        if id_str:
            canon = id_str.lstrip("0") or "0"
            gt_by_id_str[canon] = name
        if id_int is not None:
            gt_by_id_int[id_int] = name
        if name and (id_int is not None):
            gt_by_name[name] = id_int
    return gt_by_id_str, gt_by_id_int, gt_by_name


def evaluate(gt_csv: Path, report_csv: Path, mapping_csv: Path):
    gt = pd.read_csv(gt_csv, dtype=str).fillna("")
    gt_by_id_str, gt_by_id_int, gt_by_name = _build_gt_maps(gt)

    mp = pd.read_csv(mapping_csv, dtype=str).fillna("")
    mp["Nr_str"] = mp["Nr"].astype(str).str.strip()
    mp["Nr_can"] = mp["Nr_str"].map(lambda s: (_canon_id_str(s) or ""))
    mp["room_n"] = mp["Roomtype"].map(_norm_text)

    map_by_id_can: Dict[str, str] = {}
    map_by_name: Dict[str, str] = {}
    for _, r in mp.iterrows():
        if r["Nr_can"]:
            map_by_id_can[r["Nr_can"]] = r["room_n"]
        if r["room_n"]:
            map_by_name[r["room_n"]] = r["Nr_can"]

    gt_ids_can = set(k.lstrip("0") or "0" for k in gt_by_id_str.keys())
    map_ids_can = set(map_by_id_can.keys())
    id_diff = gt_ids_can ^ map_ids_can
    name_diff = set(gt_by_name.keys()) ^ set(map_by_name.keys())
    if id_diff or name_diff:
        print("GT and mapping differ for this project.")
        if id_diff:
            print("  ID symmetric diff (showing up to 10):", sorted(list(id_diff))[:10])
        if name_diff:
            print("  NAME symmetric diff (up to 10):", sorted(list(name_diff))[:10])

    rep = pd.read_csv(report_csv, dtype=str).fillna("")
    rep["Nr_str"] = rep["Nr"].astype(str).str.strip()
    rep["Nr_int"] = rep["Nr_str"].map(_to_int_or_none)
    rep["Nr_can"] = rep["Nr_str"].map(_canon_id_str)
    rep["pred_room_n"] = rep["MatchedRoomtype"].map(_norm_text)

    if "GT_ID" in rep.columns:
        rep["GT_ID_display"] = rep["GT_ID"].astype(str).str.strip()
    else:
        rep["GT_ID_display"] = rep["pred_room_n"].map(
            lambda n: (
                ""
                if n == ""
                else (
                    (
                        ""
                        if gt_by_name.get(n) is None and map_by_name.get(n) is None
                        else str(gt_by_name.get(n, map_by_name.get(n)))
                    )
                )
            )
        )

    def id_in_gt(row) -> bool:
        i = row["Nr_int"]
        s = row["Nr_can"]
        return (i in gt_by_id_int) or (s in gt_by_id_str if s is not None else False)

    def expected_name_from_id(row) -> Optional[str]:
        i = row["Nr_int"]
        s = row["Nr_can"]
        if i in gt_by_id_int:
            return gt_by_id_int[i]
        if s in gt_by_id_str:
            return gt_by_id_str[s]
        return None

    rep["Nr_valid"] = rep.apply(id_in_gt, axis=1)
    rep["Text_valid"] = rep["pred_room_n"].map(lambda n: n in gt_by_name)

    rep["Expected_name_from_ID"] = rep.apply(expected_name_from_id, axis=1)
    rep["Expected_ID_from_name"] = rep["pred_room_n"].map(lambda n: gt_by_name.get(n))

    rep["Consistent"] = (
        rep["Nr_valid"]
        & rep["Text_valid"]
        & (rep["Expected_name_from_ID"] == rep["pred_room_n"])
        & (
            rep["Expected_ID_from_name"].fillna(-1).astype(int)
            == rep["Nr_int"].fillna(-2).astype(int)
        )
    )

    total = len(rep)
    strict_acc = float(rep["Consistent"].mean()) if total else 0.0
    id_only_acc = float(rep["Nr_valid"].mean()) if total else 0.0
    text_only_acc = float(rep["Text_valid"].mean()) if total else 0.0

    print("=== Evaluation Summary (per report row) ===")
    print(f"{'rows':>16}: {total}")
    print(f"{'strict_accuracy':>16}: {strict_acc:.4f}  (ID↔Name must agree)")
    print(f"{'id_valid_rate':>16}: {id_only_acc:.4f}")
    print(f"{'text_valid_rate':>16}: {text_only_acc:.4f}")

    expected_from_mapping = rep["Nr_can"].map(lambda s: map_by_id_can.get(s or "", ""))
    mism = rep[~rep["Consistent"]].copy()
    mism["Expected_room_from_mapping"] = expected_from_mapping
    cols = [
        "RowIndex",
        "Raum-Bezeichnung",
        "MatchedRoomtype",
        "Nr",
        "GT_ID_display",
        "Expected_room_from_mapping",
    ]
    print("\n=== Sample mismatches (up to 20) ===")
    print(mism[cols].head(20).to_string(index=False))

    conf = (
        rep.assign(gt_norm=rep["Expected_name_from_ID"], pred_norm=rep["pred_room_n"])
        .value_counts(["gt_norm", "pred_norm"])
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    return rep, conf


if __name__ == "__main__":
    project_number = "5"

    gt_path = Path(f"data/evals/gt/gt_{project_number}.csv")
    report_path = Path(f"data/evals/preds/preds_{project_number}.csv")
    mapping_path = Path(f"data/evals/mappings/mapping_{project_number}.csv")

    detailed, confusion = evaluate(gt_path, report_path, mapping_path)
    print("\nTop (gt_norm, pred_norm) pairs")
    print(confusion.head(15).to_string(index=False))
