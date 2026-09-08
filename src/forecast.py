"""Nihai tahmin üretimi ve arşivleme.

Geliştirmede seçilmiş yapılandırma (model + eğitim penceresi + dönüşüm) veri
kesimine kadar yeniden eğitilir. Seçilmiş eğitim penceresi KORUNUR.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .backtest import _fit_predict
from .models.base import ModelSpec
from .transforms import (compound_pct, compound_path_pct, to_pct, ytd_pct,
                         yearend_from_ytd)


def fit_final(spec: ModelSpec, z: pd.Series, horizon: int) -> tuple[np.ndarray, float]:
    """Seçilmiş yapılandırmayı veri kesimine kadar yeniden eğitip yol üretir."""
    return _fit_predict(spec, z, horizon)


def build_forecast_table(z: pd.Series, z_path: np.ndarray, cutoff: pd.Period,
                         monthly_official: pd.DataFrame,
                         model_label: str) -> pd.DataFrame:
    """Aylık tahmin tablosu: aylık %, yıllık %, YTD %, kesimden kümülatif %."""
    horizon = len(z_path)
    periods = [cutoff + i for i in range(1, horizon + 1)]
    monthly_pct = to_pct(z_path)
    cum_pct = compound_path_pct(z_path)

    # yıllık ve YTD için gerçekleşmiş + tahmin birleşik serisi
    z_all = pd.concat([z, pd.Series(z_path, index=pd.PeriodIndex(periods, freq="M"))])

    rows = []
    # Güncel yılsonu için doğrulanmış RESMÎ YTD başlangıcı kullanılır.
    official_ytd = float(monthly_official.loc[cutoff, "yilBasindanYuzde"])
    for i, per in enumerate(periods):
        win = z_all[(z_all.index > per - 12) & (z_all.index <= per)]
        yoy = compound_pct(win.to_numpy()) if len(win) == 12 else np.nan
        if per.year == cutoff.year:
            ytd = yearend_from_ytd(official_ytd, z_path[:i + 1])
            ytd_note = "resmî YTD + tahmin"
        else:
            jan = pd.Period(year=per.year, month=1, freq="M")
            seg = z_all[(z_all.index >= jan) & (z_all.index <= per)]
            ytd = compound_pct(seg.to_numpy()) if len(seg) == per.month else np.nan
            ytd_note = "tahmin"
        rows.append({
            "tarih": str(per),
            "aylik_pct": float(monthly_pct[i]),
            "yillik_pct": yoy,
            "ytd_pct": ytd,
            "ytd_kaynak": ytd_note,
            f"kumulatif_{cutoff}_sonrasi_pct": float(cum_pct[i]),
            "model": model_label,
            "veri_kesimi": str(cutoff),
        })
    return pd.DataFrame(rows)


def period_summaries(z: pd.Series, z_path: np.ndarray, cutoff: pd.Period,
                     monthly_official: pd.DataFrame) -> pd.DataFrame:
    """Yılsonu, ileri 6/12 ay ve takvim yarıyılı özetleri (birbirinden ayrı)."""
    periods = pd.PeriodIndex([cutoff + i for i in range(1, len(z_path) + 1)], freq="M")
    z_all = pd.concat([z, pd.Series(z_path, index=periods)])
    official_ytd = float(monthly_official.loc[cutoff, "yilBasindanYuzde"])
    dec = pd.Period(year=cutoff.year, month=12, freq="M")
    k = 12 - cutoff.month

    rows = [
        {"olcu": f"{cutoff.year} yılsonu enflasyonu (Ara {cutoff.year}/Ara {cutoff.year-1})",
         "tanim": f"Gerçekleşmiş YTD (%{official_ytd:.4f}, {cutoff}) + {k} aylık tahmin",
         "deger_pct": yearend_from_ytd(official_ytd, z_path[:k]),
         "donem": f"{cutoff.year}-01 → {dec}"},
        {"olcu": "Gelecek 6 ayın BİLEŞİK enflasyonu",
         "tanim": "Başlangıç sonrası 6 ayın bileşiği (yıllık enflasyon DEĞİLDİR)",
         "deger_pct": compound_pct(z_path[:6]),
         "donem": f"{periods[0]} → {periods[5]}"},
        {"olcu": "Gelecek 12 ayın BİLEŞİK enflasyonu",
         "tanim": "Başlangıç sonrası 12 ayın bileşiği",
         "deger_pct": compound_pct(z_path[:12]),
         "donem": f"{periods[0]} → {periods[11]}"},
    ]

    # Temmuz–Aralık 2026 (2. dönem): Tem+Ağu gerçekleşme, Eyl–Ara tahmin
    jul = pd.Period(year=cutoff.year, month=7, freq="M")
    seg_real = z[(z.index >= jul) & (z.index <= cutoff)]
    n_real = len(seg_real)
    if n_real > 0 and k > 0:
        val = compound_pct(np.concatenate([seg_real.to_numpy(), z_path[:k]]))
        rows.append({"olcu": f"Temmuz–Aralık {cutoff.year} bileşik değişimi (2. dönem)",
                     "tanim": f"{n_real} ay gerçekleşme + {k} ay tahmin",
                     "deger_pct": val, "donem": f"{jul} → {dec}"})

    # Ocak–Haziran 2027 (1. dönem, tamamen tahmin)
    nxt = cutoff.year + 1
    jan, jun = pd.Period(year=nxt, month=1, freq="M"), pd.Period(year=nxt, month=6, freq="M")
    seg = z_all[(z_all.index >= jan) & (z_all.index <= jun)]
    if len(seg) == 6:
        rows.append({"olcu": f"Ocak–Haziran {nxt} bileşik değişimi (1. dönem)",
                     "tanim": "Tamamı tahmin (takvim yarıyılı)",
                     "deger_pct": compound_pct(seg.to_numpy()),
                     "donem": f"{jan} → {jun}"})

    # Şubat 2027 yıllık
    feb = pd.Period(year=nxt, month=2, freq="M")
    win = z_all[(z_all.index > feb - 12) & (z_all.index <= feb)]
    if len(win) == 12:
        rows.append({"olcu": f"{feb} YILLIK enflasyonu",
                     "tanim": "12 aylık geriye dönük değişim (6 aylık bileşik DEĞİLDİR)",
                     "deger_pct": compound_pct(win.to_numpy()), "donem": f"{feb-11} → {feb}"})

    return pd.DataFrame(rows)


def archive(payload: dict, archive_dir: Path) -> Path:
    """Tarihli tahmin arşivi.

    Kaydedilen tahminlerin sonradan gerçekleşmelerle karşılaştırılabilmesi için
    değişmez (append-only) bir yapı. Zamanlanmış otomasyon veya dış servise
    dağıtım BU GÖREVİN KAPSAMINDA DEĞİLDİR.
    """
    archive_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = archive_dir / f"forecast_{payload['veri_kesimi']}_{stamp}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str),
                    encoding="utf-8")
    index = archive_dir / "index.jsonl"
    with open(index, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"dosya": path.name, "veri_kesimi": payload["veri_kesimi"],
                             "model": payload["model"], "uretildi": stamp},
                            ensure_ascii=False) + "\n")
    return path
