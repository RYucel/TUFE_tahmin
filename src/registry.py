"""Aday model/pencere/dönüşüm yapılandırmaları.

Bu liste sonuçlar görülmeden tanımlanmıştır. ``complexity_rank`` beraberlik
bozmada kullanılan ÖNCEDEN TANIMLI basitlik sırasıdır (küçük = daha basit).
"""
from __future__ import annotations

import pandas as pd

from .models.base import ModelSpec
from .models import baselines as B
from .models import statistical as S
from .models import ml as M
from .models.timesfm_adapter import TimesFMZeroShot


def build_specs(cfg: dict, items: pd.DataFrame | None = None,
                include_timesfm: bool = True) -> list[ModelSpec]:
    specs: list[ModelSpec] = []

    def add(key, factory, family, window, rank, transform="log", uses_exog=False,
            min_history=24, meta=None):
        specs.append(ModelSpec(key=key, factory=factory, family=family, window=window,
                               transform=transform, complexity_rank=rank,
                               uses_exog=uses_exog, min_history=min_history,
                               meta=meta or {}))

    # --- zorunlu referanslar (pencere kavramı yok; tüm geçmişle çalışırlar) ---
    add("naive_son_ay", B.LastValue, "baseline", 0, 0, min_history=13)
    add("naive_mevsimsel_12", B.SeasonalNaive, "baseline", 0, 0, min_history=24)
    for k in (3, 6, 12):
        add(f"ortalama_{k}ay", (lambda k=k: B.RollingMean(k)), "baseline", 0, 0,
            min_history=max(24, k + 1))

    # --- istatistiksel modeller ---
    for w in cfg["backtest"]["windows"]:
        wl = "tum" if w == 0 else str(w)
        add(f"ETS_damped_seasonal_w{wl}", (lambda: S.ETSModel(True, True)), "ets", w, 2,
            min_history=48)
        add(f"AutoTheta_w{wl}", S.AutoTheta, "theta", w, 2, min_history=48)
    for w in (60, 120, 0):
        wl = "tum" if w == 0 else str(w)
        add(f"SARIMA_w{wl}", (lambda: S.SarimaSmallGrid(True)), "arima", w, 4,
            min_history=60)
    for w in (120, 0):
        wl = "tum" if w == 0 else str(w)
        add(f"UCM_llt_seasonal_w{wl}",
            (lambda: S.LocalLevelTrend("local linear trend", True)), "ucm", w, 3,
            min_history=60)

    # --- regresyon / ağaç (doğrudan ufuk) ---
    for w in (120, 0):
        wl = "tum" if w == 0 else str(w)
        add(f"Ridge_w{wl}", (lambda: M.RidgeDirect()), "ridge", w, 5, min_history=84)
        add(f"LightGBM_w{wl}", (lambda: M.LightGBMDirect()), "lgbm", w, 6, min_history=84)
    add("ElasticNet_wtum", (lambda: M.ElasticNetDirect()), "ridge", 0, 5, min_history=84)

    # --- yardımcı (sepet) verili varyantlar: yalnızca 2015+ geçmişi olan
    #     başlangıçlarda çalışır; tek değişkenli karşılıklarıyla ORTAK
    #     başlangıçlarda karşılaştırılır. ---
    if items is not None:
        add("Ridge_sepet_wtum", (lambda: M.RidgeDirect(use_items=True, items=items)),
            "ridge_aux", 0, 7, uses_exog=True, min_history=84,
            meta={"aux": "sepet_ozet_ve_faktor", "aux_start": str(items.index.min())})
        add("LightGBM_sepet_wtum",
            (lambda: M.LightGBMDirect(use_items=True, items=items)),
            "lgbm_aux", 0, 7, uses_exog=True, min_history=84,
            meta={"aux": "sepet_ozet_ve_faktor", "aux_start": str(items.index.min())})

    # --- TimesFM 3 (zorunlu karşılaştırma bileşeni) ---
    if include_timesfm and cfg.get("timesfm", {}).get("enabled", False):
        for ctx in cfg["timesfm"]["context_lengths"]:
            add(f"TimesFM3_zeroshot_ctx{ctx}",
                (lambda ctx=ctx: TimesFMZeroShot(cfg, ctx)), "foundation", 0, 8,
                min_history=48, meta={"context_length": ctx, "finetune": False})

    return specs


SIMPLICITY_NOTE = (
    "Basitlik sırası (küçük=daha basit): 0 referans, 2 ETS/Theta, 3 UCM, "
    "4 SARIMA, 5 Ridge/ElasticNet, 6 LightGBM, 7 sepet destekli ML, "
    "8 temel model (TimesFM). Bu sıra sonuçlar görülmeden sabitlenmiştir."
)
