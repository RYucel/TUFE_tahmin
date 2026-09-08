"""Yapılandırma yükleme yardımcıları."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_config(path: str | os.PathLike | None = None) -> dict[str, Any]:
    cfg_path = Path(path) if path else ROOT / "config.yaml"
    with open(cfg_path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    cfg["_root"] = str(ROOT)
    cfg["_config_path"] = str(cfg_path)
    return cfg


def out_dir(cfg: dict, *parts: str) -> Path:
    p = Path(cfg["_root"]) / cfg["report"]["out_dir"]
    for part in parts:
        p = p / part
    p.mkdir(parents=True, exist_ok=True)
    return p
