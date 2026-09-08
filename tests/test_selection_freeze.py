"""Seçim dondurma, eğitim penceresinin korunması ve aşama kapıları."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src import selection as SEL
from src.config import load_config
from src.registry import build_specs
from src.models.base import slice_window


def test_load_frozen_raises_without_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="dondurulmuş seçim"):
        SEL.load_frozen(tmp_path / "yok.json")


def _scores(vals: dict) -> pd.DataFrame:
    rows = []
    for model, s in vals.items():
        rows.append({"model": model, "S": s, "uygun": True,
                     "MAE_yearend": s, "MAE_c6": s, "MAE_c12": s,
                     "n_yearend": 20, "n_c6": 20, "n_c12": 20})
    return pd.DataFrame(rows)


def test_tie_break_prefers_simpler_then_cheaper():
    cfg = load_config()
    scores = _scores({"karmasik": 1.000, "basit": 1.015, "cok_basit": 1.019})
    meta = {"karmasik": {"family": "lgbm", "complexity_rank": 6},
            "basit": {"family": "ets", "complexity_rank": 2},
            "cok_basit": {"family": "baseline", "complexity_rank": 0}}
    sel = SEL.choose(scores, meta, cfg, {"karmasik": 9.0, "basit": 1.0, "cok_basit": 0.1})
    # üçü de %2 içinde → en basit kazanır
    assert sel.winner == "cok_basit"


def test_tie_break_runtime_when_equal_complexity():
    cfg = load_config()
    scores = _scores({"a": 1.000, "b": 1.005})
    meta = {"a": {"family": "ets", "complexity_rank": 2},
            "b": {"family": "theta", "complexity_rank": 2}}
    sel = SEL.choose(scores, meta, cfg, {"a": 5.0, "b": 0.5})
    assert sel.winner == "b"


def test_outside_threshold_keeps_best():
    cfg = load_config()
    scores = _scores({"iyi": 1.0, "basit_ama_kotu": 1.5})
    meta = {"iyi": {"family": "lgbm", "complexity_rank": 6},
            "basit_ama_kotu": {"family": "baseline", "complexity_rank": 0}}
    sel = SEL.choose(scores, meta, cfg, {"iyi": 9.0, "basit_ama_kotu": 0.1})
    assert sel.winner == "iyi"


def test_zero_score_case_uses_absolute_epsilon():
    cfg = load_config()
    scores = _scores({"mukemmel": 0.0, "digeri": 1e-12})
    meta = {"mukemmel": {"family": "a", "complexity_rank": 3},
            "digeri": {"family": "b", "complexity_rank": 1}}
    sel = SEL.choose(scores, meta, cfg, {"mukemmel": 1.0, "digeri": 1.0})
    assert "sıfıra yakın" in sel.rule
    assert sel.winner == "digeri"       # eşit skorda daha basit olan


def test_ensemble_members_from_distinct_families():
    cfg = load_config()
    scores = _scores({"a1": 1.0, "a2": 1.1, "b1": 1.2, "c1": 1.3})
    meta = {"a1": {"family": "ets", "complexity_rank": 2},
            "a2": {"family": "ets", "complexity_rank": 2},
            "b1": {"family": "arima", "complexity_rank": 4},
            "c1": {"family": "lgbm", "complexity_rank": 6}}
    sel = SEL.choose(scores, meta, cfg, {k: 1.0 for k in meta})
    assert sel.ensemble_members == ["a1", "b1", "c1"]


def test_freeze_roundtrip(tmp_path):
    cfg = load_config()
    scores = _scores({"a": 1.0, "b": 2.0})
    meta = {"a": {"family": "ets", "complexity_rank": 2},
            "b": {"family": "arima", "complexity_rank": 4}}
    sel = SEL.choose(scores, meta, cfg, {"a": 1.0, "b": 1.0})
    p = tmp_path / "frozen.json"
    SEL.freeze(sel, p, {"kazanan_yapilandirma": {"pencere_ay": 60}})
    loaded = SEL.load_frozen(p)
    assert loaded["winner"] == "a"
    assert loaded["frozen_extra"]["kazanan_yapilandirma"]["pencere_ay"] == 60


def test_selected_window_is_preserved_in_final_fit():
    """Seçim sonrası eğitim penceresi korunur (60 kazandıysa tüm geçmişe geçilmez)."""
    cfg = load_config()
    specs = {s.key: s for s in build_specs(cfg, items=None, include_timesfm=False)}
    spec = specs["SARIMA_w60"]
    assert spec.window == 60
    z = pd.Series(np.zeros(400), index=pd.period_range("1990-01", periods=400, freq="M"))
    assert len(slice_window(z, spec.window)) == 60
    assert len(slice_window(z, specs["SARIMA_wtum"].window)) == 400


def test_registry_has_all_required_baselines():
    cfg = load_config()
    keys = {s.key for s in build_specs(cfg, items=None, include_timesfm=False)}
    for req in ("naive_son_ay", "naive_mevsimsel_12", "ortalama_3ay",
                "ortalama_6ay", "ortalama_12ay"):
        assert req in keys
