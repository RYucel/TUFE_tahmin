"""Zaman sızıntısı testleri."""
import numpy as np
import pandas as pd
import pytest

from src.features import build_feature_frame, build_direct_dataset, LAGS, ROLL
from src.transforms import to_log
from src import backtest as BT
from src import calibration as CAL


def _z(n=120, start="2015-01"):
    rng = np.random.default_rng(0)
    idx = pd.period_range(start, periods=n, freq="M")
    return pd.Series(to_log(rng.normal(1.5, 0.8, n)), index=idx)


def test_features_use_only_past_and_present():
    z = _z()
    feats = build_feature_frame(z)
    t = z.index[80]
    # t satırındaki değerler yalnızca z[<= t] ile aynı kalmalı
    truncated = build_feature_frame(z[z.index <= t])
    pd.testing.assert_series_equal(feats.loc[t].dropna(), truncated.loc[t].dropna(),
                                   check_names=False)


def test_lag1_is_current_month():
    z = _z()
    feats = build_feature_frame(z)
    t = z.index[50]
    assert feats.loc[t, "lag1"] == pytest.approx(z.loc[t])


def test_rolling_features_contain_no_future():
    z = _z()
    feats = build_feature_frame(z)
    t = z.index[60]
    for w in ROLL:
        assert feats.loc[t, f"ma{w}"] == pytest.approx(z[z.index <= t].iloc[-w:].mean())


def test_direct_targets_respect_training_cutoff():
    z = _z()
    feats = build_feature_frame(z)
    cutoff = z.index[90]
    for h in (1, 6, 12):
        X, y = build_direct_dataset(z, h, feats, cutoff)
        assert len(X) == len(y)
        # her eğitim örneğinin hedefi kesime kadar gerçekleşmiş olmalı
        assert all((t + h) <= cutoff for t in X.index)
        for t in X.index:
            assert y.loc[t] == pytest.approx(z.loc[t + h])


def test_backtest_uses_only_history_up_to_origin(monkeypatch):
    from src.models.base import ModelSpec, BaseModel

    seen = {}

    class Spy(BaseModel):
        name, family, min_obs = "spy", "test", 1

        def fit(self, z, exog=None):
            seen["max"] = z.index.max()
            seen["n"] = len(z)
            return self

        def predict(self, h):
            return np.zeros(h)

    z = _z()
    origin = z.index[70]
    spec = ModelSpec("spy", Spy, "test", 0, min_history=1)
    BT.run_backtest(z, [spec], [origin], 12, progress=False)
    assert seen["max"] == origin


def test_window_is_respected():
    from src.models.base import ModelSpec, BaseModel
    seen = {}

    class Spy(BaseModel):
        name, family, min_obs = "spy", "test", 1

        def fit(self, z, exog=None):
            seen["n"] = len(z)
            return self

        def predict(self, h):
            return np.zeros(h)

    z = _z()
    spec = ModelSpec("spy60", Spy, "test", 60, min_history=1)
    BT.run_backtest(z, [spec], [z.index[100]], 12, progress=False)
    assert seen["n"] == 60


def test_calibration_uses_only_realized_errors():
    """Kalibrasyonda origin'den sonra biten hedeflerin hatası kullanılamaz."""
    idx = pd.period_range("2015-01", periods=60, freq="M")
    rows = []
    for i, o in enumerate(idx):
        rows.append({"origin": o, "model": "m", "target": "c12",
                     "target_end": o + 12, "pred": 0.0,
                     "actual": float(i), "err": -float(i)})
    scored = pd.DataFrame(rows)
    cfg = {"calibration": {"levels": [0.80], "min_samples": {0.80: 1},
                           "max_history": 100, "method": "conformal_absolute",
                           "update": "expanding"}}
    cal = CAL.calibrate(scored, "m", cfg)
    # origin idx[13] için yalnızca target_end <= origin olan hatalar (i=0) kullanılabilir
    row = cal[cal["origin"] == idx[13]].iloc[0]
    assert row["n_cal"] == 2   # target_end 2016-01 ve 2016-02 <= 2016-02
    early = cal[cal["origin"] == idx[0]].iloc[0]
    assert early["n_cal"] == 0
    assert np.isnan(early["lo80"])
