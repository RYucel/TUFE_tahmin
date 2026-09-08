"""Dönüşümler ve ekonomik hesaplamalar.

Birim sözleşmesi (tüm modüllerde geçerlidir):
  * ``r``  : aylık yüzde değişim (ör. 3.0443 = %3,0443)
  * ``z``  : ``log(1 + r/100)`` — 100 ile ÇARPILMAMIŞ log değişim
  * dönem enflasyonları her zaman yüzde (pp) cinsinden döner.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

ArrayLike = np.ndarray | pd.Series | list


def to_log(r: ArrayLike) -> np.ndarray | pd.Series:
    """Aylık yüzde değişimi log değişime çevirir."""
    if isinstance(r, pd.Series):
        return np.log1p(r.astype(float) / 100.0)
    return np.log1p(np.asarray(r, dtype=float) / 100.0)


def to_pct(z: ArrayLike) -> np.ndarray | pd.Series:
    """Log değişimi aylık yüzde değişime çevirir."""
    if isinstance(z, pd.Series):
        return (np.expm1(z.astype(float))) * 100.0
    return np.expm1(np.asarray(z, dtype=float)) * 100.0


def compound_pct(z: ArrayLike) -> float:
    """Log değişim dizisinin bileşik yüzde karşılığı: 100*(exp(Σz)-1)."""
    arr = np.asarray(z, dtype=float)
    if arr.size == 0:
        return 0.0
    return float(np.expm1(arr.sum()) * 100.0)


def compound_path_pct(z: ArrayLike) -> np.ndarray:
    """Kümülatif bileşik enflasyon yolu (her ufuk için)."""
    arr = np.asarray(z, dtype=float)
    return np.expm1(np.cumsum(arr)) * 100.0


def combine_pct(a_pct: float, b_pct: float) -> float:
    """İki yüzde değişimi bileşik olarak birleştirir (toplamaz)."""
    return float(((1.0 + a_pct / 100.0) * (1.0 + b_pct / 100.0) - 1.0) * 100.0)


def yearend_from_ytd(realized_ytd_pct: float, future_z: ArrayLike) -> float:
    """Yılsonu (Aralık/Aralık) enflasyonu.

    ``realized_ytd_pct`` başlangıç ayına kadar gerçekleşmiş YTD, ``future_z``
    başlangıçtan Aralık'a kadarki log değişim tahminleridir.
    """
    arr = np.asarray(future_z, dtype=float)
    return float(((1.0 + realized_ytd_pct / 100.0) * np.exp(arr.sum()) - 1.0) * 100.0)


def yoy_pct(z_last12: ArrayLike) -> float:
    """Son 12 ayın log değişim toplamından yıllık enflasyon."""
    arr = np.asarray(z_last12, dtype=float)
    if arr.size != 12:
        raise ValueError(f"Yıllık değişim tam 12 ay gerektirir, {arr.size} verildi.")
    return compound_pct(arr)


def ytd_pct(z_series: pd.Series, period: pd.Period) -> float:
    """İlgili ayın bir önceki yılın Aralık ayına göre değişimi.

    Ocak ayında hesap yeni yıl için yeniden başlar (yalnız Ocak'ın kendisi).
    """
    start = pd.Period(year=period.year, month=1, freq="M")
    seg = z_series[(z_series.index >= start) & (z_series.index <= period)]
    if len(seg) != period.month:
        raise ValueError(f"{period} için YTD hesaplanamıyor: {len(seg)}/{period.month} ay mevcut.")
    return compound_pct(seg.to_numpy())


def half_year_pct(z_series: pd.Series, year: int, half: int) -> float:
    """Takvim yarıyılı enflasyonu (1: Ocak–Haziran, 2: Temmuz–Aralık)."""
    m0, m1 = (1, 6) if half == 1 else (7, 12)
    start = pd.Period(year=year, month=m0, freq="M")
    end = pd.Period(year=year, month=m1, freq="M")
    seg = z_series[(z_series.index >= start) & (z_series.index <= end)]
    if len(seg) != 6:
        raise ValueError(f"{year}/{half}. yarıyıl için 6 ay gerekli, {len(seg)} bulundu.")
    return compound_pct(seg.to_numpy())


def synthetic_chain_index(r: pd.Series, base: float = 100.0) -> pd.Series:
    """Oranlardan üretilen SENTETİK ZİNCİR ENDEKS.

    API endeks düzeyi vermediği için bu endeks resmî endeks değildir. Pozitiftir;
    negatif enflasyon aylarında düşebilir, monoton artması gerekmez.
    """
    z = to_log(r.astype(float))
    idx = base * np.exp(np.cumsum(z.to_numpy()))
    return pd.Series(idx, index=r.index, name="sentetik_zincir_endeks")


def realized_targets(z: pd.Series, origin: pd.Period, horizon: int) -> dict:
    """Bir başlangıç için gerçekleşmiş hedefler (mevcut olanlar).

    Dönem gerçekleşmeleri her zaman aylık seriden aynı formülle hesaplanır.
    """
    out: dict = {}
    for h in range(1, horizon + 1):
        per = origin + h
        if per in z.index:
            out[f"m{h}"] = float(to_pct(z.loc[per]))
    for h in (6, 12):
        seg = z[(z.index > origin) & (z.index <= origin + h)]
        if len(seg) == h:
            out[f"c{h}"] = compound_pct(seg.to_numpy())
    # yılsonu
    dec = pd.Period(year=origin.year, month=12, freq="M")
    if origin.month < 12:
        seg = z[(z.index > origin) & (z.index <= dec)]
        if len(seg) == (12 - origin.month):
            try:
                base_ytd = ytd_pct(z, origin)
                out["yearend"] = yearend_from_ytd(base_ytd, seg.to_numpy())
            except ValueError:
                pass
    return out
