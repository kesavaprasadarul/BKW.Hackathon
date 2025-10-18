"""Service"""

from pathlib import Path
from typing import Dict, List
import pandas as pd

from src.roomtypes.models import Cfg
from src.roomtypes.matching import (
    load_mapping,
    norm_text,
    best_match_fulltext,
    detect_header,
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


def process(
    mapping_csv: Path, target_xlsx: Path, output_xlsx: Path, report_csv: Path, cfg: Cfg
):
    """Process roomtypes"""
    ai = AIService()

    mapping = load_mapping(mapping_csv)
    catalog = [
        {"nr": r["Nr"], "roomtype": r["Roomtype"]} for _, r in mapping.iterrows()
    ]
    cache = load_cache(cfg.cache_path)

    from src.roomtypes.io import read_sheets, write_output, write_report

    report_rows, out_sheets = [], []

    for sheet, raw in read_sheets(target_xlsx):
        header_row, bez_idx, nr_idx = detect_header(raw, cfg.max_scan_rows)
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

        # Pass 1: cache / FTS
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

        # Pass 2: AI for unresolved
        if unresolved_queries:
            ai_results = ai.choose_roomtypes(
                queries=unresolved_queries,
                catalog=catalog,
                batch_size=cfg.batch_size,
            )
            # validate, merge into cache
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

                # update the last row we appended for that (sheet, index)
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
                save_cache(cfg.cache_path, cache)

        out_sheets.append((sheet, data))

    from src.roomtypes.io import write_output, write_report

    write_output(out_sheets, output_xlsx)
    write_report(report_rows, report_csv)
