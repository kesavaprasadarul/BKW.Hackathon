import argparse
import json
import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from google import genai
import dotenv

dotenv.load_dotenv()

_RE_NON_ALNUM_SPACE = re.compile(r"[^a-z0-9\s]")
_RE_SPACEY = re.compile(r"\s+")
_RE_HEADER_JUNK = re.compile(r"[\s\.\:\;\-\_\/]+")


def _fold(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return s


def norm_text(x) -> str:
    if x is None:
        return ""
    s = _fold(str(x))
    s = _RE_NON_ALNUM_SPACE.sub(" ", s)
    s = _RE_SPACEY.sub(" ", s).strip()
    return s


def norm_key(x) -> str:
    if x is None:
        return ""
    s = _fold(str(x))
    return _RE_HEADER_JUNK.sub("", s)


@dataclass(frozen=True)
class Settings:
    threshold: float = 0.85
    ai_threshold: float = 0.85
    top_k: int = 25
    max_scan_rows: int = 30
    use_gemini: bool = True
    gemini_model: str = "gemini-2.5-flash"


_BEZ_ALIASES = {
    "raumbezeichnung",
    "raumbezeich",
    "raumbez",
    "raumbezeichng",
    "raumbezchung",
    "raum-bezeichnung",
}
_NR_ALIASES = {"nummerraumtyp", "nummer raumtyp"}


def load_mapping(mapping_csv: Path) -> pd.DataFrame:
    m = pd.read_csv(mapping_csv, dtype=str).fillna("")
    col_map = {c.lower(): c for c in m.columns}
    nr_col = col_map.get("nr") or "Nr"
    rt_col = col_map.get("roomtype") or "Roomtype"
    m = m.rename(columns={nr_col: "Nr", rt_col: "Roomtype"})
    m["Nr"] = m["Nr"].astype(str).str.strip()
    m["Roomtype"] = m["Roomtype"].astype(str).str.strip()
    m = m.drop_duplicates(subset=["Roomtype"]).reset_index(drop=True)
    m["_norm"] = m["Roomtype"].map(norm_text)
    return m[["Nr", "Roomtype", "_norm"]]


def fulltext_score(query_norm: str, cand_norm: str) -> float:
    if not query_norm or not cand_norm:
        return 0.0
    if query_norm == cand_norm:
        return 1.0
    if query_norm in cand_norm:
        return 0.98
    q_tokens = query_norm.split()
    c_tokens = cand_norm.split()
    if not q_tokens or not c_tokens:
        return 0.0
    q_set, c_set = set(q_tokens), set(c_tokens)
    inter = len(q_set & c_set)
    coverage = inter / max(1, len(q_set))
    jaccard = inter / max(1, len(q_set | c_set))
    prefix_bonus = 0.05 if cand_norm.startswith(q_tokens[0]) else 0.0
    suffix_bonus = 0.03 if cand_norm.endswith(q_tokens[-1]) else 0.0
    return min(1.0, 0.7 * coverage + 0.3 * jaccard + prefix_bonus + suffix_bonus)


def best_match_fulltext(query: str, mapping_df: pd.DataFrame, k: int):
    qn = norm_text(query)
    if not qn:
        return "", "", 0.0, [], []
    scores = [fulltext_score(qn, cn) for cn in mapping_df["_norm"]]
    best_i = int(max(range(len(scores)), key=lambda i: scores[i])) if scores else 0
    best_score = float(scores[best_i]) if scores else 0.0
    best_nr = mapping_df.iat[best_i, mapping_df.columns.get_loc("Nr")] if scores else ""
    best_rt = (
        mapping_df.iat[best_i, mapping_df.columns.get_loc("Roomtype")] if scores else ""
    )
    idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[
        : min(k, len(scores))
    ]
    cand_rows = mapping_df.iloc[idxs][["Nr", "Roomtype"]].reset_index(drop=True)
    cand_scores = [float(scores[i]) for i in idxs]
    return (
        best_nr,
        best_rt,
        best_score,
        cand_rows.to_dict(orient="records"),
        cand_scores,
    )


def _detect_header_row_and_cols(
    df: pd.DataFrame, cfg: Settings
) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    for r in range(min(cfg.max_scan_rows, len(df))):
        row = df.iloc[r, :]
        key_to_idx: Dict[str, int] = {norm_key(v): i for i, v in enumerate(row)}
        bez_idx = next((key_to_idx[k] for k in _BEZ_ALIASES if k in key_to_idx), None)
        nr_idx = next((key_to_idx[k] for k in _NR_ALIASES if k in key_to_idx), None)
        if bez_idx is not None or nr_idx is not None:
            return r, bez_idx, nr_idx
    return None, None, None


def gemini_choose(
    query: str,
    candidates: List[Dict[str, str]],
    scores: List[float],
    model: str = "gemini-2.0-flash-lite",
) -> Tuple[str, str, float, str]:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    sys_prompt = (
        "Match a German room description to the best room type from candidates. "
        "Prefer exact or near-exact semantic matches. If none fits well, choose confidence < 0.85. "
        'Return JSON: {"nr": str, "roomtype": str, "confidence": float, "rationale": str}.'
    )
    content = {
        "query": query,
        "candidates": [
            {"nr": c["Nr"], "roomtype": c["Roomtype"], "score_hint": s}
            for c, s in zip(candidates, scores)
        ],
    }
    resp = client.models.generate_content(
        model=model,
        contents=[sys_prompt, json.dumps(content, ensure_ascii=False)],
    )
    text = (resp.text or "").strip()
    try:
        j = json.loads(text)
        nr = str(j.get("nr", "")).strip()
        rt = str(j.get("roomtype", "")).strip()
        conf = float(j.get("confidence", 0.0))
        rationale = str(j.get("rationale", "")).strip()
        return nr, rt, conf, rationale
    except Exception:
        return "", "", 0.0, ""


def fill_target(
    mapping_csv: Path,
    target_xlsx: Path,
    output_xlsx: Path,
    report_csv: Path,
    cfg: Settings,
):
    mapping = load_mapping(mapping_csv)
    xls = pd.ExcelFile(target_xlsx)
    report_rows: List[Dict[str, object]] = []
    out_sheets: Dict[str, pd.DataFrame] = {}
    for sheet in xls.sheet_names:
        raw = pd.read_excel(target_xlsx, sheet_name=sheet, header=None)
        header_row, bez_col_idx, nr_col_idx = _detect_header_row_and_cols(raw, cfg)
        if header_row is None or bez_col_idx is None:
            out_sheets[sheet] = raw
            continue
        headers = raw.iloc[header_row].tolist()
        data = raw.iloc[header_row + 1 :].copy()
        data.columns = [
            str(h) if pd.notna(h) else f"Unnamed_{i}" for i, h in enumerate(headers)
        ]
        bez_name = data.columns[bez_col_idx]
        if nr_col_idx is not None and nr_col_idx < len(data.columns):
            nr_name = data.columns[nr_col_idx]
        else:
            nr_name = "Nummer Raumtyp"
            data[nr_name] = ""
        for idx, rb in data[bez_name].items():
            if pd.isna(rb) or not str(rb).strip():
                continue
            nr, rt, score, cands, scores = best_match_fulltext(
                str(rb), mapping, cfg.top_k
            )
            used = "fulltext"
            ai_conf = None
            ai_rt = ""
            ai_nr = ""
            rationale = ""
            if score < cfg.threshold and cfg.use_gemini:
                ai_nr, ai_rt, ai_conf, rationale = gemini_choose(
                    str(rb), cands, scores, model=cfg.gemini_model
                )
                if ai_conf is not None and ai_conf >= cfg.ai_threshold and ai_nr:
                    nr, rt, score = ai_nr, (ai_rt or rt), float(ai_conf)
                    used = "gemini"
            if score >= cfg.threshold:
                data.at[idx, nr_name] = nr
            report_rows.append(
                {
                    "Sheet": sheet,
                    "RowIndex": int(idx),
                    "Raum-Bezeichnung": str(rb),
                    "MatchedRoomtype": rt,
                    "Nr": nr,
                    "Score": round(float(score), 4),
                    "Method": used,
                    "AI_Confidence": (
                        None if ai_conf is None else round(float(ai_conf), 4)
                    ),
                    "AI_Rationale": rationale,
                    "Accepted": bool(float(score) >= cfg.threshold),
                }
            )
        out_sheets[sheet] = data
    with pd.ExcelWriter(output_xlsx, engine="openpyxl") as writer:
        for sheet, d in out_sheets.items():
            d.to_excel(writer, sheet_name=sheet, index=False)
    pd.DataFrame(report_rows).to_csv(report_csv, index=False, encoding="utf-8-sig")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mapping_csv", type=Path)
    p.add_argument("target_xlsx", type=Path)
    p.add_argument("output_xlsx", type=Path)
    p.add_argument("report_csv", type=Path)
    p.add_argument("--threshold", type=float, default=Settings.threshold)
    p.add_argument("--ai_threshold", type=float, default=Settings.ai_threshold)
    p.add_argument("--top_k", type=int, default=Settings.top_k)
    p.add_argument("--max_scan_rows", type=int, default=Settings.max_scan_rows)
    p.add_argument("--use_gemini", type=bool, default=Settings.use_gemini)
    p.add_argument("--gemini_model", type=str, default=Settings.gemini_model)
    args = p.parse_args()
    cfg = Settings(
        threshold=args.threshold,
        ai_threshold=args.ai_threshold,
        top_k=args.top_k,
        max_scan_rows=args.max_scan_rows,
        use_gemini=args.use_gemini,
        gemini_model=args.gemini_model,
    )
    fill_target(
        args.mapping_csv, args.target_xlsx, args.output_xlsx, args.report_csv, cfg
    )
    print(f"Done. Wrote {args.output_xlsx} and {args.report_csv}")


if __name__ == "__main__":
    main()
