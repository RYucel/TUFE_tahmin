"""Hata metrikleri, MASE ve blok bootstrap.

Tüm hedef metrikleri YÜZDE PUAN (pp) cinsindendir. Log ölçekte hesaplanan
hatalar dönem enflasyonu hatası olarak raporlanmaz.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def mae(err: np.ndarray) -> float:
    err = np.asarray(err, dtype=float)
    return float(np.mean(np.abs(err))) if err.size else float("nan")


def rmse(err: np.ndarray) -> float:
    err = np.asarray(err, dtype=float)
    return float(np.sqrt(np.mean(err ** 2))) if err.size else float("nan")


def mean_error(err: np.ndarray) -> float:
    """İşaretli ortalama hata (yanlılık)."""
    err = np.asarray(err, dtype=float)
    return float(np.mean(err)) if err.size else float("nan")


def mape(actual: np.ndarray, pred: np.ndarray) -> float:
    """Yalnızca destekleyici olarak raporlanır; ana seçim metriği DEĞİLDİR."""
    actual = np.asarray(actual, dtype=float)
    pred = np.asarray(pred, dtype=float)
    mask = np.abs(actual) > 1e-9
    if not mask.any():
        return float("nan")
    return float(np.mean(np.abs((actual[mask] - pred[mask]) / actual[mask])) * 100.0)


def mase(err: np.ndarray, denominator: np.ndarray | float) -> float:
    """Ortak paydalı MASE.

    ``denominator`` her gözlem için o BAŞLANGIÇTA tüm modeller için ortak olan
    mevsimsel-naive mutlak hata ortalamasıdır. Modelin kendi eğitim
    penceresinden türetilmez.
    """
    err = np.asarray(err, dtype=float)
    den = np.asarray(denominator, dtype=float)
    if err.size == 0:
        return float("nan")
    if den.ndim == 0:
        den = np.full(err.shape, float(den))
    mask = np.isfinite(den) & (den > 0) & np.isfinite(err)
    if not mask.any():
        return float("nan")
    return float(np.mean(np.abs(err[mask]) / den[mask]))


def interval_score(actual: np.ndarray, lower: np.ndarray, upper: np.ndarray,
                   alpha: float) -> float:
    """Winkler / interval score (düşük daha iyi)."""
    a, lo, hi = (np.asarray(x, dtype=float) for x in (actual, lower, upper))
    mask = np.isfinite(a) & np.isfinite(lo) & np.isfinite(hi)
    if not mask.any():
        return float("nan")
    a, lo, hi = a[mask], lo[mask], hi[mask]
    score = (hi - lo) + (2.0 / alpha) * (lo - a) * (a < lo) + (2.0 / alpha) * (a - hi) * (a > hi)
    return float(np.mean(score))


def wis(actual: np.ndarray, intervals: dict[float, tuple[np.ndarray, np.ndarray]],
        median: np.ndarray | None = None) -> float:
    """Weighted Interval Score — yalnızca mevcut kuantillerden hesaplanır.

    Tam CRPS DEĞİLDİR ve öyle sunulmaz; sınırlı sayıda aralıkla yaklaşıktır.
    """
    a = np.asarray(actual, dtype=float)
    k = len(intervals)
    if k == 0:
        return float("nan")
    total = np.zeros_like(a, dtype=float)
    weight_sum = 0.0
    if median is not None:
        med = np.asarray(median, dtype=float)
        total += 0.5 * np.abs(a - med)
        weight_sum += 0.5
    for level, (lo, hi) in intervals.items():
        alpha = 1.0 - level
        lo, hi = np.asarray(lo, float), np.asarray(hi, float)
        s = (hi - lo) + (2.0 / alpha) * (lo - a) * (a < lo) + (2.0 / alpha) * (a - hi) * (a > hi)
        total += (alpha / 2.0) * s
        weight_sum += alpha / 2.0
    out = total / (k + (0.5 if median is not None else 0.0))
    mask = np.isfinite(out)
    return float(np.mean(out[mask])) if mask.any() else float("nan")


def pinball_loss(actual: np.ndarray, quantile_pred: np.ndarray, q: float) -> float:
    a = np.asarray(actual, float)
    p = np.asarray(quantile_pred, float)
    mask = np.isfinite(a) & np.isfinite(p)
    if not mask.any():
        return float("nan")
    a, p = a[mask], p[mask]
    diff = a - p
    return float(np.mean(np.maximum(q * diff, (q - 1.0) * diff)))


def coverage(actual: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> tuple[float, int]:
    a, lo, hi = (np.asarray(x, float) for x in (actual, lower, upper))
    mask = np.isfinite(a) & np.isfinite(lo) & np.isfinite(hi)
    if not mask.any():
        return float("nan"), 0
    inside = (a[mask] >= lo[mask]) & (a[mask] <= hi[mask])
    return float(inside.mean()), int(mask.sum())


# --------------------------------------------------------------------------- #
# belirsizlik: blok bootstrap ve Diebold-Mariano
# --------------------------------------------------------------------------- #
def block_bootstrap_diff(err_a: np.ndarray, err_b: np.ndarray, blocks: np.ndarray,
                         n_boot: int = 1000, seed: int = 0,
                         stat: str = "mae") -> dict:
    """İki modelin eşleşmiş hataları arasındaki farkın blok bootstrap aralığı.

    ``blocks`` her gözlemin blok kimliğidir (ör. yılsonu için yıl). Bloklar
    yeniden örneklenerek örtüşen hataların bağımlılığı korunur.
    """
    rng = np.random.default_rng(seed)
    ea, eb = np.asarray(err_a, float), np.asarray(err_b, float)
    blocks = np.asarray(blocks)
    mask = np.isfinite(ea) & np.isfinite(eb)
    ea, eb, blocks = ea[mask], eb[mask], blocks[mask]
    if ea.size == 0:
        return {"diff": float("nan"), "lo95": float("nan"), "hi95": float("nan"), "n": 0}
    uniq = np.unique(blocks)
    idx_by_block = {b: np.where(blocks == b)[0] for b in uniq}

    def _stat(x: np.ndarray) -> float:
        return mae(x) if stat == "mae" else rmse(x)

    point = _stat(ea) - _stat(eb)
    draws = np.empty(n_boot)
    for i in range(n_boot):
        chosen = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([idx_by_block[b] for b in chosen])
        draws[i] = _stat(ea[idx]) - _stat(eb[idx])
    return {"diff": point, "lo95": float(np.percentile(draws, 2.5)),
            "hi95": float(np.percentile(draws, 97.5)), "n": int(ea.size),
            "n_blocks": int(len(uniq))}


def diebold_mariano(err_a: np.ndarray, err_b: np.ndarray, h: int = 1,
                    loss: str = "abs") -> dict:
    """Diebold–Mariano testi (İSTEĞE BAĞLI destekleyici analiz).

    Anlamsız sonuç eşdeğerlik kanıtı değildir; az örnek ve çoklu karşılaştırma
    sınırları raporda belirtilir.
    """
    ea, eb = np.asarray(err_a, float), np.asarray(err_b, float)
    mask = np.isfinite(ea) & np.isfinite(eb)
    ea, eb = ea[mask], eb[mask]
    n = ea.size
    if n < 8:
        return {"dm": float("nan"), "p": float("nan"), "n": n,
                "note": "Örnek sayısı testin geçerliliği için yetersiz."}
    la = np.abs(ea) if loss == "abs" else ea ** 2
    lb = np.abs(eb) if loss == "abs" else eb ** 2
    d = la - lb
    dbar = d.mean()
    gamma0 = np.var(d, ddof=0)
    var = gamma0
    for lag in range(1, min(h, n - 1)):
        cov = np.mean((d[lag:] - dbar) * (d[:-lag] - dbar))
        var += 2.0 * (1.0 - lag / h) * cov
    if var <= 0:
        return {"dm": float("nan"), "p": float("nan"), "n": n,
                "note": "Varyans tahmini pozitif değil."}
    dm = dbar / np.sqrt(var / n)
    # Harvey-Leybourne-Newbold küçük örnek düzeltmesi
    corr = np.sqrt(max((n + 1 - 2 * h + h * (h - 1) / n) / n, 1e-12))
    dm *= corr
    from scipy import stats
    p = 2.0 * (1.0 - stats.t.cdf(abs(dm), df=n - 1))
    return {"dm": float(dm), "p": float(p), "n": n, "note": ""}
