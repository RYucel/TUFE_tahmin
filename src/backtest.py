"""Kayan başlangıçlı (rolling-origin) geriye dönük test motoru.

Sızıntı kuralları:
  * Bir başlangıç ``t`` için model YALNIZCA ``z[<= t]`` ile eğitilir.
  * Yardımcı veriler de ``t``'ye kadar kesilir; doldurma/ölçekleme/faktör
    çıkarımı her dilimde yeniden yapılır.
  * Hedefler yalnızca gerçekleşmişse puanlanır.

Not: Geçmiş veri sürümleri (vintage) mevcut olmadığından bu değerlendirme
"son veri sürümüyle geriye dönük test"tir.
"""
from __future__ import annotations

import time
import traceback
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .models.base import ModelSpec, slice_window
from .transforms import (compound_pct, to_pct, ytd_pct, yearend_from_ytd)


@dataclass
class OriginResult:
    origin: pd.Period
    model: str
    z_path: np.ndarray | None
    runtime_sec: float
    status: str
    error: str = ""


def origins_for(z: pd.Series, start: pd.Period, end: pd.Period) -> list[pd.Period]:
    return [p for p in z.index if start <= p <= end]


def _fit_predict(spec: ModelSpec, z_hist: pd.Series, horizon: int) -> tuple[np.ndarray, float]:
    t0 = time.perf_counter()
    train = slice_window(z_hist, spec.window)
    if spec.transform == "pct":
        series = to_pct(train)
        model = spec.build().fit(series)
        pred_pct = np.asarray(model.predict(horizon), dtype=float)
        path = np.log1p(np.clip(pred_pct, -99.0, None) / 100.0)
    else:
        model = spec.build().fit(train)
        path = np.asarray(model.predict(horizon), dtype=float)
    if path.shape[0] != horizon or not np.all(np.isfinite(path)):
        raise ValueError(f"{spec.key}: geçersiz tahmin yolu (uzunluk {path.shape[0]}).")
    return path, time.perf_counter() - t0


def run_backtest(z: pd.Series, specs: list[ModelSpec], origins: list[pd.Period],
                 horizon: int = 12, progress: bool = True,
                 log=print) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Her (başlangıç, model) için 12 aylık log değişim yolunu üretir.

    Döner: (paths_df, failures_df)
      paths_df sütunları: origin, model, h, z_pred, runtime_sec
    """
    rows: list[dict] = []
    failures: list[dict] = []
    n_total = len(specs) * len(origins)
    done = 0
    for spec in specs:
        n_ok = n_fail = 0
        for origin in origins:
            done += 1
            z_hist = z[z.index <= origin]
            if len(z_hist) < spec.min_history:
                failures.append({"origin": str(origin), "model": spec.key,
                                 "sebep": "yetersiz_gecmis",
                                 "ayrinti": f"{len(z_hist)} < {spec.min_history}"})
                n_fail += 1
                continue
            try:
                path, rt = _fit_predict(spec, z_hist, horizon)
            except Exception as exc:
                failures.append({"origin": str(origin), "model": spec.key,
                                 "sebep": type(exc).__name__,
                                 "ayrinti": str(exc)[:300]})
                n_fail += 1
                continue
            n_ok += 1
            for h in range(1, horizon + 1):
                rows.append({"origin": origin, "model": spec.key, "h": h,
                             "z_pred": float(path[h - 1]),
                             "runtime_sec": rt if h == 1 else np.nan})
        if progress:
            log(f"  [{done}/{n_total}] {spec.key}: {n_ok} başlangıç tamam, {n_fail} atlandı")
    paths = pd.DataFrame(rows)
    if not paths.empty:
        paths["origin"] = pd.PeriodIndex(paths["origin"], freq="M")
    return paths, pd.DataFrame(failures)


# --------------------------------------------------------------------------- #
# hedeflerin türetilmesi
# --------------------------------------------------------------------------- #
def realized_frame(z: pd.Series, origins: list[pd.Period], horizon: int,
                   score_end: pd.Period,
                   yearend_origin_months: tuple[int, ...] = (6, 8, 10)) -> pd.DataFrame:
    """Gerçekleşmiş hedefler. Yalnızca ``score_end``'e kadar tamamlananlar.

    Yılsonu hedefi yalnızca yapılandırmada tanımlı başlangıç aylarında
    (varsayılan Haziran/Ağustos/Ekim sonu) üretilir; böylece her yıl seçim
    skoruna tam üç başlangıçla ve eşit ağırlıkla girer.
    """
    rows = []
    for origin in origins:
        # aylık
        for h in range(1, horizon + 1):
            per = origin + h
            if per in z.index and per <= score_end:
                rows.append({"origin": origin, "target": f"m{h}", "h": h,
                             "target_end": per, "actual": float(to_pct(z.loc[per]))})
        # bileşik 6 / 12
        for h in (6, 12):
            end = origin + h
            seg = z[(z.index > origin) & (z.index <= end)]
            if len(seg) == h and end <= score_end:
                rows.append({"origin": origin, "target": f"c{h}", "h": h,
                             "target_end": end, "actual": compound_pct(seg.to_numpy())})
        # yılsonu — yalnızca tanımlı başlangıç aylarında
        dec = pd.Period(year=origin.year, month=12, freq="M")
        if origin.month in yearend_origin_months and dec <= score_end:
            seg = z[(z.index > origin) & (z.index <= dec)]
            if len(seg) == (12 - origin.month):
                try:
                    base = ytd_pct(z, origin)
                except ValueError:
                    continue
                rows.append({"origin": origin, "target": "yearend",
                             "h": 12 - origin.month, "target_end": dec,
                             "actual": yearend_from_ytd(base, seg.to_numpy())})
        # yıllık (yoy) her ufukta
        for h in range(1, horizon + 1):
            end = origin + h
            if end > score_end:
                continue
            window = z[(z.index > end - 12) & (z.index <= end)]
            if len(window) == 12:
                rows.append({"origin": origin, "target": f"yoy{h}", "h": h,
                             "target_end": end,
                             "actual": compound_pct(window.to_numpy())})
    out = pd.DataFrame(rows)
    if not out.empty:
        out["origin"] = pd.PeriodIndex(out["origin"], freq="M")
        out["target_end"] = pd.PeriodIndex(out["target_end"], freq="M")
    return out


def predicted_frame(z: pd.Series, paths: pd.DataFrame, horizon: int,
                    yearend_origin_months: tuple[int, ...] = (6, 8, 10)) -> pd.DataFrame:
    """Tahmin yollarından hedef tahminlerini türetir (aynı ekonomik formüller)."""
    rows = []
    for (origin, model), grp in paths.groupby(["origin", "model"], sort=False):
        g = grp.sort_values("h")
        zp = g["z_pred"].to_numpy()
        if zp.size < horizon:
            continue
        for h in range(1, horizon + 1):
            rows.append({"origin": origin, "model": model, "target": f"m{h}",
                         "pred": float(np.expm1(zp[h - 1]) * 100.0)})
        for h in (6, 12):
            rows.append({"origin": origin, "model": model, "target": f"c{h}",
                         "pred": compound_pct(zp[:h])})
        if origin.month in yearend_origin_months:
            k = 12 - origin.month
            try:
                base = ytd_pct(z, origin)
            except ValueError:
                base = None
            if base is not None:
                rows.append({"origin": origin, "model": model, "target": "yearend",
                             "pred": yearend_from_ytd(base, zp[:k])})
        # yıllık: gerçekleşmiş geçmiş + tahmin karışımı
        hist = z[z.index <= origin]
        for h in range(1, horizon + 1):
            n_hist = max(12 - h, 0)
            if n_hist > len(hist):
                continue
            past = hist.to_numpy()[len(hist) - n_hist:] if n_hist else np.array([])
            comb = np.concatenate([past, zp[:h]])[-12:]
            if comb.size == 12:
                rows.append({"origin": origin, "model": model, "target": f"yoy{h}",
                             "pred": compound_pct(comb)})
    out = pd.DataFrame(rows)
    if not out.empty:
        out["origin"] = pd.PeriodIndex(out["origin"], freq="M")
    return out


def score_frame(pred: pd.DataFrame, actual: pd.DataFrame) -> pd.DataFrame:
    """Tahmin ve gerçekleşmeleri eşleştirip hata sütunu ekler."""
    if pred.empty or actual.empty:
        return pd.DataFrame(columns=["origin", "model", "target", "pred", "actual", "err"])
    df = pred.merge(actual, on=["origin", "target"], how="inner")
    df["err"] = df["pred"] - df["actual"]
    return df


# --------------------------------------------------------------------------- #
# MASE ortak paydası
# --------------------------------------------------------------------------- #
def mase_denominators(scored: pd.DataFrame, reference_model: str,
                      min_obs: int = 8) -> pd.DataFrame:
    """Her (başlangıç, hedef) için TÜM MODELLER İÇİN ORTAK payda.

    Payda, ``reference_model`` (mevsimsel naive) modelinin AYNI hedef türünde,
    başlangıç ``t``'ye kadar GERÇEKLEŞMİŞ hedeflerdeki ortalama mutlak
    hatasıdır. Hiçbir model kendi eğitim penceresinden farklı payda kullanmaz.
    """
    ref = scored[scored["model"] == reference_model].copy()
    if ref.empty:
        return pd.DataFrame(columns=["origin", "target", "mase_den", "den_n"])
    ref = ref.sort_values("target_end")
    rows = []
    for target, grp in ref.groupby("target"):
        grp = grp.sort_values("target_end")
        ends = grp["target_end"].to_numpy()
        abs_err = grp["err"].abs().to_numpy()
        for origin in sorted(scored["origin"].unique()):
            # yalnızca origin'e kadar gerçekleşmiş referans hataları
            mask = ends <= origin
            n = int(mask.sum())
            den = float(abs_err[mask].mean()) if n >= min_obs else np.nan
            rows.append({"origin": origin, "target": target,
                         "mase_den": den, "den_n": n})
    out = pd.DataFrame(rows)
    out["origin"] = pd.PeriodIndex(out["origin"], freq="M")
    return out


# --------------------------------------------------------------------------- #
# birleşimler (ensemble)
# --------------------------------------------------------------------------- #
def ensemble_paths(paths: pd.DataFrame, members: list[str], name: str,
                   method: str = "mean") -> pd.DataFrame:
    """Üye modellerin AYLIK LOG DEĞİŞİM ölçeğinde birleşimi.

    Birleşim ölçeği açıkça log aylık değişimdir; ekonomik dönüşümler
    (bileşik, YTD, yılsonu) birleşim sonrası tek ve tutarlı biçimde uygulanır.
    Yalnızca TÜM üyelerin tahmin ürettiği başlangıçlar kullanılır.
    """
    sub = paths[paths["model"].isin(members)]
    if sub.empty:
        return pd.DataFrame()
    counts = sub.groupby("origin")["model"].nunique()
    full = counts[counts == len(members)].index
    sub = sub[sub["origin"].isin(full)]
    agg = "mean" if method == "mean" else "median"
    out = (sub.groupby(["origin", "h"])["z_pred"].agg(agg).reset_index())
    out["model"] = name
    out["runtime_sec"] = np.nan
    return out[["origin", "model", "h", "z_pred", "runtime_sec"]]


def complete_yearend_years(scored: pd.DataFrame,
                           n_origins: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Yılsonu skorlarını TAM yıllara (üç başlangıcı da değerlendirilebilen)
    ve kısmi yıllara ayırır.

    Döner: (tam_yil_skorlari, kismi_yil_skorlari)
    """
    ye = scored[scored["target"] == "yearend"]
    if ye.empty:
        return scored.iloc[0:0], scored.iloc[0:0]
    ye = ye.copy()
    ye["yil"] = pd.PeriodIndex(ye["target_end"].astype(str), freq="M").year
    counts = ye.groupby(["model", "yil"])["origin"].nunique().reset_index(name="n_org")
    full = counts[counts["n_org"] >= n_origins][["model", "yil"]]
    merged = ye.merge(full, on=["model", "yil"], how="left", indicator=True)
    tam = merged[merged["_merge"] == "both"].drop(columns=["_merge"])
    kismi = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])
    return tam, kismi


def scored_for_selection(scored: pd.DataFrame, n_origins: int = 3) -> pd.DataFrame:
    """Seçim skorunda kullanılacak skorlar: yılsonu yalnızca TAM yıllardan."""
    tam, _ = complete_yearend_years(scored, n_origins)
    other = scored[scored["target"] != "yearend"]
    cols = [c for c in scored.columns]
    if tam.empty:
        return other
    return pd.concat([other, tam[cols]], ignore_index=True)
