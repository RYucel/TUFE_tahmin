"""Belirsizlik aralıkları (conformal, hedef ölçeğinde).

Zaman kuralı: ``t`` başlangıcında kalibrasyona YALNIZCA hedefi ``t``'ye kadar
gerçekleşmiş eski tahmin hataları girer. Henüz gerçekleşmemiş 12 aylık hatalar
kullanılamaz.

Aralıklar doğrudan İLGİLİ DÖNEM hedefinin hatalarından üretilir; aylık alt/üst
sınırların çarpımıyla kümülatif aralık OLUŞTURULMAZ — bu yolla zamansal
bağımlılık korunur.

Uyarı: conformal yaklaşım rejim değişimlerinde otomatik geçerli kapsama
GARANTİ ETMEZ.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def calibrate(scored: pd.DataFrame, model: str, cfg: dict) -> pd.DataFrame:
    """Her (başlangıç, hedef) için %80/%95 aralık üretir.

    Döner: origin, target, pred, actual, lo80, hi80, lo95, hi95, n_cal ve
    yetersiz örnek durumunda ilgili sınırlar NaN kalır.
    """
    cal = cfg["calibration"]
    levels = list(cal["levels"])
    min_s = {float(k): int(v) for k, v in cal["min_samples"].items()}
    max_hist = int(cal["max_history"])

    sub = scored[scored["model"] == model].copy()
    if sub.empty:
        return pd.DataFrame()
    sub = sub.sort_values(["target", "origin"])
    out_rows = []
    for target, g in sub.groupby("target"):
        g = g.sort_values("origin").reset_index(drop=True)
        ends = g["target_end"].to_numpy()
        errs = g["err"].abs().to_numpy()
        for i, row in g.iterrows():
            origin = row["origin"]
            # yalnızca hedefi origin'e kadar gerçekleşmiş hatalar
            mask = ends <= origin
            hist = errs[mask]
            if max_hist and hist.size > max_hist:
                hist = hist[-max_hist:]
            rec = {"origin": origin, "target": target, "pred": row["pred"],
                   "actual": row["actual"], "n_cal": int(hist.size)}
            for lv in levels:
                need = min_s.get(lv, 10)
                key = f"{int(lv*100)}"
                if hist.size >= need:
                    # conformal: (1-lv) kuyruğu için sonlu örnek düzeltmeli kuantil
                    q_level = min(1.0, np.ceil((hist.size + 1) * lv) / hist.size)
                    q = float(np.quantile(hist, q_level))
                    rec[f"lo{key}"] = row["pred"] - q
                    rec[f"hi{key}"] = row["pred"] + q
                else:
                    rec[f"lo{key}"] = np.nan
                    rec[f"hi{key}"] = np.nan
                    rec[f"yetersiz{key}"] = f"{hist.size}<{need}"
            out_rows.append(rec)
    return pd.DataFrame(out_rows)


def forward_intervals(scored: pd.DataFrame, model: str, cfg: dict,
                      preds: dict[str, float], origin: pd.Period) -> pd.DataFrame:
    """Nihai tahmin için aralıklar: yalnızca gerçekleşmiş geçmiş hatalar kullanılır."""
    cal = cfg["calibration"]
    levels = list(cal["levels"])
    min_s = {float(k): int(v) for k, v in cal["min_samples"].items()}
    max_hist = int(cal["max_history"])
    sub = scored[scored["model"] == model]
    rows = []
    for target, pred in preds.items():
        g = sub[(sub["target"] == target) & (sub["target_end"] <= origin)]
        hist = g["err"].abs().to_numpy()
        if max_hist and hist.size > max_hist:
            hist = hist[-max_hist:]
        rec = {"target": target, "pred": pred, "n_cal": int(hist.size)}
        for lv in levels:
            key = f"{int(lv*100)}"
            need = min_s.get(lv, 10)
            if hist.size >= need:
                q_level = min(1.0, np.ceil((hist.size + 1) * lv) / hist.size)
                q = float(np.quantile(hist, q_level))
                rec[f"lo{key}"], rec[f"hi{key}"] = pred - q, pred + q
                rec[f"yontem{key}"] = "conformal (mutlak hata kuantili)"
            else:
                rec[f"lo{key}"] = np.nan
                rec[f"hi{key}"] = np.nan
                rec[f"yontem{key}"] = f"YETERSİZ ÖRNEK ({hist.size}<{need}) — aralık üretilmedi"
        rows.append(rec)
    return pd.DataFrame(rows)


def coverage_report(cal_df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Kapsama oranı, gözlem sayısı, ortalama genişlik ve interval score."""
    from . import metrics as MX
    rows = []
    for target, g in cal_df.groupby("target"):
        for lv in cfg["calibration"]["levels"]:
            key = f"{int(lv*100)}"
            lo, hi = g.get(f"lo{key}"), g.get(f"hi{key}")
            if lo is None:
                continue
            cov, n = MX.coverage(g["actual"].to_numpy(), lo.to_numpy(), hi.to_numpy())
            width = float(np.nanmean((hi - lo).to_numpy())) if n else np.nan
            isc = MX.interval_score(g["actual"].to_numpy(), lo.to_numpy(),
                                    hi.to_numpy(), 1.0 - lv)
            rows.append({"hedef": target, "seviye": f"%{key}", "kapsama": cov,
                         "n": n, "ortalama_genislik": width, "interval_score": isc})
    df = pd.DataFrame(rows)
    if not df.empty:
        # WIS: mevcut aralıklardan yaklaşık; tam CRPS DEĞİLDİR
        wis_rows = []
        for target, g in cal_df.groupby("target"):
            iv = {}
            for lv in cfg["calibration"]["levels"]:
                key = f"{int(lv*100)}"
                if f"lo{key}" in g:
                    iv[lv] = (g[f"lo{key}"].to_numpy(), g[f"hi{key}"].to_numpy())
            if iv:
                wis_rows.append({"hedef": target,
                                 "WIS_yaklasik": MX.wis(g["actual"].to_numpy(), iv,
                                                        g["pred"].to_numpy())})
        if wis_rows:
            df = df.merge(pd.DataFrame(wis_rows), on="hedef", how="left")
    return df
