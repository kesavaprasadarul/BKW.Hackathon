"""Models"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Cfg:
    """Configuration"""

    fts_threshold: float = 0.85
    ai_threshold: float = 0.75
    max_scan_rows: int = 30
    top_k: int = 25
    batch_size: int = 25
    cache_path: Path = Path("cache/roomtype_gemini_cache.json")
    matching_mode: str = "hybrid"  # hybrid, llm_only
