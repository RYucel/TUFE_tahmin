"""Metrik ve seçim skoru testleri (küçük örneklerde elle doğrulama)."""
import numpy as np
import pandas as pd
import pytest

from src import metrics as MX
from src import selection as SEL
from src import backtest as BT
from src.transforms import to_log


def test_mae_small_sample():
    # %35 gerçekleşme, %32 tahmin → 3 yüzde puan hata
    assert MX.mae(np.array([32.0 - 35.0])) == pytest.approx(3.0)
    assert MX.mae(np.array([3.0, -1.0, 2.0])) == pytest.approx(2.0)


def test_rmse_and_me():
    err = np.array([3.0, -1.0])
    assert MX.rmse(err) == pytest.approx(np.sqrt(5.0))
    assert MX.mean_error(err) == pytest.approx(1.0)


def test_mase_with_shared_denominator():
    err = np.array([2.0, -4.0])
    assert MX.mase(err, 2.0) == pytest.approx(1.5)
    assert MX.mase(err, np.array([2.0, 4.0])) == pytest.approx(1.0)


def test_mase_denominator_is_common_across_models():
    """Payda tüm modeller için AYNI olmalı; modelin kendi penceresinden gelmez."""
    origins = pd.period_range("2016-01", periods=30, freq="M")
    rows = []
    for m, scale in (("naive_mevsimsel_12", 1.0), ("baska_model", 5.0)):
        for i, o in enumerate(origins):
            rows.append({"origin": o, "model": m, "target": "c6",
                         "target_end": o + 6, "pred": 0.0, "actual": 0.0,
                         "err": scale * (1.0 if i % 2 else -1.0)})
    scored = pd.DataFrame(rows)
    den = BT.mase_denominators(scored, "naive_mevsimsel_12", min_obs=2)
    per_origin = den.groupby("origin")["mase_den"].nunique()
    assert (per_origin <= 1).all()
    ok = den[den["mase_den"].notna()]
    assert np.allclose(ok["mase_den"].to_numpy(), 1.0)   # referanstan gelir, 5.0'dan değil


def test_mase_denominator_only_uses_realized():
    origins = pd.period_range("2016-01", periods=20, freq="M")
    rows = [{"origin": o, "model": "naive_mevsimsel_12", "target": "c12",
             "target_end": o + 12, "pred": 0.0, "actual": 0.0, "err": 1.0}
            for o in origins]
    den = BT.mase_denominators(pd.DataFrame(rows), "naive_mevsimsel_12", min_obs=1)
    first = den[den["origin"] == origins[0]].iloc[0]
    assert first["den_n"] == 0                      # henüz hiçbir hedef gerçekleşmedi


def test_seasonal_naive_test_mase_need_not_be_one():
    """Mevsimsel naive'in MASE'si tanım gereği 1 DEĞİLDİR (payda farklı alt kümeden)."""
    origins = pd.period_range("2016-01", periods=40, freq="M")
    rows = []
    for i, o in enumerate(origins):
        rows.append({"origin": o, "model": "naive_mevsimsel_12", "target": "c6",
                     "target_end": o + 6, "pred": 0.0, "actual": 0.0,
                     "err": float(i)})     # zamanla büyüyen hata
    scored = pd.DataFrame(rows)
    den = BT.mase_denominators(scored, "naive_mevsimsel_12", min_obs=2)
    d = scored.merge(den, on=["origin", "target"])
    val = MX.mase(d["err"].to_numpy(), d["mase_den"].to_numpy())
    assert np.isfinite(val)
    assert val != pytest.approx(1.0)


def test_selection_score_formula():
    rows = []
    for model, (ye, c6, c12) in {"A": (2.0, 1.0, 4.0), "B": (1.0, 3.0, 3.0)}.items():
        for t, e in (("yearend", ye), ("c6", c6), ("c12", c12)):
            for k in range(15):
                o = pd.Period("2016-01", "M") + k
                rows.append({"origin": o, "model": model, "target": t,
                             "target_end": o + 6, "pred": e, "actual": 0.0, "err": e})
    scores = SEL.selection_scores(pd.DataFrame(rows),
                                  {"yearend": 0.6, "c6": 0.3, "c12": 0.1}, 12)
    a = scores[scores["model"] == "A"].iloc[0]
    b = scores[scores["model"] == "B"].iloc[0]
    assert a["S"] == pytest.approx(0.6 * 2 + 0.3 * 1 + 0.1 * 4)   # 1.9
    assert b["S"] == pytest.approx(0.6 * 1 + 0.3 * 3 + 0.1 * 3)   # 1.8
    assert scores.sort_values("S").iloc[0]["model"] == "B"


def test_common_origins_restriction():
    rows = []
    for k in range(10):
        o = pd.Period("2016-01", "M") + k
        rows.append({"origin": o, "model": "A", "target": "c6",
                     "target_end": o + 6, "pred": 0.0, "actual": 0.0, "err": 1.0})
        if k < 5:
            rows.append({"origin": o, "model": "B", "target": "c6",
                         "target_end": o + 6, "pred": 0.0, "actual": 0.0, "err": 0.1})
    scored = pd.DataFrame(rows)
    common = SEL.common_origins(scored, "c6", ["A", "B"])
    assert len(common) == 5


def test_interval_score_and_coverage():
    actual = np.array([1.0, 5.0, 3.0])
    lo, hi = np.array([0.0, 0.0, 0.0]), np.array([4.0, 4.0, 4.0])
    cov, n = MX.coverage(actual, lo, hi)
    assert n == 3 and cov == pytest.approx(2 / 3)
    isc = MX.interval_score(actual, lo, hi, alpha=0.2)
    assert isc > 4.0     # dışarıda kalan gözlem ceza ekler


def test_block_bootstrap_is_deterministic_with_seed():
    rng = np.random.default_rng(1)
    ea, eb = rng.normal(0, 1, 40), rng.normal(0, 2, 40)
    blocks = np.repeat(np.arange(10), 4)
    r1 = MX.block_bootstrap_diff(ea, eb, blocks, 200, seed=7)
    r2 = MX.block_bootstrap_diff(ea, eb, blocks, 200, seed=7)
    assert r1 == r2
    assert r1["n_blocks"] == 10
