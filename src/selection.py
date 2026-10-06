"""Model seçimi ve değerlendirme özetleri.

Seçim YALNIZCA geliştirme skoruyla yapılır. Nihai test tablosu performansı
denetler; test kazananına bakılarak seçim değiştirilmez.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd

from . import metrics as MX

MAIN_TARGETS = {"yearend": "yearend", "c6": "c6", "c12": "c12"}


def common_origins(scored: pd.DataFrame, target: str,
                   models: list[str] | None = None) -> pd.Index:
    """Karşılaştırılan modellerin HEPSİNDE bulunan ortak başlangıçlar."""
    sub = scored[scored["target"] == target]
    if models is not None:
        sub = sub[sub["model"].isin(models)]
    if sub.empty:
        return pd.Index([])
    counts = sub.groupby("origin")["model"].nunique()
    n_models = sub["model"].nunique()
    return counts[counts == n_models].index


def restrict_to_common(scored: pd.DataFrame, targets: list[str],
                       models: list[str]) -> pd.DataFrame:
    """Skorları ortak başlangıçlarla sınırlar (daha kolay dönem avantajını önler)."""
    keep = []
    for t in targets:
        idx = common_origins(scored, t, models)
        keep.append(scored[(scored["target"] == t) & (scored["origin"].isin(idx))])
    return pd.concat(keep, ignore_index=True) if keep else scored.iloc[0:0]


def summarize(scored: pd.DataFrame, mase_den: pd.DataFrame | None = None) -> pd.DataFrame:
    """Model × hedef bazında hata özetleri ve gözlem sayıları."""
    if scored.empty:
        return pd.DataFrame()
    df = scored
    if mase_den is not None and not mase_den.empty:
        df = df.merge(mase_den, on=["origin", "target"], how="left")
    rows = []
    for (model, target), g in df.groupby(["model", "target"]):
        err = g["err"].to_numpy()
        row = {
            "model": model, "hedef": target, "n": int(len(g)),
            "MAE": MX.mae(err), "RMSE": MX.rmse(err), "ME": MX.mean_error(err),
            "MAPE": MX.mape(g["actual"].to_numpy(), g["pred"].to_numpy()),
            "en_kotu_hata": float(np.max(np.abs(err))) if len(err) else np.nan,
            "en_kotu_donem": (str(g.loc[g["err"].abs().idxmax(), "target_end"])
                              if len(g) else ""),
        }
        if "mase_den" in g.columns:
            row["MASE"] = MX.mase(err, g["mase_den"].to_numpy())
            row["MASE_payda_n"] = int(g["den_n"].median()) if "den_n" in g else 0
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["hedef", "MAE"]).reset_index(drop=True)


def selection_scores(scored: pd.DataFrame, weights: dict,
                     min_common: int = 12) -> pd.DataFrame:
    """S = 0.60*MAE_yılsonu + 0.30*MAE_6ay + 0.10*MAE_12ay (ortak başlangıçlarda)."""
    models = sorted(scored["model"].unique())
    targets = list(MAIN_TARGETS.values())
    common = restrict_to_common(scored, targets, models)
    rows = []
    for model in models:
        entry = {"model": model}
        total, ok = 0.0, True
        for t in targets:
            g = common[(common["model"] == model) & (common["target"] == t)]
            m = MX.mae(g["err"].to_numpy())
            entry[f"MAE_{t}"] = m
            entry[f"n_{t}"] = int(len(g))
            if not np.isfinite(m) or len(g) < min_common:
                ok = False
            else:
                total += weights[{"yearend": "yearend", "c6": "c6", "c12": "c12"}[t]] * m
        entry["S"] = total if ok else np.nan
        entry["uygun"] = ok
        rows.append(entry)
    out = pd.DataFrame(rows).sort_values("S", na_position="last").reset_index(drop=True)
    out["sira"] = np.arange(1, len(out) + 1)
    return out


@dataclass
class Selection:
    winner: str
    score: float
    rule: str
    tied_with: list
    complexity_rank: int
    runtime_sec: float
    weights: dict
    dev_end: str
    n_candidates: int
    alternatives: list
    ensemble_members: list
    frozen_at: str
    notes: str = ""

    def dict(self) -> dict:
        return asdict(self)


def choose(scores: pd.DataFrame, specs_meta: dict, cfg: dict,
           runtimes: dict[str, float],
           ensemble_members: list[str] | None = None) -> Selection:
    """Yapılandırmada önceden tanımlı kurala göre kazananı belirler."""
    from datetime import datetime, timezone

    sel = cfg["selection"]
    eligible = scores[scores["uygun"]].copy()
    if eligible.empty:
        raise RuntimeError("Seçim için uygun aday yok (ortak başlangıç sayısı yetersiz).")
    best = float(eligible["S"].min())
    eps = float(sel["zero_score_epsilon"])
    thr = float(sel["tie_relative_threshold"])
    if best <= eps:
        # sıfır/sıfıra yakın skor: göreli eşik anlamsızdır, mutlak eşik kullanılır
        tied = eligible[eligible["S"] <= best + eps]
        rule = (f"En iyi skor sıfıra yakın ({best:.2e}); göreli %{thr*100:.0f} eşiği "
                f"yerine mutlak eşik {eps:.1e} uygulandı.")
    else:
        tied = eligible[eligible["S"] <= best * (1.0 + thr)]
        rule = (f"En iyi skora göre göreli farkı %{thr*100:.0f}'den küçük adaylar "
                "berabere sayıldı; ardından basitlik, sonra hesaplama maliyeti.")
    tied = tied.copy()
    tied["complexity_rank"] = tied["model"].map(
        lambda m: specs_meta.get(m, {}).get("complexity_rank", 99))
    tied["runtime_sec"] = tied["model"].map(lambda m: runtimes.get(m, np.inf))
    tied = tied.sort_values(sel["tie_break"]).reset_index(drop=True)
    winner = tied.loc[0, "model"]

    # birleşim üyeleri: farklı ailelerden en iyi 3 (birleşimlerin kendisi hariç)
    members: list[str] = list(ensemble_members or [])
    if sel["ensemble"]["enabled"] and not members:
        seen = set()
        for _, r in scores[scores["uygun"]].sort_values("S").iterrows():
            fam = specs_meta.get(r["model"], {}).get("family", "?")
            if fam == "ensemble":
                continue
            if sel["ensemble"]["distinct_families"] and fam in seen:
                continue
            seen.add(fam)
            members.append(r["model"])
            if len(members) >= int(sel["ensemble"]["top_k"]):
                break

    alts = [m for m in scores[scores["uygun"]].sort_values("S")["model"].tolist()
            if m != winner][:2]

    return Selection(
        winner=winner, score=float(tied.loc[0, "S"]), rule=rule,
        tied_with=[m for m in tied["model"].tolist() if m != winner],
        complexity_rank=int(tied.loc[0, "complexity_rank"]),
        runtime_sec=float(tied.loc[0, "runtime_sec"]),
        weights=sel["weights"], dev_end=cfg["split"]["dev_end"],
        n_candidates=int(len(scores)), alternatives=alts,
        ensemble_members=members,
        frozen_at=datetime.now(timezone.utc).isoformat(),
        notes=("Seçim yalnızca geliştirme doğrulaması skorlarıyla yapılmıştır. "
               "Nihai holdout bu aşamada hiç kullanılmamıştır."))


def freeze(selection: Selection, path: Path, extra: dict) -> None:
    payload = selection.dict() | {"frozen_extra": extra}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_frozen(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Dondurulmuş seçim dosyası bulunamadı: {path}. "
            "Nihai test aşaması, dondurulmuş seçim dosyası olmadan çalışmaz. "
            "Önce `python run.py select` çalıştırın.")
    return json.loads(path.read_text(encoding="utf-8"))
