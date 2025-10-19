"""Cache"""

import json
from pathlib import Path
from typing import Dict, Any


def load_cache(p: Path) -> Dict[str, Any]:
    """Load cache from file"""
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_cache(p: Path, d: Dict[str, Any]) -> None:
    """Save cache to file"""
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
