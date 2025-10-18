import sys
import re
import unicodedata
import argparse
import pandas as pd
from pathlib import Path
from difflib import SequenceMatcher


def normalize_text(s: str) -> str:
    """Lowercase, strip, remove punctuation/extra spaces, normalize umlauts; keep letters/digits."""
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def token_set_similarity(a: str, b: str) -> float:
    na, nb = normalize_text(a), normalize_text(b)
    if not na or not nb:
        return 0.0
    ta, tb = set(na.split()), set(nb.split())
    inter = " ".join(sorted(ta & tb))
    r1 = SequenceMatcher(None, inter, " ".join(sorted(tb))).ratio() if inter else 0.0
    r2 = SequenceMatcher(None, inter, " ".join(sorted(ta))).ratio() if inter else 0.0
    r3 = SequenceMatcher(None, na, nb).ratio()
    return max(r1, r2, r3)


def normalize_header(x):
    if pd.isna(x):
        return ""
    s = str(x).strip().lower()
    s = re.sub(r"[\s\.\:\;\-\_\/]+", "", s)
    return s


def find_column(df: pd.DataFrame, wanted: set, max_scan_rows: int = 30):
    for r in range(min(max_scan_rows, len(df))):
        row_vals = df.iloc[r, :]
        for c, v in row_vals.items():
            nv = normalize_header(v)
            if nv in wanted:
                return r, c
    return None, None


def find_headers_target(df: pd.DataFrame, max_scan_rows: int = 30):
    bezeichnung_aliases = {
        "raumbezeichnung",
        "raum-bezeichnung",
        "raumbez",
        "raumbezchung",
        "raumbezeichng",
        "raumbezeich",
    }
    nr_aliases = {"raum-nr", "raumnr", "raumnummer", "raum-no", "raumno"}
    bez_row, bez_col = find_column(df, bezeichnung_aliases, max_scan_rows=max_scan_rows)
    nr_row, nr_col = find_column(df, nr_aliases, max_scan_rows=max_scan_rows)
    header_row = None
    if bez_row is not None and nr_row is not None:
        header_row = min(bez_row, nr_row)
    elif bez_row is not None:
        header_row = bez_row
    elif nr_row is not None:
        header_row = nr_row
    return header_row, bez_col, nr_col


def load_mapping(mapping_csv: Path) -> pd.DataFrame:
    m = pd.read_csv(mapping_csv, dtype=str).fillna("")
    col_map = {c.lower(): c for c in m.columns}

    nr_col = col_map.get("nr") or "Nr"
    rt_col = col_map.get("roomtype") or "Roomtype"
    m = m.rename(columns={nr_col: "Nr", rt_col: "Roomtype"})

    m["Nr"] = m["Nr"].astype(str).str.strip()
    m["Roomtype"] = m["Roomtype"].astype(str).str.strip()
    m["_norm"] = m["Roomtype"].apply(normalize_text)

    return m[["Nr", "Roomtype", "_norm"]]


def best_match(s: str, mapping_df: pd.DataFrame):
    best = ("", "", 0.0)
    for _, row in mapping_df.iterrows():
        score = token_set_similarity(s, row["Roomtype"])
        if score > best[2]:
            best = (row["Nr"], row["Roomtype"], score)

    return best


def fill_target(
    mapping_csv: Path,
    target_xlsx: Path,
    output_xlsx: Path,
    report_csv: Path,
    threshold: float = 0.75,
):
    mapping = load_mapping(mapping_csv)
    xls = pd.ExcelFile(target_xlsx)
    report_rows = []
    out_sheets = {}

    for sheet in xls.sheet_names:
        df = pd.read_excel(target_xlsx, sheet_name=sheet, header=None)
        header_row, bez_col, nr_col = find_headers_target(df, max_scan_rows=30)
        if header_row is None or bez_col is None:
            out_sheets[sheet] = df
            continue

        headers = df.iloc[header_row].tolist()
        data = df.iloc[header_row + 1 :].copy()
        data.columns = [
            str(h) if not pd.isna(h) else f"Unnamed_{i}" for i, h in enumerate(headers)
        ]

        def col_by_predicate(cols, keys):
            for c in cols:
                if normalize_header(c) in keys:
                    return c
            return None

        bez_name = col_by_predicate(
            data.columns,
            {"raumbezeichnung", "raum-bezeichnung", "raumbez", "raumbezeich"},
        )
        nr_name = col_by_predicate(
            data.columns,
            {"nummer raumtyp"},
        )

        if nr_name is None:
            nr_name = "Nummer Raumtyp"
            data[nr_name] = ""

        for idx, row in data.iterrows():
            rb = row.get(bez_name, "")
            if pd.isna(rb) or str(rb).strip() == "":
                continue
            nr, rt, score = best_match(str(rb), mapping)
            if score >= threshold:
                data.at[idx, nr_name] = nr
            report_rows.append(
                {
                    "Sheet": sheet,
                    "RowIndex": idx,
                    "Raum-Bezeichnung": str(rb),
                    "MatchedRoomtype": rt,
                    "Nr": nr,
                    "Score": round(score, 4),
                    "Accepted": bool(score >= threshold),
                }
            )

        out_sheets[sheet] = data

    with pd.ExcelWriter(output_xlsx, engine="openpyxl") as writer:
        for sheet, d in out_sheets.items():
            d.to_excel(writer, sheet_name=sheet, index=False)

    pd.DataFrame(report_rows).to_csv(report_csv, index=False, encoding="utf-8-sig")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mapping_csv", type=Path, help="CSV with columns ['Nr','Roomtype']"
    )
    parser.add_argument(
        "target_xlsx", type=Path, help="Excel containing 'Raum-Bezeichnung'"
    )
    parser.add_argument("output_xlsx", type=Path, help="Path to write filled Excel")
    parser.add_argument("report_csv", type=Path, help="Path to write match report CSV")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.75,
        help="Similarity threshold for accepting a match (0..1)",
    )
    args = parser.parse_args()

    fill_target(
        args.mapping_csv,
        args.target_xlsx,
        args.output_xlsx,
        args.report_csv,
        threshold=args.threshold,
    )
    print(f"Done. Wrote {args.output_xlsx} and {args.report_csv}")


if __name__ == "__main__":
    main()
