import os, json, re, unicodedata
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import pandas as pd
from dataclasses import dataclass

from pydantic import BaseModel
from google import genai
import dotenv

dotenv.load_dotenv()


@dataclass(frozen=True)
class Cfg:
    fts_threshold: float = 0.05
    ai_threshold: float = 0.75
    max_scan_rows: int = 30
    top_k: int = 25
    batch_size: int = 25
    gemini_model: str = "gemini-2.5-flash-lite"
    cache_path: Path = Path("cache/roomtype_gemini_cache.json")


class MatchResult(BaseModel):
    nr: str
    roomtype: str
    confidence: float
    rationale: str


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


def _fold(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    return s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")


def norm_text(x) -> str:
    if x is None:
        return ""
    s = _fold(str(x))
    s = _NON_ALNUM_SPACE.sub(" ", s)
    return _SPACEY.sub(" ", s).strip()


def norm_key(x) -> str:
    if x is None:
        return ""
    return _HEADER_JUNK.sub("", _fold(str(x)))


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


def fulltext_score(q: str, c: str) -> float:
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


def _cache_load(p: Path) -> Dict[str, dict]:
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _cache_save(p: Path, d: Dict[str, dict]):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def detect_header(df: pd.DataFrame, cfg: Cfg):
    for r in range(min(cfg.max_scan_rows, len(df))):
        row = df.iloc[r, :]
        m = {norm_key(v): i for i, v in enumerate(row)}
        bez_idx = next((m[k] for k in _BEZ_ALIASES if k in m), None)
        nr_idx = next((m[k] for k in _NR_ALIASES if k in m), None)
        if bez_idx is not None or nr_idx is not None:
            return r, bez_idx, nr_idx
    return None, None, None


def _validate_against_catalog(
    res: MatchResult, catalog: List[Dict[str, str]]
) -> MatchResult:
    nr = (res.nr or "").strip()
    rt = (res.roomtype or "").strip()

    def _c_nr(c: Dict[str, str]) -> str:
        return str(c.get("nr", c.get("Nr", ""))).strip()

    def _c_rt(c: Dict[str, str]) -> str:
        return str(c.get("roomtype", c.get("Roomtype", ""))).strip()

    if nr and any(_c_nr(c) == nr for c in catalog):
        return res

    nrt = norm_text(rt)
    for c in catalog:
        crt = norm_text(_c_rt(c))
        if nrt and (nrt == crt or nrt in crt or crt in nrt):
            return MatchResult(
                nr=_c_nr(c),
                roomtype=_c_rt(c),
                confidence=res.confidence,
                rationale=res.rationale,
            )

    return MatchResult(nr="", roomtype="", confidence=0.0, rationale=res.rationale)


def gemini_choose_batch(
    queries: List[str], catalog: List[Dict[str, str]], model: str
) -> List[MatchResult]:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
    sys_prompt = (
        "You are given a fixed catalog of room types. For each query, choose the best matching item from the catalog. "
        "If none fits well, set confidence < 0.85. "
        "Return ONLY a JSON array; one object per input in the same order. "
        'Each object: {"nr": str, "roomtype": str, "confidence": float, "rationale": str}.'
    )
    payload = {"catalog": catalog, "queries": queries}

    try:
        resp = client.models.generate_content(
            model=model,
            contents=[sys_prompt, json.dumps(payload, ensure_ascii=False)],
            config={
                "response_mime_type": "application/json",
                "response_schema": list[MatchResult],
            },
        )
        outs: List[MatchResult] = resp.parsed or []
    except Exception as e:
        outs = []

    if len(outs) < len(queries):
        pad = [
            MatchResult(nr="", roomtype="", confidence=0.0, rationale="no_response")
        ] * (len(queries) - len(outs))
        outs = list(outs) + pad
    elif len(outs) > len(queries):
        outs = outs[: len(queries)]

    return outs


def process(
    mapping_csv: Path, target_xlsx: Path, output_xlsx: Path, report_csv: Path, cfg: Cfg
):
    mapping = load_mapping(mapping_csv)
    catalog = [
        {"nr": r["Nr"], "roomtype": r["Roomtype"]} for _, r in mapping.iterrows()
    ]
    cache = _cache_load(cfg.cache_path)

    xls = pd.ExcelFile(target_xlsx)
    report_rows, out_sheets = [], []

    for sheet in xls.sheet_names:
        raw = pd.read_excel(target_xlsx, sheet_name=sheet, header=None)
        header_row, bez_idx, nr_idx = detect_header(raw, cfg)
        if header_row is None or bez_idx is None:
            out_sheets.append((sheet, raw))
            continue

        headers = raw.iloc[header_row].tolist()
        data = raw.iloc[header_row + 1 :].copy()
        data.columns = [
            str(h) if pd.notna(h) else f"Unnamed_{i}" for i, h in enumerate(headers)
        ]
        bez_name = data.columns[bez_idx]
        nr_name = (
            data.columns[nr_idx]
            if nr_idx is not None and nr_idx < len(data.columns)
            else "Nummer Raumtyp"
        )
        if nr_name not in data.columns:
            data[nr_name] = ""

        unresolved_idx, unresolved_queries = [], []
        key_for_idx: Dict[int, str] = {}
        fts_cache_updates: Dict[str, dict] = {}

        for idx, rb in data[bez_name].items():
            if pd.isna(rb) or not str(rb).strip():
                continue
            q = str(rb)
            qkey = norm_text(q)
            key_for_idx[int(idx)] = qkey

            hit = cache.get(qkey)
            if (
                hit
                and float(hit.get("confidence", 0.0)) >= cfg.ai_threshold
                and hit.get("nr")
            ):
                data.at[idx, nr_name] = hit["nr"]
                report_rows.append(
                    {
                        "Sheet": sheet,
                        "RowIndex": int(idx),
                        "Raum-Bezeichnung": q,
                        "MatchedRoomtype": hit.get("roomtype", ""),
                        "Nr": hit.get("nr", ""),
                        "Score": round(float(hit.get("confidence", 0.0)), 4),
                        "Method": "cache",
                        "AI_Confidence": round(float(hit.get("confidence", 0.0)), 4),
                        "AI_Rationale": hit.get("rationale", ""),
                        "Accepted": True,
                    }
                )
                continue

            nr, rt, score, _, _ = best_match_fulltext(q, mapping, cfg.top_k)
            if score >= cfg.fts_threshold and nr:
                data.at[idx, nr_name] = nr
                report_rows.append(
                    {
                        "Sheet": sheet,
                        "RowIndex": int(idx),
                        "Raum-Bezeichnung": q,
                        "MatchedRoomtype": rt,
                        "Nr": nr,
                        "Score": round(float(score), 4),
                        "Method": "fts",
                        "AI_Confidence": None,
                        "AI_Rationale": "fts",
                        "Accepted": True,
                    }
                )
                fts_cache_updates[qkey] = {
                    "nr": nr,
                    "roomtype": rt,
                    "confidence": float(score),
                    "rationale": "fts",
                }
            else:
                unresolved_idx.append(int(idx))
                unresolved_queries.append(q)
                report_rows.append(
                    {
                        "Sheet": sheet,
                        "RowIndex": int(idx),
                        "Raum-Bezeichnung": q,
                        "MatchedRoomtype": "",
                        "Nr": "",
                        "Score": 0.0,
                        "Method": "pending",
                        "AI_Confidence": None,
                        "AI_Rationale": "",
                        "Accepted": False,
                    }
                )

        if unresolved_queries:
            uniq, seen = [], set()
            for q in unresolved_queries:
                k = norm_text(q)
                if k not in seen:
                    seen.add(k)
                    uniq.append(q)

            results_map: Dict[str, dict] = {}
            for s in range(0, len(uniq), cfg.batch_size):
                qs = uniq[s : s + cfg.batch_size]
                outs = gemini_choose_batch(qs, catalog, cfg.gemini_model)
                outs = [_validate_against_catalog(o, catalog) for o in outs]
                for q, o in zip(qs, outs):
                    results_map[norm_text(q)] = {
                        "nr": o.nr,
                        "roomtype": o.roomtype,
                        "confidence": float(o.confidence),
                        "rationale": o.rationale,
                    }

            cache.update(fts_cache_updates)
            cache.update(results_map)
            _cache_save(cfg.cache_path, cache)

            for i in unresolved_idx:
                res = cache.get(
                    key_for_idx[i],
                    {"nr": "", "roomtype": "", "confidence": 0.0, "rationale": ""},
                )
                conf = float(res.get("confidence", 0.0))
                nr_val = res.get("nr", "")
                rt_val = res.get("roomtype", "")
                accepted = bool(nr_val and conf >= cfg.ai_threshold)

                if nr_val:
                    data.at[i, nr_name] = nr_val

                for rr in reversed(report_rows):
                    if rr["Sheet"] == sheet and rr["RowIndex"] == i:
                        rr.update(
                            {
                                "MatchedRoomtype": rt_val,
                                "Nr": nr_val if accepted else (nr_val or ""),
                                "Score": round(conf, 4),
                                "Method": (
                                    "gemini"
                                    if accepted
                                    else (
                                        "gemini_low_conf"
                                        if nr_val
                                        else "gemini_no_answer"
                                    )
                                ),
                                "AI_Confidence": round(conf, 4),
                                "AI_Rationale": res.get("rationale", ""),
                                "Accepted": accepted,
                            }
                        )
                        break
        else:
            if fts_cache_updates:
                cache.update(fts_cache_updates)
                _cache_save(cfg.cache_path, cache)

        out_sheets.append((sheet, data))

    with pd.ExcelWriter(output_xlsx, engine="openpyxl") as w:
        for sheet, df in out_sheets:
            df.to_excel(w, sheet_name=sheet, index=False)
    pd.DataFrame(report_rows).to_csv(report_csv, index=False, encoding="utf-8-sig")


def main():
    cfg = Cfg()
    mapping_csv = Path("mapping.csv")
    target_xlsx = Path("proj_5_test.xlsx")
    output_xlsx = Path("proj_5_test_output.xlsx")
    report_csv = Path("match_report.csv")
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY not set")
    process(mapping_csv, target_xlsx, output_xlsx, report_csv, cfg)


if __name__ == "__main__":
    main()
