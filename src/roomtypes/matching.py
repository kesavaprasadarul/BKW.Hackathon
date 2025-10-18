"""Matching"""

import re
import unicodedata
from typing import List, Tuple
import pandas as pd

_NON_ALNUM_SPACE = re.compile(r"[^a-z0-9\s]")
_SPACEY = re.compile(r"\s+")
_HEADER_JUNK = re.compile(r"[\s\.\:\;\-\_\/]+")

_BEZ_ALIASES = {
    "raumbezeichnung",
    "raumbezeich",
    "raumbez",
    "raumbezeichng",
    "raumbezchung",
    "raum-bezeichnung",
}
_NR_ALIASES = {"nummerraumtyp", "nummer raumtyp"}


def fold(s: str) -> str:
    """Fold string by removing punctuation and whitespace"""
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    return s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")


def norm_text(x) -> str:
    """Normalize text by removing punctuation and whitespace"""
    if x is None:
        return ""
    s = fold(str(x))
    s = _NON_ALNUM_SPACE.sub(" ", s)
    return _SPACEY.sub(" ", s).strip()


def norm_key(x) -> str:
    """Normalize key by removing punctuation and whitespace"""
    if x is None:
        return ""
    return _HEADER_JUNK.sub("", fold(str(x)))


def load_mapping(mapping_csv) -> pd.DataFrame:
    """Load mapping from CSV file"""
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


def fulltext_score(q: str, c: str) -> float:
    """Calculate fulltext score"""
    if not q or not c:
        return 0.0
    if q == c:
        return 1.0
    if q in c:
        return 0.98
    qt, ct = q.split(), c.split()
    if not qt or not ct:
        return 0.0
    qs, cs = set(qt), set(ct)
    inter = len(qs & cs)
    coverage = inter / max(1, len(qs))
    jaccard = inter / max(1, len(qs | cs))
    pref = 0.05 if c.startswith(qt[0]) else 0.0
    suff = 0.03 if c.endswith(qt[-1]) else 0.0
    return min(1.0, 0.7 * coverage + 0.3 * jaccard + pref + suff)


def best_match_fulltext(query: str, mapping_df: pd.DataFrame, k: int):
    """Find best match fulltext"""
    qn = norm_text(query)
    if not qn:
        return "", "", 0.0, [], []
    scores = [fulltext_score(qn, cn) for cn in mapping_df["_norm"]]
    bi = int(max(range(len(scores)), key=lambda i: scores[i])) if scores else 0
    bscore = float(scores[bi]) if scores else 0.0
    bnr = mapping_df.iat[bi, mapping_df.columns.get_loc("Nr")] if scores else ""
    brt = mapping_df.iat[bi, mapping_df.columns.get_loc("Roomtype")] if scores else ""
    idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[
        : min(k, len(scores))
    ]
    cands = (
        mapping_df.iloc[idxs][["Nr", "Roomtype"]]
        .reset_index(drop=True)
        .to_dict(orient="records")
    )
    cand_scores = [float(scores[i]) for i in idxs]
    return bnr, brt, bscore, cands, cand_scores
