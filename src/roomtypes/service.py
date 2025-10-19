"""Service"""

from pathlib import Path
from typing import Dict, List
import pandas as pd

from src.roomtypes.io import (
    load_wb,
    save_wb,
    detect_header_xlsx,
    ensure_nr_column,
    iter_data_rows,
)
from src.roomtypes.models import Cfg
from src.roomtypes.matching import (
    load_mapping,
    norm_text,
    best_match_fulltext,
)
from src.roomtypes.cache import load_cache, save_cache
from src.ai import AIService


def _validate_against_catalog(res: dict, catalog: List[Dict[str, str]]) -> dict:
    """Validate against catalog"""
    nr = (res.get("nr") or "").strip()
    rt = (res.get("roomtype") or "").strip()

    def _c_nr(c: Dict[str, str]) -> str:
        """Get NR from catalog"""
        return str(c.get("nr", c.get("Nr", ""))).strip()

    def _c_rt(c: Dict[str, str]) -> str:
        """Get Roomtype from catalog"""
        return str(c.get("roomtype", c.get("Roomtype", ""))).strip()

    if nr and any(_c_nr(c) == nr for c in catalog):
        """If NR is in catalog, return result"""
        return res

    nrt = norm_text(rt)
    for c in catalog:
        crt = norm_text(_c_rt(c))
        if nrt and (nrt == crt or nrt in crt or crt in nrt):
            return {
                "nr": _c_nr(c),
                "roomtype": _c_rt(c),
                "confidence": float(res.get("confidence", 0.0)),
                "rationale": res.get("rationale", ""),
            }
    # fallback: invalidate
    return {
        "nr": "",
        "roomtype": "",
        "confidence": 0.0,
        "rationale": res.get("rationale", ""),
    }


def convert_to_int(value: str) -> int:
    """Convert to integer"""
    val = str(value).strip()
    if val.replace(".", "", 1).isdigit():
        return int(float(val))
    return val


def process(
    mapping_csv: Path, target_xlsx: Path, output_xlsx: Path, report_csv: Path, cfg: Cfg
):
    """
    Reads the Excel file with openpyxl and writes ONLY the target cells (Nummer Raumtyp column),
    preserving all original formatting and formulas in other cells/sheets.
    """
    ai = AIService()
    mapping = load_mapping(mapping_csv)
    catalog = [
        {"nr": r["Nr"], "roomtype": r["Roomtype"]} for _, r in mapping.iterrows()
    ]
    cache = load_cache(cfg.cache_path)

    def use_fts() -> bool:
        return (cfg.matching_mode or "hybrid").lower() == "hybrid"

    report_rows: List[dict] = []

    wb = load_wb(target_xlsx)

    for ws in wb.worksheets:
        header_row, bez_col, nr_col = detect_header_xlsx(ws, cfg.max_scan_rows)
        if header_row is None or bez_col is None:
            continue

        nr_col = ensure_nr_column(ws, header_row, nr_col)

        unresolved_row_idxs: List[int] = []
        unresolved_queries: List[str] = []
        key_for_row: Dict[int, str] = {}
        fts_cache_updates: Dict[str, dict] = {}

        for r in iter_data_rows(ws, header_row):
            rb_cell = ws.cell(row=r, column=bez_col)
            rb_val = rb_cell.value
            if rb_val is None or not str(rb_val).strip():
                continue

            q = str(rb_val)
            qkey = norm_text(q)
            key_for_row[r] = qkey

            hit = cache.get(qkey)
            if hit:
                conf = float(hit.get("confidence", 0.0))
                is_fts_hit = (hit.get("rationale") or "").strip().lower() == "fts"
                cache_hit_allowed = conf >= cfg.ai_threshold and hit.get("nr")
                if cache_hit_allowed and (use_fts() or not is_fts_hit):
                    val = convert_to_int(hit["nr"])
                    ws.cell(row=r, column=nr_col).value = val
                    report_rows.append(
                        {
                            "Sheet": ws.title,
                            "RowIndex": r,
                            "Raum-Bezeichnung": q,
                            "MatchedRoomtype": hit.get("roomtype", ""),
                            "Nr": hit.get("nr", ""),
                            "Score": round(conf, 4),
                            "Method": "cache",
                            "AI_Confidence": round(conf, 4),
                            "AI_Rationale": hit.get("rationale", ""),
                            "Accepted": True,
                        }
                    )
                    continue

            if use_fts():
                nr, rt, score, _, _ = best_match_fulltext(q, mapping, cfg.top_k)
                if score >= cfg.fts_threshold and nr:
                    val = convert_to_int(nr)
                    ws.cell(row=r, column=nr_col).value = val
                    report_rows.append(
                        {
                            "Sheet": ws.title,
                            "RowIndex": r,
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
                    continue

            unresolved_row_idxs.append(r)
            unresolved_queries.append(q)
            report_rows.append(
                {
                    "Sheet": ws.title,
                    "RowIndex": r,
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
            ai_results = ai.choose_roomtypes(
                queries=unresolved_queries,
                catalog=catalog,
                batch_size=cfg.batch_size,
            )
            validated: Dict[str, dict] = {}
            for q in unresolved_queries:
                key = norm_text(q)
                res = ai_results.get(
                    key, {"nr": "", "roomtype": "", "confidence": 0.0, "rationale": ""}
                )
                validated[key] = _validate_against_catalog(res, catalog)

            cache.update(fts_cache_updates)
            cache.update(validated)
            save_cache(cfg.cache_path, cache)

            for r in unresolved_row_idxs:
                res = cache.get(
                    key_for_row[r],
                    {"nr": "", "roomtype": "", "confidence": 0.0, "rationale": ""},
                )
                conf = float(res.get("confidence", 0.0))
                nr_val = res.get("nr", "")
                rt_val = res.get("roomtype", "")
                accepted = bool(nr_val and conf >= cfg.ai_threshold)

                if nr_val:
                    val = convert_to_int(nr_val)
                    ws.cell(row=r, column=nr_col).value = (
                        val  # only touch the target cell
                    )

                for rr in reversed(report_rows):
                    if rr["Sheet"] == ws.title and rr["RowIndex"] == r:
                        rr.update(
                            {
                                "MatchedRoomtype": rt_val,
                                "Nr": nr_val if accepted else (nr_val or ""),
                                "Score": round(conf, 4),
                                "Method": (
                                    (
                                        "gemini"
                                        if accepted
                                        else (
                                            "gemini_low_conf"
                                            if nr_val
                                            else "gemini_no_answer"
                                        )
                                    )
                                    if use_fts()
                                    else (
                                        "llm_only"
                                        if accepted
                                        else (
                                            "llm_only_low_conf"
                                            if nr_val
                                            else "llm_only_no_answer"
                                        )
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
                save_cache(cfg.cache_path, cache)

    save_wb(wb, output_xlsx)
    pd.DataFrame(report_rows).to_csv(report_csv, index=False, encoding="utf-8-sig")
