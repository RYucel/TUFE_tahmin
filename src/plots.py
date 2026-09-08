"""Türkçe grafikler (PNG + SVG).

Kurallar: gerçekleşme/tahmin ayrımı çizgi biçimiyle gösterilir, tahmin
başlangıcı işaretlenir, başlık ve eksenlerde veri kesimi ile ölçü birimi yer
alır.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import out_dir
from .data import get_data
from .transforms import to_log

plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 150, "font.size": 10,
    "axes.grid": True, "grid.alpha": 0.3, "axes.spines.top": False,
    "axes.spines.right": False, "figure.autolayout": True,
})

C_REAL, C_FC, C_ALT1, C_ALT2 = "#1b3a6b", "#c1440e", "#2e7d32", "#6a1b9a"


def _save(fig, cfg, name: str) -> list[Path]:
    fdir = out_dir(cfg, "figures")
    paths = []
    for fmt in cfg["report"]["formats"]:
        p = fdir / f"{name}.{fmt}"
        fig.savefig(p, format=fmt, bbox_inches="tight")
        paths.append(p)
    plt.close(fig)
    return paths


def _mark_origin(ax, x, label: str) -> None:
    ax.axvline(x, color="0.35", ls=":", lw=1.4)
    ax.annotate(label, xy=(x, ax.get_ylim()[1]), xytext=(4, -12),
                textcoords="offset points", fontsize=8, color="0.3",
                rotation=90, va="top")


def _read(cfg, rel: str) -> pd.DataFrame | None:
    p = out_dir(cfg) / rel
    if not p.exists():
        return None
    return pd.read_parquet(p) if rel.endswith(".parquet") else pd.read_csv(p)


def _tbl(cfg, name: str) -> pd.DataFrame | None:
    p = out_dir(cfg, "tables") / name
    return pd.read_csv(p) if p.exists() else None


# --------------------------------------------------------------------------- #
def fig_monthly_forecast(cfg, bundle, table) -> None:
    cutoff = pd.Period(cfg["data"]["cutoff"], freq="M")
    m = bundle.monthly["aylikYuzde"]
    hist = m[m.index >= cutoff - 59]
    fx = pd.PeriodIndex(table["tarih"], freq="M")

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(hist.index.to_timestamp(), hist.values, color=C_REAL, lw=1.8,
            label="Gerçekleşme (resmî)")
    bridge_x = [cutoff.to_timestamp()] + list(fx.to_timestamp())
    bridge_y = [float(m.loc[cutoff])] + list(table["aylik_pct"])
    ax.plot(bridge_x, bridge_y, color=C_FC, lw=2.0, ls="--", marker="o", ms=3.5,
            label="Tahmin")
    if "aylik_lo80" in table and table["aylik_lo80"].notna().any():
        ax.fill_between(fx.to_timestamp(), table["aylik_lo80"], table["aylik_hi80"],
                        color=C_FC, alpha=0.18, label="%80 aralık (aylık ölçü)")
    if "aylik_lo95" in table and table["aylik_lo95"].notna().any():
        ax.fill_between(fx.to_timestamp(), table["aylik_lo95"], table["aylik_hi95"],
                        color=C_FC, alpha=0.09, label="%95 aralık (aylık ölçü)")
    _mark_origin(ax, cutoff.to_timestamp(), f"tahmin başlangıcı ({cutoff})")
    ax.set_title(f"KKTC aylık TÜFE değişimi — son 5 yıl ve 12 aylık tahmin\n"
                 f"veri kesimi: {cutoff} · ölçü: aylık % değişim (yüzde puan)")
    ax.set_xlabel("Ay"); ax.set_ylabel("Aylık değişim (%)")
    ax.legend(fontsize=8, ncol=2)
    _save(fig, cfg, "g1_aylik_enflasyon_ve_tahmin")


def fig_yoy(cfg, bundle, table) -> None:
    cutoff = pd.Period(cfg["data"]["cutoff"], freq="M")
    y = bundle.monthly["yillikYuzde"].dropna()
    y = y[y.index >= cutoff - 71]
    fx = pd.PeriodIndex(table["tarih"], freq="M")
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(y.index.to_timestamp(), y.values, color=C_REAL, lw=1.8,
            label="Gerçekleşme (resmî yıllık)")
    ax.plot([cutoff.to_timestamp()] + list(fx.to_timestamp()),
            [float(y.loc[cutoff])] + list(table["yillik_pct"]),
            color=C_FC, lw=2.0, ls="--", marker="o", ms=3.5, label="Tahmin (yıllık)")
    _mark_origin(ax, cutoff.to_timestamp(), f"tahmin başlangıcı ({cutoff})")
    ax.set_title(f"KKTC yıllık TÜFE enflasyonu ve tahmini\n"
                 f"veri kesimi: {cutoff} · ölçü: 12 aylık % değişim (yüzde puan)")
    ax.set_xlabel("Ay"); ax.set_ylabel("Yıllık değişim (%)")
    ax.legend(fontsize=8)
    _save(fig, cfg, "g2_yillik_enflasyon_ve_tahmin")


def fig_cumulative(cfg, table) -> None:
    cutoff = pd.Period(cfg["data"]["cutoff"], freq="M")
    col = [c for c in table.columns if c.startswith("kumulatif_")][0]
    fx = pd.PeriodIndex(table["tarih"], freq="M")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot([cutoff.to_timestamp()] + list(fx.to_timestamp()),
            [0.0] + list(table[col]), color=C_FC, lw=2.2, ls="--", marker="o", ms=4)
    for i, (x, v) in enumerate(zip(fx.to_timestamp(), table[col])):
        if i % 2 == 1:
            ax.annotate(f"%{v:.1f}", (x, v), textcoords="offset points",
                        xytext=(0, 7), fontsize=8, ha="center")
    _mark_origin(ax, cutoff.to_timestamp(), f"başlangıç ({cutoff})")
    ax.set_title(f"{cutoff} sonrası KÜMÜLATİF (bileşik) tahmin yolu\n"
                 f"veri kesimi: {cutoff} · ölçü: bileşik % değişim (yüzde puan)")
    ax.set_xlabel("Ay"); ax.set_ylabel(f"{cutoff}'a göre bileşik değişim (%)")
    _save(fig, cfg, "g3_kumulatif_tahmin_yolu")


def fig_yearend_history(cfg, dev, test, winner) -> None:
    frames = [d for d in (dev, test) if d is not None and not d.empty]
    if not frames:
        return
    df = pd.concat(frames)
    df = df[(df["target"] == "yearend") & (df["model"] == winner)]
    if df.empty:
        return
    df = df.copy()
    df["yil"] = pd.PeriodIndex(df["target_end"].astype(str), freq="M").year
    df["ay"] = pd.PeriodIndex(df["origin"].astype(str), freq="M").month
    fig, ax = plt.subplots(figsize=(11, 5))
    marks = {6: ("o", "Haziran sonu (6 ay)"), 8: ("s", "Ağustos sonu (4 ay)"),
             10: ("^", "Ekim sonu (2 ay)")}
    for mth, (mk, lbl) in marks.items():
        sub = df[df["ay"] == mth]
        if not sub.empty:
            ax.scatter(sub["yil"], sub["pred"], marker=mk, s=55, label=f"Tahmin — {lbl}",
                       color=C_FC, alpha=0.85)
    act = df.groupby("yil")["actual"].first()
    ax.plot(act.index, act.values, color=C_REAL, lw=2, marker="D", ms=6,
            label="Gerçekleşme (Aralık/Aralık)")
    ax.set_title(f"Geçmiş yılsonu tahminleri ve gerçekleşmeler — {winner}\n"
                 "ölçü: Aralık/Aralık yıllık enflasyon (%)")
    ax.set_xlabel("Yıl"); ax.set_ylabel("Yılsonu enflasyonu (%)")
    ax.legend(fontsize=8)
    _save(fig, cfg, "g4_yilsonu_tahmin_gerceklesme")


def fig_error_heatmap(cfg, scored, tag: str) -> None:
    if scored is None or scored.empty:
        return
    keep = ["c6", "c12", "yearend"] + [f"m{h}" for h in (1, 3, 6, 12)]
    sub = scored[scored["target"].isin(keep)]
    piv = sub.groupby(["model", "target"])["err"].apply(lambda s: s.abs().mean()).unstack()
    piv = piv.reindex(columns=[c for c in keep if c in piv.columns])
    piv = piv.loc[piv.mean(axis=1).sort_values().index]
    fig, ax = plt.subplots(figsize=(1.05 * len(piv.columns) + 4, 0.36 * len(piv) + 2.4))
    im = ax.imshow(piv.values, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(piv.columns)), piv.columns, rotation=0)
    ax.set_yticks(range(len(piv.index)), piv.index, fontsize=7)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v = piv.values[i, j]
            if np.isfinite(v):
                ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=6.5,
                        color="black" if v < np.nanmax(piv.values) * 0.6 else "white")
    fig.colorbar(im, ax=ax, label="MAE (yüzde puan)")
    ax.set_title(f"Model × hedef ortalama mutlak hata — {tag}\n"
                 f"veri kesimi: {cfg['data']['cutoff']} · birim: yüzde puan")
    ax.grid(False)
    _save(fig, cfg, f"g5_hata_isi_haritasi_{tag}")


def fig_c6_errors_over_time(cfg, dev, test, models: list[str]) -> None:
    frames = [d for d in (dev, test) if d is not None and not d.empty]
    if not frames:
        return
    df = pd.concat(frames)
    df = df[(df["target"] == "c6") & (df["model"].isin(models))]
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(11, 4.6))
    for mdl, color in zip(models, (C_FC, C_ALT1, C_ALT2)):
        sub = df[df["model"] == mdl].copy()
        sub["x"] = pd.PeriodIndex(sub["target_end"].astype(str), freq="M").to_timestamp()
        sub = sub.sort_values("x")
        ax.plot(sub["x"], sub["err"], lw=1.4, label=mdl, color=color)
    ax.axhline(0, color="0.3", lw=1)
    dev_end = pd.Period(cfg["split"]["dev_end"], freq="M").to_timestamp()
    _mark_origin(ax, dev_end, "geliştirme sınırı")
    ax.set_title("Zaman içinde 6 aylık BİLEŞİK enflasyon tahmin hataları\n"
                 f"veri kesimi: {cfg['data']['cutoff']} · birim: yüzde puan "
                 "(pozitif = fazla tahmin)")
    ax.set_xlabel("Hedef dönemin bitiş ayı"); ax.set_ylabel("Hata (yüzde puan)")
    ax.legend(fontsize=8)
    _save(fig, cfg, "g6_6ay_hatalar_zaman_icinde")


def fig_dev_vs_test(cfg) -> None:
    dev = _tbl(cfg, "03b_gelistirme_siralamasi.csv")
    test = _tbl(cfg, "03d_nihai_test_ozet.csv")
    if dev is None or test is None:
        return
    tw = {}
    w = cfg["selection"]["weights"]
    for model, g in test.groupby("model"):
        s, ok = 0.0, True
        for t, key in (("yearend", "yearend"), ("c6", "c6"), ("c12", "c12")):
            r = g[g["hedef"] == t]
            if r.empty or not np.isfinite(r["MAE"].iloc[0]):
                ok = False
                break
            s += w[key] * float(r["MAE"].iloc[0])
        if ok:
            tw[model] = s
    merged = dev[["model", "S"]].dropna().copy()
    merged["S_test"] = merged["model"].map(tw)
    merged = merged.dropna()
    if merged.empty:
        return
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    ax.scatter(merged["S"], merged["S_test"], s=45, color=C_REAL, alpha=0.8)
    for _, r in merged.iterrows():
        ax.annotate(r["model"], (r["S"], r["S_test"]), fontsize=6.5,
                    xytext=(4, 3), textcoords="offset points")
    lim = [0, max(merged["S"].max(), merged["S_test"].max()) * 1.1]
    ax.plot(lim, lim, ls=":", color="0.5", lw=1)
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_title("Geliştirme ve nihai test performansı\n"
                 "seçim skoru S = 0,60·MAE_yılsonu + 0,30·MAE_6ay + 0,10·MAE_12ay "
                 "(yüzde puan)")
    ax.set_xlabel("Geliştirme S (düşük daha iyi)")
    ax.set_ylabel("Nihai test S (düşük daha iyi)")
    _save(fig, cfg, "g7_gelistirme_vs_nihai_test")


def fig_model_differences(cfg, tables: dict[str, pd.DataFrame]) -> None:
    if len(tables) < 2:
        return
    cutoff = pd.Period(cfg["data"]["cutoff"], freq="M")
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    colors = [C_FC, C_ALT1, C_ALT2]
    for (name, t), c in zip(tables.items(), colors):
        x = pd.PeriodIndex(t["tarih"], freq="M").to_timestamp()
        axes[0].plot(x, t["aylik_pct"], lw=1.8, marker="o", ms=3, label=name, color=c)
        col = [k for k in t.columns if k.startswith("kumulatif_")][0]
        axes[1].plot(x, t[col], lw=1.8, marker="o", ms=3, label=name, color=c)
    axes[0].set_title(f"Ana model ve alternatiflerin tahmin farkları\n"
                      f"veri kesimi: {cutoff} · üst: aylık %, alt: {cutoff} sonrası bileşik %")
    axes[0].set_ylabel("Aylık değişim (%)")
    axes[1].set_ylabel(f"{cutoff} sonrası bileşik (%)")
    axes[1].set_xlabel("Ay")
    axes[0].legend(fontsize=8)
    _save(fig, cfg, "g8_model_tahmin_farklari")


def make_all(cfg: dict) -> None:
    bundle = get_data(cfg, refresh=False)
    table = _tbl(cfg, "06_aylik_tahminler.csv")
    dev = _read(cfg, "dev_scored.parquet")
    test = _read(cfg, "test_scored.parquet")
    frozen_p = out_dir(cfg, "selection") / "frozen_selection.json"
    winner, alts = None, []
    if frozen_p.exists():
        fr = json.loads(frozen_p.read_text(encoding="utf-8"))
        winner, alts = fr["winner"], fr["frozen_extra"]["alternatifler"]

    if table is not None:
        fig_monthly_forecast(cfg, bundle, table)
        fig_yoy(cfg, bundle, table)
        fig_cumulative(cfg, table)
    if winner:
        fig_yearend_history(cfg, dev, test, winner)
        fig_c6_errors_over_time(cfg, dev, test, [winner] + alts[:2])
    fig_error_heatmap(cfg, dev, "gelistirme")
    fig_error_heatmap(cfg, test, "nihai_test")
    fig_dev_vs_test(cfg)

    # ana model + alternatiflerin nihai tahmin yolları
    tabs = {}
    if table is not None and winner:
        tabs[winner] = table
    comp = _tbl(cfg, "08_model_karsilastirmasi.csv")
    if comp is not None and "model" in comp:
        pass
    alt_dir = out_dir(cfg, "tables")
    for a in alts[:2]:
        p = alt_dir / f"06_aylik_tahminler_{_slug(a)}.csv"
        if p.exists():
            tabs[a] = pd.read_csv(p)
    fig_model_differences(cfg, tabs)


def _slug(s: str) -> str:
    keep = "".join(ch if ch.isalnum() else "_" for ch in s)
    return keep.strip("_")[:60]
