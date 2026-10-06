#!/usr/bin/env python
"""KKTC TÜFE Tahmin Sistemi — çalıştırma aşamaları.

Aşamalar: data, backtest, select, evaluate, forecast, report, all
Nihai test (evaluate) aşaması, DONDURULMUŞ SEÇİM DOSYASI olmadan çalışmaz.
"""
from __future__ import annotations

import argparse
import json
import warnings
import os
import platform
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
os.environ.setdefault("PYTHONWARNINGS", "ignore")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src import backtest as BT
from src import calibration as CAL
from src import data as DATA
from src import metrics as MX
from src import selection as SEL
from src import forecast as FC
from src.config import load_config, out_dir
from src.registry import build_specs, SIMPLICITY_NOTE
from src.transforms import to_log, synthetic_chain_index
from src.models.timesfm_adapter import probe as timesfm_probe

ROOT = Path(__file__).resolve().parent


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)


def hardware_info() -> dict:
    info = {"platform": platform.platform(), "python": platform.python_version(),
            "processor": platform.processor() or platform.machine(),
            "cpu_count": os.cpu_count()}
    try:
        import psutil  # noqa
        info["ram_gb"] = round(psutil.virtual_memory().total / 1e9, 1)
    except Exception:
        try:
            info["ram_gb"] = round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1e9, 1)
        except Exception:
            info["ram_gb"] = None
    try:
        import torch
        info["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "yok (CPU)"
    except Exception:
        info["gpu"] = "bilinmiyor"
    return info


def package_versions() -> dict:
    import importlib.metadata as md
    out = {}
    for p in ("numpy", "pandas", "scipy", "scikit-learn", "statsmodels", "lightgbm",
              "matplotlib", "pyarrow", "torch", "timesfm"):
        try:
            out[p] = md.version(p)
        except Exception:
            out[p] = None
    return out


def peak_memory_mb() -> float:
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def write_manifest(cfg: dict, stage: str, extra: dict) -> Path:
    man = {
        "asama": stage,
        "zaman_utc": datetime.now(timezone.utc).isoformat(),
        "seed": cfg["project"]["seed"],
        "config": {k: v for k, v in cfg.items() if not k.startswith("_")},
        "paket_surumleri": package_versions(),
        "donanim": hardware_info(),
        "tepe_bellek_mb": round(peak_memory_mb(), 1),
        "determinizm_notu": (
            "Sabit seed kullanılmıştır. LightGBM/BLAS iş parçacığı sayısı ve "
            "donanım farklılıkları nedeniyle son basamak düzeyinde tam "
            "determinizm garanti edilmez."),
    }
    man.update(extra)
    p = out_dir(cfg) / f"manifest_{stage}.json"
    p.write_text(json.dumps(man, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return p


# --------------------------------------------------------------------------- #
def stage_data(cfg: dict, args) -> dict:
    log("Veri alınıyor…")
    bundle = DATA.get_data(cfg, refresh=args.refresh)
    log(f"  köken={bundle.provenance}  ana seri={len(bundle.monthly)} ay "
        f"({bundle.monthly.index.min()}–{bundle.monthly.index.max()})")
    audit = DATA.audit(bundle, cfg)
    tdir = out_dir(cfg, "tables")
    audit.to_csv(tdir / "01_veri_denetimi.csv", index=False, encoding="utf-8-sig")

    kapsam = pd.DataFrame([
        {"alan": "Ana seri", "kapsam": f"{bundle.monthly.index.min()} – {bundle.monthly.index.max()}",
         "kayit": len(bundle.monthly), "kaynak": bundle.provenance},
        {"alan": "Sepet madde fiyatları",
         "kapsam": (f"{bundle.items.index.min()} – {bundle.items.index.max()}"
                    if bundle.items is not None else "yok"),
         "kayit": (f"{bundle.items.shape[1]} kalem × {bundle.items.shape[0]} ay"
                   if bundle.items is not None else 0),
         "kaynak": bundle.provenance},
    ])
    kapsam.to_csv(tdir / "01_veri_kapsami.csv", index=False, encoding="utf-8-sig")

    idx = synthetic_chain_index(bundle.monthly["aylikYuzde"])
    idx.to_frame().to_csv(tdir / "01_sentetik_zincir_endeks.csv", encoding="utf-8-sig")

    fails = [s.dict() for s in bundle.sources if s.status != "ok"]
    tfm = timesfm_probe(cfg)
    log(f"  TimesFM 3 durumu: {'KULLANILABİLİR' if tfm.available else 'ENGELLİ'}")
    write_manifest(cfg, "data", {
        "veri_kaynaklari": [s.dict() for s in bundle.sources],
        "api_meta": bundle.api_meta,
        "api_openapi_uc_noktalari": bundle.api_openapi_endpoints,
        "erisilemeyen_kaynaklar": fails,
        "timesfm_durumu": tfm.dict(),
        "denetim_ozeti": audit["durum"].value_counts().to_dict(),
    })
    return {"bundle": bundle, "audit": audit, "timesfm": tfm}




def _run_paths(cfg, z, specs, origins, H, log) -> tuple:
    """Geriye dönük testi çalıştırır; TimesFM zero-shot adayları için toplu
    (batched) çıkarım yolunu kullanır. Sonuç tek tek çalıştırmayla özdeştir."""
    from src.models import timesfm_adapter as TFM

    batchable = [sp for sp in specs if sp.meta.get("batch_capable")]
    rest = [sp for sp in specs if not sp.meta.get("batch_capable")]
    paths, failures = BT.run_backtest(z, rest, origins, H, log=log)
    for sp in batchable:
        try:
            bp = TFM.batch_backtest_paths(
                cfg, z, origins, H, int(sp.meta["context_length"]), sp.key,
                int(cfg["timesfm"].get("batch_size", 64)), log=log)
            if not bp.empty:
                paths = pd.concat([paths, bp], ignore_index=True)
                log(f"  {sp.key}: {bp['origin'].nunique()} başlangıç tamam (toplu)")
        except Exception as exc:
            log(f"  {sp.key}: toplu çıkarım başarısız ({type(exc).__name__}: {exc}); "
                "tek tek çalıştırılıyor")
            p2, f2 = BT.run_backtest(z, [sp], origins, H, log=log)
            if not p2.empty:
                paths = pd.concat([paths, p2], ignore_index=True)
            failures = pd.concat([failures, f2], ignore_index=True)
    if not paths.empty:
        paths["origin"] = pd.PeriodIndex(paths["origin"].astype(str), freq="M")
    return paths, failures


def _write_failures(cfg, failures: pd.DataFrame, name: str) -> None:
    """Başarısız denemeler boş olsa bile başlıklı bir CSV yazılır."""
    if failures is None or failures.empty:
        failures = pd.DataFrame(columns=["origin", "model", "sebep", "ayrinti"])
    failures.to_csv(out_dir(cfg, "tables") / name, index=False, encoding="utf-8-sig")


def _yem(cfg) -> tuple:
    return tuple(cfg["targets"]["yearend_origin_months"])


def _rescore(cfg, z, paths, score_end, H):
    origins = sorted(pd.PeriodIndex(paths["origin"].astype(str), freq="M").unique())
    actual = BT.realized_frame(z, list(origins), H, score_end, _yem(cfg))
    pred = BT.predicted_frame(z, paths, H, _yem(cfg))
    return BT.score_frame(pred, actual)


def _prepare(cfg: dict, args):
    bundle = DATA.get_data(cfg, refresh=False)
    z = to_log(bundle.monthly["aylikYuzde"]).dropna()
    z.name = "z"
    tfm = timesfm_probe(cfg)
    specs = build_specs(cfg, items=bundle.items, include_timesfm=tfm.available)
    return bundle, z, specs, tfm


def stage_backtest(cfg: dict, args) -> dict:
    """Geliştirme doğrulaması: hedefler dev_end'e kadar tamamlanmış olmalı."""
    bundle, z, specs, tfm = _prepare(cfg, args)
    dev_end = pd.Period(cfg["split"]["dev_end"], freq="M")
    o_start = pd.Period(cfg["split"]["dev_origin_start"], freq="M")
    H = int(cfg["horizon"])
    origins = [p for p in z.index if o_start <= p <= dev_end]
    if args.smoke:
        origins = origins[-args.smoke:]
        log(f"SMOKE modu: yalnızca son {len(origins)} başlangıç")

    log(f"Geliştirme geriye dönük testi: {len(specs)} aday × {len(origins)} başlangıç")
    t0 = time.perf_counter()
    paths, failures = _run_paths(cfg, z, specs, origins, H, log)
    elapsed = time.perf_counter() - t0
    log(f"  süre: {elapsed:.1f} s, tepe bellek: {peak_memory_mb():.0f} MB")

    # birleşimler geliştirme skorlarına aday olarak eklenir (üyeler dev'de seçilir)
    scored, ens_members = _score_and_ensemble(cfg, z, paths, dev_end, H, specs)

    adir = out_dir(cfg)
    paths.to_parquet(adir / "dev_paths.parquet")
    scored.to_parquet(adir / "dev_scored.parquet")
    _write_failures(cfg, failures, "10_basarisiz_denemeler_dev.csv")

    cfgs = pd.DataFrame([{
        "aday": s.key, "aile": s.family, "pencere": ("tüm geçmiş" if s.window == 0
                                                     else f"son {s.window} ay"),
        "donusum": s.transform, "basitlik_sirasi": s.complexity_rank,
        "yardimci_veri": "evet" if s.uses_exog else "hayır",
        "min_gecmis_ay": s.min_history, "notlar": json.dumps(s.meta, ensure_ascii=False),
    } for s in specs])
    cfgs.to_csv(out_dir(cfg, "tables") / "02_aday_yapilandirmalar.csv",
                index=False, encoding="utf-8-sig")

    write_manifest(cfg, "backtest", {
        "n_aday": len(specs), "n_baslangic": len(origins),
        "sure_sn": round(elapsed, 1),
        "birlesim_uyeleri": ens_members,
        "timesfm_durumu": tfm.dict(),
        "basitlik_notu": SIMPLICITY_NOTE,
    })
    return {"paths": paths, "scored": scored}


def _score_and_ensemble(cfg, z, paths, score_end, H, specs):
    origins = sorted(paths["origin"].unique())
    actual = BT.realized_frame(z, list(origins), H, score_end, _yem(cfg))
    # birleşim adayları: mevcut skorlara göre farklı ailelerden en iyi 3
    pred = BT.predicted_frame(z, paths, H, _yem(cfg))
    scored = BT.score_frame(pred, actual)
    meta = {s.key: {"family": s.family, "complexity_rank": s.complexity_rank}
            for s in specs}
    try:
        base_scores = SEL.selection_scores(
            BT.scored_for_selection(scored, len(_yem(cfg))),
            cfg["selection"]["weights"], cfg["selection"]["min_common_origins"])
        seen, members = set(), []
        for _, r in base_scores[base_scores["uygun"]].sort_values("S").iterrows():
            fam = meta.get(r["model"], {}).get("family", "?")
            if fam in seen:
                continue
            seen.add(fam)
            members.append(r["model"])
            if len(members) >= cfg["selection"]["ensemble"]["top_k"]:
                break
    except Exception:
        members = []
    if len(members) >= 2:
        extra = []
        for method in cfg["selection"]["ensemble"]["methods"]:
            name = f"BIRLESIM_{method}_{len(members)}"
            ep = BT.ensemble_paths(paths, members, name, method)
            if not ep.empty:
                extra.append(ep)
        if extra:
            paths_all = pd.concat([paths] + extra, ignore_index=True)
            pred = BT.predicted_frame(z, paths_all, H, _yem(cfg))
            scored = BT.score_frame(pred, actual)
    return scored, members



def _members_from_paths(cfg, z, paths, score_end, H, specs) -> list:
    """Birleşim üyeleri: geliştirme skorlarına göre farklı ailelerden en iyi 3."""
    scored = _rescore(cfg, z, paths, score_end, H)
    sel_scored = BT.scored_for_selection(scored, len(_yem(cfg)))
    meta = {s.key: s.family for s in specs}
    try:
        base = SEL.selection_scores(sel_scored, cfg["selection"]["weights"],
                                    cfg["selection"]["min_common_origins"])
    except Exception:
        return []
    seen, members = set(), []
    for _, r in base[base["uygun"]].sort_values("S").iterrows():
        fam = meta.get(r["model"], "?")
        if cfg["selection"]["ensemble"]["distinct_families"] and fam in seen:
            continue
        seen.add(fam)
        members.append(r["model"])
        if len(members) >= int(cfg["selection"]["ensemble"]["top_k"]):
            break
    return members


def stage_select(cfg: dict, args) -> dict:
    bundle, z, specs, tfm = _prepare(cfg, args)
    adir = out_dir(cfg)
    paths = pd.read_parquet(adir / "dev_paths.parquet")
    paths["origin"] = pd.PeriodIndex(paths["origin"].astype(str), freq="M")
    dev_end = pd.Period(cfg["split"]["dev_end"], freq="M")
    H = int(cfg["horizon"])
    members = _members_from_paths(cfg, z, paths, dev_end, H, specs)
    for method in cfg["selection"]["ensemble"]["methods"]:
        if len(members) >= 2:
            ep = BT.ensemble_paths(paths, members, f"BIRLESIM_{method}_{len(members)}", method)
            if not ep.empty:
                paths = pd.concat([paths, ep], ignore_index=True)
    scored = _rescore(cfg, z, paths, dev_end, H)
    scored.to_parquet(adir / "dev_scored.parquet")

    den = BT.mase_denominators(scored, "naive_mevsimsel_12",
                               cfg["backtest"]["mase"]["min_denominator_obs"])
    summ = SEL.summarize(scored, den)
    summ.to_csv(out_dir(cfg, "tables") / "03a_gelistirme_ozet.csv",
                index=False, encoding="utf-8-sig")

    sel_scored = BT.scored_for_selection(scored, len(_yem(cfg)))
    tam, kismi = BT.complete_yearend_years(scored, len(_yem(cfg)))
    if not kismi.empty:
        kismi.to_csv(out_dir(cfg, "tables") / "03e_kismi_yil_yilsonu.csv",
                     index=False, encoding="utf-8-sig")
    scores = SEL.selection_scores(sel_scored, cfg["selection"]["weights"],
                                  cfg["selection"]["min_common_origins"])
    scores.to_csv(out_dir(cfg, "tables") / "03b_gelistirme_siralamasi.csv",
                  index=False, encoding="utf-8-sig")

    rt = paths.groupby("model")["runtime_sec"].mean().to_dict()
    # Tablo 12 — hesaplama maliyeti (beraberlik bozmada kullanılan ölçü)
    rt_tbl = (paths.groupby("model")["runtime_sec"]
              .agg(["count", "mean", "median", "max", "sum"]).reset_index())
    rt_tbl.columns = ["model", "n_baslangic", "ort_sn_baslangic", "medyan_sn",
                      "en_uzun_sn", "toplam_sn"]
    rt_tbl["asama"] = "geliştirme"
    rt_tbl["tepe_bellek_mb_surec"] = round(peak_memory_mb(), 1)
    rt_tbl = rt_tbl.sort_values("toplam_sn", na_position="last")
    rt_tbl.to_csv(out_dir(cfg, "tables") / "12_calisma_suresi_bellek.csv",
                  index=False, encoding="utf-8-sig")
    meta = {s.key: {"family": s.family, "complexity_rank": s.complexity_rank}
            for s in specs}
    for m in scored["model"].unique():
        if m.startswith("BIRLESIM"):
            meta[m] = {"family": "ensemble", "complexity_rank": 9}
    sel = SEL.choose(scores, meta, cfg, rt, ensemble_members=members)
    log(f"SEÇİLEN (yalnızca geliştirme skoruyla): {sel.winner}  S={sel.score:.4f}")

    spec_map = {s.key: s for s in specs}
    win_spec = spec_map.get(sel.winner)
    frozen_extra = {
        "kazanan_yapilandirma": ({
            "model": sel.winner,
            "aile": win_spec.family if win_spec else "ensemble",
            "pencere": (("tüm geçmiş" if win_spec.window == 0 else f"son {win_spec.window} ay")
                        if win_spec else "üye modellerin kendi pencereleri"),
            "pencere_ay": (win_spec.window if win_spec else None),
            "donusum": win_spec.transform if win_spec else "log",
        }),
        "alternatifler": sel.alternatives,
        "birlesim": {"uyeler": sel.ensemble_members,
                     "olcek": cfg["selection"]["ensemble"]["scale"],
                     "yontemler": cfg["selection"]["ensemble"]["methods"]},
        "kalibrasyon": cfg["calibration"],
        "mase": cfg["backtest"]["mase"],
        "aday_listesi": [s.key for s in specs],
        "timesfm_durumu": tfm.dict(),
        "basitlik_notu": SIMPLICITY_NOTE,
    }
    fpath = out_dir(cfg, "selection") / "frozen_selection.json"
    SEL.freeze(sel, fpath, frozen_extra)
    log(f"  dondurulmuş seçim yazıldı: {fpath}")

    # alt dönem analizi (yalnızca dayanıklılık açıklaması için)
    rows = []
    for sp in cfg["split"]["subperiods"]:
        s0, s1 = pd.Period(sp["start"], freq="M"), pd.Period(sp["end"], freq="M")
        sub = sel_scored[(sel_scored["target_end"] >= s0) & (sel_scored["target_end"] <= s1)]
        sc = SEL.selection_scores(sub, cfg["selection"]["weights"], 1)
        sc["alt_donem"] = sp["name"]
        rows.append(sc)
    if rows:
        pd.concat(rows).to_csv(out_dir(cfg, "tables") / "03c_alt_donem_siralamasi.csv",
                               index=False, encoding="utf-8-sig")
    write_manifest(cfg, "select", {"secim": sel.dict(), "dondurulmus_dosya": str(fpath)})
    return {"selection": sel}


def stage_evaluate(cfg: dict, args) -> dict:
    """Nihai holdout. Dondurulmuş seçim dosyası ZORUNLUDUR."""
    fpath = out_dir(cfg, "selection") / "frozen_selection.json"
    frozen = SEL.load_frozen(fpath)
    log(f"Dondurulmuş seçim yüklendi: {frozen['winner']} (donduruldu: {frozen['frozen_at']})")

    bundle, z, specs, tfm = _prepare(cfg, args)
    H = int(cfg["horizon"])
    o_start = pd.Period(cfg["split"]["holdout_start_origin"], freq="M")
    score_end = pd.Period(cfg["split"]["holdout_end"], freq="M")
    origins = [p for p in z.index if o_start <= p <= score_end]
    log(f"Nihai test: {len(specs)} aday × {len(origins)} başlangıç "
        f"({origins[0]} → {origins[-1]})")

    cached = out_dir(cfg) / "test_paths_raw.parquet"
    if args.reuse_paths and cached.exists():
        log("  --reuse-paths: kayıtlı tahmin yolları yeniden kullanılıyor (yeniden eğitim yok)")
        paths = pd.read_parquet(cached)
        paths["origin"] = pd.PeriodIndex(paths["origin"].astype(str), freq="M")
        failures = pd.DataFrame()
        elapsed = 0.0
    else:
        t0 = time.perf_counter()
        paths, failures = _run_paths(cfg, z, specs, origins, H, log)
        elapsed = time.perf_counter() - t0
        paths.to_parquet(cached)

    members = frozen["frozen_extra"]["birlesim"]["uyeler"]
    extra = []
    for method in cfg["selection"]["ensemble"]["methods"]:
        name = f"BIRLESIM_{method}_{len(members)}"
        ep = BT.ensemble_paths(paths, members, name, method)
        if not ep.empty:
            extra.append(ep)
    if extra:
        paths = pd.concat([paths] + extra, ignore_index=True)

    actual = BT.realized_frame(z, origins, H, score_end, _yem(cfg))
    pred = BT.predicted_frame(z, paths, H, _yem(cfg))
    scored = BT.score_frame(pred, actual)

    # MASE paydası: geliştirme + test kayıtlarından oluşan ORTAK, önceden
    # tanımlanmış geçmişten; her başlangıçta yalnızca O ANA KADAR gerçekleşmiş
    # referans hataları kullanılır ve tüm modeller için aynıdır.
    dev_prev = pd.read_parquet(out_dir(cfg) / "dev_scored.parquet")
    dev_prev["origin"] = pd.PeriodIndex(dev_prev["origin"], freq="M")
    dev_prev["target_end"] = pd.PeriodIndex(dev_prev["target_end"], freq="M")
    combined = pd.concat([dev_prev, scored], ignore_index=True)
    den = BT.mase_denominators(combined, "naive_mevsimsel_12",
                               cfg["backtest"]["mase"]["min_denominator_obs"])
    den = den[den["origin"].isin(scored["origin"].unique())]
    summ = SEL.summarize(scored, den)
    summ.to_csv(out_dir(cfg, "tables") / "03d_nihai_test_ozet.csv",
                index=False, encoding="utf-8-sig")
    scored.to_parquet(out_dir(cfg) / "test_scored.parquet")
    paths.to_parquet(out_dir(cfg) / "test_paths.parquet")
    _write_failures(cfg, failures, "10_basarisiz_denemeler_test.csv")
    dev_scored = pd.read_parquet(out_dir(cfg) / "dev_scored.parquet")
    dev_scored["origin"] = pd.PeriodIndex(dev_scored["origin"], freq="M")
    dev_scored["target_end"] = pd.PeriodIndex(dev_scored["target_end"], freq="M")

    winner = frozen["winner"]
    alts = frozen["frozen_extra"]["alternatifler"]

    _table_horizons(cfg, dev_scored, scored)
    _table_yearend(cfg, dev_scored, scored, [winner] + alts[:2])
    _table_intervals(cfg, dev_scored, scored, winner)
    _table_bootstrap(cfg, scored, winner, alts[:2])

    log(f"  süre: {elapsed:.1f} s")
    write_manifest(cfg, "evaluate", {
        "dondurulmus_secim": frozen["winner"], "n_baslangic": len(origins),
        "sure_sn": round(elapsed, 1),
        "not": ("Nihai test yalnızca performansı DENETLER. Test kazananına "
                "bakılarak seçilmiş model değiştirilmemiştir."),
    })
    return {"scored": scored}


def stage_forecast(cfg: dict, args) -> dict:
    fpath = out_dir(cfg, "selection") / "frozen_selection.json"
    frozen = SEL.load_frozen(fpath)
    bundle, z, specs, tfm = _prepare(cfg, args)
    H = int(cfg["horizon"])
    cutoff = pd.Period(cfg["data"]["cutoff"], freq="M")
    spec_map = {s.key: s for s in specs}
    winner = frozen["winner"]

    # Kalibrasyon kaydı: geliştirme + nihai test kayıtlarının tamamı. Zaman
    # kuralı gereği aşağıda yalnızca hedefi veri kesimine kadar GERÇEKLEŞMİŞ
    # hatalar kullanılır; yöntem, minimum örnek ve güncelleme kuralı testten
    # önce dondurulmuştur (config.calibration).
    hist_frames = []
    for fn in ("dev_scored.parquet", "test_scored.parquet"):
        fp = out_dir(cfg) / fn
        if fp.exists():
            d = pd.read_parquet(fp)
            d["origin"] = pd.PeriodIndex(d["origin"], freq="M")
            d["target_end"] = pd.PeriodIndex(d["target_end"], freq="M")
            hist_frames.append(d)
    dev_scored = pd.concat(hist_frames, ignore_index=True)

    def path_for(model_key: str) -> np.ndarray:
        if model_key.startswith("BIRLESIM"):
            method = model_key.split("_")[1]
            members = frozen["frozen_extra"]["birlesim"]["uyeler"]
            mats = [FC.fit_final(spec_map[m], z, H)[0] for m in members]
            arr = np.vstack(mats)
            return arr.mean(axis=0) if method == "mean" else np.median(arr, axis=0)
        return FC.fit_final(spec_map[model_key], z, H)[0]

    log(f"Nihai tahmin: {winner} (eğitim penceresi korunuyor: "
        f"{frozen['frozen_extra']['kazanan_yapilandirma']['pencere']})")
    z_path = path_for(winner)
    table = FC.build_forecast_table(z, z_path, cutoff, bundle.monthly, winner)
    summary = FC.period_summaries(z, z_path, cutoff, bundle.monthly)

    # aralıklar: yalnızca gerçekleşmiş geçmiş hatalardan
    preds = {r["target"]: r["pred"] for _, r in
             BT.predicted_frame(z, pd.DataFrame({
                 "origin": [cutoff] * H, "model": [winner] * H,
                 "h": list(range(1, H + 1)), "z_pred": z_path}), H,
                 (cutoff.month,)).iterrows()}
    # Yılsonu nokta tahmini DOĞRULANMIŞ RESMÎ YTD başlangıcı ile hesaplanır;
    # aralık da bu değerin etrafında merkezlenir.
    ye_row = summary[summary["olcu"].str.contains("yılsonu")]
    if len(ye_row):
        preds["yearend"] = float(ye_row["deger_pct"].iloc[0])
    iv = CAL.forward_intervals(dev_scored, winner, cfg, preds, cutoff)
    iv.to_csv(out_dir(cfg, "tables") / "07b_nihai_tahmin_araliklari.csv",
              index=False, encoding="utf-8-sig")

    ivm = iv.set_index("target")
    for i in range(H):
        key = f"m{i+1}"
        for lv in (80, 95):
            table.loc[i, f"aylik_lo{lv}"] = ivm.at[key, f"lo{lv}"] if key in ivm.index else np.nan
            table.loc[i, f"aylik_hi{lv}"] = ivm.at[key, f"hi{lv}"] if key in ivm.index else np.nan
    table["aralik_olcusu"] = "AYLIK yüzde değişim (bileşik dönem aralığı değildir)"
    table.to_csv(out_dir(cfg, "tables") / "06_aylik_tahminler.csv",
                 index=False, encoding="utf-8-sig")
    summary.to_csv(out_dir(cfg, "tables") / "07_donem_ozetleri.csv",
                   index=False, encoding="utf-8-sig")

    # ana model + iki alternatif
    alts = frozen["frozen_extra"]["alternatifler"]
    comp_rows = []
    alt_tables = {}
    for label, key in [("ana", winner)] + [(f"alternatif{i+1}", a) for i, a in enumerate(alts)]:
        try:
            zp = path_for(key)
        except Exception as exc:
            log(f"  {key} nihai tahmini üretilemedi: {exc}")
            continue
        s = FC.period_summaries(z, zp, cutoff, bundle.monthly)
        s["rol"], s["model"] = label, key
        comp_rows.append(s)
        at = FC.build_forecast_table(z, zp, cutoff, bundle.monthly, key)
        alt_tables[key] = at
        if label != "ana":
            slug = "".join(ch if ch.isalnum() else "_" for ch in key).strip("_")[:60]
            at.to_csv(out_dir(cfg, "tables") / f"06_aylik_tahminler_{slug}.csv",
                      index=False, encoding="utf-8-sig")
    comp = pd.concat(comp_rows, ignore_index=True) if comp_rows else pd.DataFrame()
    comp.to_csv(out_dir(cfg, "tables") / "08_model_karsilastirmasi.csv",
                index=False, encoding="utf-8-sig")

    payload = {
        "veri_kesimi": str(cutoff), "model": winner,
        "tahmin_donemi": f"{cutoff+1} – {cutoff+H}",
        "uretim_zamani": datetime.now(timezone.utc).isoformat(),
        "aylik_tahminler": json.loads(table.to_json(orient="records")),
        "donem_ozetleri": json.loads(summary.to_json(orient="records")),
        "araliklar": json.loads(iv.to_json(orient="records")),
        "secim": {k: frozen[k] for k in ("winner", "score", "rule", "weights", "frozen_at")},
        "timesfm_durumu": tfm.dict(),
    }
    (out_dir(cfg, "forecast") / "nihai_tahmin.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    FC.archive(payload, out_dir(cfg, "forecast", "arsiv"))

    # ham geçmiş tahminler (parquet)
    frames = []
    for name in ("dev_paths", "test_paths"):
        p = out_dir(cfg) / f"{name}.parquet"
        if p.exists():
            df = pd.read_parquet(p)
            df["asama"] = "gelistirme" if name.startswith("dev") else "nihai_test"
            frames.append(df)
    final_df = pd.DataFrame({"origin": [str(cutoff)] * H, "model": [winner] * H,
                             "h": range(1, H + 1), "z_pred": z_path,
                             "runtime_sec": np.nan, "asama": "nihai_tahmin"})
    frames.append(final_df)
    allp = pd.concat(frames, ignore_index=True)
    allp["origin"] = allp["origin"].astype(str)
    allp.to_parquet(out_dir(cfg) / "ham_gecmis_tahminler.parquet")

    write_manifest(cfg, "forecast", {"model": winner, "veri_kesimi": str(cutoff),
                                     "tahmin_donemi": payload["tahmin_donemi"]})
    log(f"  {cutoff+1}–{cutoff+H} tahmini üretildi.")
    return {"table": table, "summary": summary, "alt_tables": alt_tables}


def stage_report(cfg: dict, args) -> dict:
    from src import plots, report
    log("Grafikler üretiliyor…")
    plots.make_all(cfg)
    log("Rapor üretiliyor…")
    paths = report.build(cfg)
    for p in paths:
        log(f"  {p}")
    return {"report": paths}



# --------------------------------------------------------------------------- #
# ek değerlendirme tabloları
# --------------------------------------------------------------------------- #
def _table_horizons(cfg, dev, test) -> None:
    """Tablo 4 — ufuk bazında hata ve gözlem sayıları (referansa göre iyileşme dahil)."""
    rows = []
    combined = pd.concat([d for d in (dev, test) if d is not None and not d.empty],
                         ignore_index=True)
    for tag, df in (("geliştirme", dev), ("nihai test", test)):
        if df is None or df.empty:
            continue
        den = BT.mase_denominators(combined, "naive_mevsimsel_12",
                                   cfg["backtest"]["mase"]["min_denominator_obs"])
        den = den[den["origin"].isin(df["origin"].unique())]
        d = df.merge(den, on=["origin", "target"], how="left")
        ref = "naive_mevsimsel_12"
        for (model, target), g in d.groupby(["model", "target"]):
            gr = d[(d["model"] == ref) & (d["target"] == target)]
            common = set(g["origin"]) & set(gr["origin"])
            gi = g[g["origin"].isin(common)]
            gri = gr[gr["origin"].isin(common)]
            imp = np.nan
            if len(gri) and MX.mae(gri["err"].to_numpy()) > 0:
                imp = 100.0 * (1 - MX.mae(gi["err"].to_numpy()) / MX.mae(gri["err"].to_numpy()))
            rows.append({
                "asama": tag, "model": model, "hedef": target, "n": len(g),
                "MAE": MX.mae(g["err"].to_numpy()), "RMSE": MX.rmse(g["err"].to_numpy()),
                "ME": MX.mean_error(g["err"].to_numpy()),
                "MASE": MX.mase(g["err"].to_numpy(), g["mase_den"].to_numpy()),
                "MASE_payda_n": int(g["den_n"].median()) if "den_n" in g else 0,
                "referansa_gore_iyilesme_pct": imp,
                "ortak_n_referansla": len(gi),
            })
    pd.DataFrame(rows).to_csv(out_dir(cfg, "tables") / "04_ufuk_bazli_hatalar.csv",
                              index=False, encoding="utf-8-sig")


def _table_yearend(cfg, dev, test, models) -> None:
    """Tablo 5 — yıl bazında yılsonu tahminleri ve gerçekleşmeler."""
    rows = []
    for tag, df in (("geliştirme", dev), ("nihai test", test)):
        if df is None or df.empty:
            continue
        sub = df[(df["target"] == "yearend") & (df["model"].isin(models))].copy()
        for _, r in sub.iterrows():
            o = r["origin"]
            rows.append({"asama": tag, "yil": r["target_end"].year, "baslangic": str(o),
                         "baslangic_ayi": o.month,
                         "ufuk_ay": 12 - o.month, "model": r["model"],
                         "tahmin_pct": r["pred"], "gerceklesme_pct": r["actual"],
                         "hata_pp": r["err"]})
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["asama", "yil", "baslangic_ayi", "model"])
    df.to_csv(out_dir(cfg, "tables") / "05_yilsonu_tahminleri.csv",
              index=False, encoding="utf-8-sig")

    # Ağustos → Aralık ayrı raporu (güncel kullanımın doğrudan karşılığı)
    if not df.empty:
        aug = df[df["baslangic_ayi"] == 8]
        rows2 = []
        for (tag, model), g in aug.groupby(["asama", "model"]):
            rows2.append({"asama": tag, "model": model, "n_yil": len(g),
                          "MAE_agustos_aralik": MX.mae(g["hata_pp"].to_numpy()),
                          "ME": MX.mean_error(g["hata_pp"].to_numpy())})
        pd.DataFrame(rows2).to_csv(
            out_dir(cfg, "tables") / "05b_agustos_aralik_mae.csv",
            index=False, encoding="utf-8-sig")


def _table_intervals(cfg, dev, test, winner) -> None:
    """Tablo 9 — aralık kapsaması/genişliği/skorları (geliştirme + nihai test).

    Kalibrasyon, geliştirme + test kayıtlarının TAMAMI üzerinden genişleyen
    (expanding) biçimde yürütülür; zaman kuralı gereği her başlangıçta yalnızca
    o ana kadar GERÇEKLEŞMİŞ hatalar kullanılır. Böylece nihai test dönemi,
    geliştirme döneminde biriken hata geçmişinden yararlanır — bu, ileriye
    dönük kullanımın birebir karşılığıdır.
    """
    combined = pd.concat([d for d in (dev, test) if d is not None and not d.empty],
                         ignore_index=True)
    cal_all = CAL.calibrate(combined, winner, cfg)
    frames = []
    for tag, df in (("geliştirme", dev), ("nihai test", test)):
        if df is None or df.empty or cal_all.empty:
            continue
        cal = cal_all[cal_all["origin"].isin(df["origin"].unique())]
        if cal.empty:
            continue
        rep = CAL.coverage_report(cal, cfg)
        rep.insert(0, "asama", tag)
        frames.append(rep)
        cal.to_parquet(out_dir(cfg) / f"kalibrasyon_{'dev' if tag=='geliştirme' else 'test'}.parquet")
    if frames:
        out = pd.concat(frames, ignore_index=True)
        out["model"] = winner
        out.to_csv(out_dir(cfg, "tables") / "09_aralik_kapsamasi.csv",
                   index=False, encoding="utf-8-sig")


def _table_bootstrap(cfg, scored, winner, alts) -> None:
    """Tablo 11 — blok bootstrap ile model farkları + DM (destekleyici)."""
    rows = []
    nb = int(cfg["bootstrap"]["n_boot"])
    seed = int(cfg["project"]["seed"])
    ref = "naive_mevsimsel_12"
    for target in ("yearend", "c6", "c12"):
        base = scored[(scored["model"] == winner) & (scored["target"] == target)]
        for other in [m for m in ([ref] + list(alts)) if m != winner]:
            comp = scored[(scored["model"] == other) & (scored["target"] == target)]
            merged = base.merge(comp, on="origin", suffixes=("_a", "_b"))
            if merged.empty:
                continue
            blocks = (pd.PeriodIndex(merged["target_end_a"], freq="M").year
                      if target == "yearend"
                      else pd.PeriodIndex(merged["target_end_a"], freq="M").year)
            bs = MX.block_bootstrap_diff(merged["err_a"].to_numpy(),
                                         merged["err_b"].to_numpy(),
                                         np.asarray(blocks), nb, seed)
            dm = MX.diebold_mariano(merged["err_a"].to_numpy(),
                                    merged["err_b"].to_numpy(),
                                    h=6 if target == "c6" else 12)
            rows.append({"hedef": target, "model_A": winner, "model_B": other,
                         "MAE_farki_A_eksi_B": bs["diff"], "boot_lo95": bs["lo95"],
                         "boot_hi95": bs["hi95"], "n": bs["n"],
                         "n_blok(yil)": bs.get("n_blocks", 0),
                         "DM_istatistigi": dm["dm"], "DM_p": dm["p"],
                         "DM_notu": dm["note"]})
    pd.DataFrame(rows).to_csv(out_dir(cfg, "tables") / "11_bootstrap_karsilastirma.csv",
                              index=False, encoding="utf-8-sig")


STAGES = {"data": stage_data, "backtest": stage_backtest, "select": stage_select,
          "evaluate": stage_evaluate, "forecast": stage_forecast,
          "report": stage_report}


def main() -> int:
    ap = argparse.ArgumentParser(description="KKTC TÜFE tahmin sistemi")
    ap.add_argument("stage", choices=list(STAGES) + ["all"])
    ap.add_argument("--config", default=None)
    ap.add_argument("--refresh", action="store_true", help="ham veriyi yeniden indir")
    ap.add_argument("--reuse-paths", action="store_true",
                    help="nihai testte kayıtlı tahmin yollarını yeniden kullan")
    ap.add_argument("--smoke", type=int, default=0,
                    help="yalnızca son N başlangıçla küçük deneme (süre/bellek ölçümü)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    set_seed(int(cfg["project"]["seed"]))
    order = ["data", "backtest", "select", "evaluate", "forecast", "report"]
    stages = order if args.stage == "all" else [args.stage]
    t0 = time.perf_counter()
    for s in stages:
        log(f"=== AŞAMA: {s} ===")
        STAGES[s](cfg, args)
    log(f"Toplam süre: {time.perf_counter()-t0:.1f} s, "
        f"tepe bellek: {peak_memory_mb():.0f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
