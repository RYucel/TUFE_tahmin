"""Dönüşüm ve ekonomik hesaplama testleri."""
import numpy as np
import pandas as pd
import pytest

from src.transforms import (to_log, to_pct, compound_pct, compound_path_pct,
                            combine_pct, yearend_from_ytd, yoy_pct, ytd_pct,
                            half_year_pct, synthetic_chain_index, realized_targets)


def test_log_roundtrip():
    r = np.array([3.0443, -1.25, 0.0, 25.5045, 12.3])
    assert np.allclose(to_pct(to_log(r)), r, atol=1e-10)


def test_log_units_not_scaled():
    # z = log(1 + r/100), 100 ile ÇARPILMAMIŞ
    assert to_log(np.array([100.0]))[0] == pytest.approx(np.log(2.0))


def test_compound_is_not_sum():
    r = np.array([10.0, 10.0])
    z = to_log(r)
    assert compound_pct(z) == pytest.approx(21.0)     # 1.1*1.1-1
    assert compound_pct(z) != pytest.approx(20.0)     # toplama DEĞİL


def test_compound_path():
    z = to_log(np.array([1.0, 2.0, 3.0]))
    path = compound_path_pct(z)
    assert path[0] == pytest.approx(1.0)
    assert path[1] == pytest.approx(3.02)
    assert path[2] == pytest.approx(6.1106, abs=1e-4)


def test_combine_pct():
    assert combine_pct(20.0, 10.0) == pytest.approx(32.0)


def test_yearend_from_ytd():
    # gerçekleşmiş YTD %24,0081; kalan 4 ayın her biri %2
    fz = to_log(np.array([2.0] * 4))
    got = yearend_from_ytd(24.0081, fz)
    exp = (1.240081 * 1.02 ** 4 - 1) * 100
    assert got == pytest.approx(exp)


def test_yoy_requires_12():
    with pytest.raises(ValueError):
        yoy_pct(np.zeros(11))
    assert yoy_pct(to_log(np.array([1.0] * 12))) == pytest.approx((1.01 ** 12 - 1) * 100)


def _series(vals, start="2024-01"):
    idx = pd.period_range(start, periods=len(vals), freq="M")
    return pd.Series(to_log(np.asarray(vals, float)), index=idx)


def test_ytd_definition_and_january_reset():
    z = _series([1.0] * 14, start="2024-01")           # Oca24 … Şub25
    assert ytd_pct(z, pd.Period("2024-03", "M")) == pytest.approx((1.01 ** 3 - 1) * 100)
    # Ocak'ta YTD yeni yıl için yeniden başlar → yalnızca Ocak ayı
    assert ytd_pct(z, pd.Period("2025-01", "M")) == pytest.approx(1.0)
    assert ytd_pct(z, pd.Period("2025-02", "M")) == pytest.approx((1.01 ** 2 - 1) * 100)


def test_ytd_raises_when_incomplete():
    z = _series([1.0] * 3, start="2024-02")
    with pytest.raises(ValueError):
        ytd_pct(z, pd.Period("2024-04", "M"))


def test_half_year():
    z = _series([1.0] * 12, start="2025-01")
    assert half_year_pct(z, 2025, 1) == pytest.approx((1.01 ** 6 - 1) * 100)
    assert half_year_pct(z, 2025, 2) == pytest.approx((1.01 ** 6 - 1) * 100)


def test_december_over_december_equals_ytd_of_december():
    z = _series([1.0] * 12, start="2025-01")
    assert ytd_pct(z, pd.Period("2025-12", "M")) == pytest.approx((1.01 ** 12 - 1) * 100)


def test_synthetic_index_positive_and_can_fall():
    r = pd.Series([5.0, -3.0, -10.0, 2.0],
                  index=pd.period_range("2024-01", periods=4, freq="M"))
    idx = synthetic_chain_index(r)
    assert (idx > 0).all()                    # pozitif olmalı
    assert idx.iloc[2] < idx.iloc[1]          # negatif enflasyonda DÜŞEBİLİR
    assert not idx.is_monotonic_increasing    # monoton artması gerekmez


def test_realized_targets_yearend_matches_manual():
    z = _series([2.0] * 12, start="2026-01")
    out = realized_targets(z, pd.Period("2026-08", "M"), 12)
    assert "yearend" in out
    assert out["yearend"] == pytest.approx((1.02 ** 12 - 1) * 100)
    assert "c6" not in out                    # yalnızca 4 ay gerçekleşmiş
