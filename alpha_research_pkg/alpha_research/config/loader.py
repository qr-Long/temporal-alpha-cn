from __future__ import annotations
import yaml
from pathlib import Path
from typing import Any, Dict

def load_config(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise ValueError("Config must be a YAML mapping at top level.")
    return cfg
