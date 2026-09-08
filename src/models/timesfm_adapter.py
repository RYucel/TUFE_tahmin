"""TimesFM 3 adaptörü (resmî kullanım arayüzü).

Resmî kaynaklar
---------------
* kod    : https://github.com/google-research/timesfm  (paket ``timesfm`` 3.0.1;
           TimesFM 3.0 arayüzü ``timesfm3`` modülünde)
* ağırlık: https://huggingface.co/google/timesfm-3.0-pytorch

Resmî depodan doğrulanan arayüz (``timesfm3/torch/timesfm3_forecaster.py``)::

    from timesfm3 import TimesFM3Forecaster
    f = TimesFM3Forecaster.from_pretrained("google/timesfm-3.0-pytorch",
                                           device="cuda")
    out = list(f.predict_batch(contexts=[ctx], horizon=12,
                               return_quantiles=True, make_positive=False))
    out[0].forecast     # (h,)      medyan nokta tahmini
    out[0].quantiles    # (h, 9)    0,1 … 0,9 kuantilleri

Önemli teknik notlar
--------------------
* ``TimesFM3Evaluator`` alt sınıfı ``make_positive=True`` varsayılanıyla gelir ve
  negatif değerleri kırpar. Bizim modelleme serimiz aylık LOG DEĞİŞİM olduğu ve
  deflasyon aylarında negatif olabildiği için ``TimesFM3Forecaster`` sınıfı
  ``make_positive=False`` ile kullanılır.
* Model kuantil ızgarası 0,1–0,9'dur; **%95 aralığı desteklemez**. Ek yöntem
  olmadan bu modelden %95 aralık sunulmaz (%80 aralık 0,1/0,9'dan gelir).
* Ağırlıklar süreç başına BİR KEZ yüklenir (``_MODEL_CACHE``); aksi hâlde her
  geriye dönük test başlangıcında yeniden yükleme yapılır ve çalışma süresi
  kullanılamaz hâle gelir.

Lisans uyarısı
--------------
TimesFM kaynak kodu Apache-2.0'dır ve 2.5'e kadarki ağırlıklar da Apache-2.0'dır.
Ancak **TimesFM 3.0 ön eğitimli ağırlıkları ayrı bir
``timesfm-non-commercial-license-v1.0`` lisansı altındadır ve ticari/üretim
kullanımına KAPALIDIR** (resmî README). Bu nedenle TimesFM 3.0 yalnızca
"araştırmada en başarılı model" tarafında değerlendirilir; üretimde
kullanılabilecek en başarılı model ayrıca raporlanır.

TimesFM 3 yerine sessizce 2.5 veya başka bir sürüm KULLANILMAZ.
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .base import BaseModel

HF_MODEL_DEFAULT = "google/timesfm-3.0-pytorch"
WEIGHTS_LICENSE = "timesfm-non-commercial-license-v1.0 (ticari/üretim kullanımı yasak)"
CODE_LICENSE = "Apache-2.0"
QUANTILE_GRID = np.round(np.arange(1, 10) / 10.0, 2)   # 0.1 … 0.9

# Ağırlıklar süreç başına bir kez yüklenir: {(checkpoint, device): forecaster}
_MODEL_CACHE: dict[tuple[str, str], object] = {}


@dataclass
class TimesFMStatus:
    available: bool
    detail: str
    package_version: str | None = None
    code_import: str = ""
    weights_ref: str = HF_MODEL_DEFAULT
    weights_revision: str | None = None
    weights_local_path: str | None = None
    weights_license: str = WEIGHTS_LICENSE
    code_license: str = CODE_LICENSE
    device: str = "cpu"
    quantile_grid: list = field(default_factory=lambda: list(QUANTILE_GRID))
    supports_95: bool = False

    def dict(self) -> dict:
        return {k: (list(v) if isinstance(v, np.ndarray) else v)
                for k, v in self.__dict__.items()}


def _pkg_version() -> str | None:
    try:
        import importlib.metadata as md
        return md.version("timesfm")
    except Exception:
        return None


def pick_device() -> str:
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def load_forecaster(checkpoint: str = HF_MODEL_DEFAULT, device: str | None = None):
    """Ön eğitimli TimesFM 3 tahmincisini yükler (süreç başına önbelleklenir)."""
    device = device or pick_device()
    key = (checkpoint, device)
    if key not in _MODEL_CACHE:
        from timesfm3 import TimesFM3Forecaster
        _MODEL_CACHE[key] = TimesFM3Forecaster.from_pretrained(checkpoint, device=device)
    return _MODEL_CACHE[key]


def probe(cfg: dict) -> TimesFMStatus:
    """TimesFM 3'ün bu ortamda GERÇEKTEN çalıştırılabilirliğini dener.

    Üç aşama ayrı ayrı raporlanır: (1) kodun içe aktarılması, (2) ağırlıkların
    indirilmesi, (3) modelin kurulup küçük bir tahmin üretmesi. Hangi aşamada
    takıldığı gizlenmez.
    """
    hf_model = cfg.get("timesfm", {}).get("hf_model", HF_MODEL_DEFAULT)
    version = _pkg_version()

    try:
        importlib.import_module("timesfm3")
    except Exception as exc:
        return TimesFMStatus(
            False,
            f"TimesFM 3 kodu içe aktarılamadı: {type(exc).__name__}: {exc}. "
            "Kurulum: pip install 'timesfm[torch]' veya "
            "pip install 'git+https://github.com/google-research/timesfm.git'",
            version, code_import="başarısız", weights_ref=hf_model)

    try:
        from huggingface_hub import snapshot_download
        path = snapshot_download(hf_model)
    except Exception as exc:
        return TimesFMStatus(
            False,
            "TimesFM 3 kodu yüklendi (import başarılı) ancak ön eğitimli "
            f"ağırlıklar indirilemedi ({hf_model}): {type(exc).__name__}: {exc}. "
            "Bu ortamda huggingface.co erişimi engellenmiş görünüyor; "
            "TimesFM 3 ÇALIŞTIRILAMAMIŞTIR.",
            version, code_import="başarılı", weights_ref=hf_model)

    device = pick_device()
    try:
        f = load_forecaster(path, device)
        ctx = np.linspace(0.0, 0.05, 128).astype(np.float32)
        out = list(f.predict_batch(contexts=[ctx], horizon=4,
                                   return_quantiles=False, make_positive=False))
        arr = np.asarray(out[0].forecast, dtype=float).reshape(-1)
        if arr.size < 4 or not np.all(np.isfinite(arr)):
            raise RuntimeError(f"Deneme tahmini geçersiz: {arr}")
    except Exception as exc:
        return TimesFMStatus(
            False,
            f"Ağırlıklar indirildi ancak model çalıştırılamadı: "
            f"{type(exc).__name__}: {exc}",
            version, code_import="başarılı", weights_ref=hf_model,
            weights_local_path=path, device=device)

    rev = None
    try:
        rev = str(path).rstrip("/").split("snapshots/")[-1].split("/")[0]
    except Exception:
        pass
    return TimesFMStatus(True, "TimesFM 3 kullanılabilir ve deneme tahmini üretildi.",
                         version, code_import="başarılı", weights_ref=hf_model,
                         weights_revision=rev, weights_local_path=path, device=device)


# --------------------------------------------------------------------------- #
class TimesFMZeroShot(BaseModel):
    """Tek değişkenli, İNCE AYARSIZ (zero-shot) TimesFM 3.0.

    Girdi dönüşümü (log aylık değişim) ve bağlam uzunluğu geliştirme
    doğrulamasında seçilir; model ağırlıkları hiç güncellenmez.
    """

    family, complexity_rank, min_obs = "foundation", 8, 36

    def __init__(self, cfg: dict, context_length: int = 512):
        self.cfg = cfg
        self.context_length = int(context_length)
        self.name = f"TimesFM-3.0(zero-shot,ctx={context_length})"
        self._ctx: np.ndarray | None = None

    def _forecaster(self):
        return load_forecaster(self.cfg["timesfm"]["hf_model"],
                               self.cfg["timesfm"].get("device"))

    def fit(self, z, exog=None):
        # Ön eğitimli model: "eğitim" yerine yalnızca geçmiş bağlam verilir.
        self._ctx = np.asarray(z, dtype=np.float32)[-self.context_length:]
        return self

    def predict(self, h):
        out = list(self._forecaster().predict_batch(
            contexts=[self._ctx], horizon=h,
            return_quantiles=False, make_positive=False))
        return np.asarray(out[0].forecast, dtype=float).reshape(-1)[:h]

    def predict_quantiles(self, h, levels):
        out = list(self._forecaster().predict_batch(
            contexts=[self._ctx], horizon=h,
            return_quantiles=True, make_positive=False))
        q = np.asarray(out[0].quantiles, dtype=float)[:h]     # (h, 9)
        res: dict[float, tuple[np.ndarray, np.ndarray]] = {}
        grid = list(QUANTILE_GRID)
        for lv in levels:
            lo_q, hi_q = round((1 - lv) / 2, 2), round(1 - (1 - lv) / 2, 2)
            if lo_q in grid and hi_q in grid:
                res[lv] = (q[:, grid.index(lo_q)], q[:, grid.index(hi_q)])
        # %95 modelin kuantil ızgarasında YOKTUR; ek yöntem olmadan üretilmez.
        return res or None


class TimesFMWithPastCovariates(TimesFMZeroShot):
    """TimesFM 3.0 + GEÇMİŞ yardımcı değişkenler (past-only covariates).

    Yardımcı değişkenler yalnızca tahmin başlangıcına kadar bilinen değerlerdir;
    gelecekteki gerçekleşmiş değerler kullanılmaz. Sepet özet serileri bu yolla
    verilir (bkz. features.item_summaries — doldurma/ölçekleme/faktör çıkarımı
    her eğitim diliminde yeniden yapılır).
    """

    family, complexity_rank = "foundation_aux", 8
    uses_exog = True

    def __init__(self, cfg: dict, context_length: int = 512,
                 items: pd.DataFrame | None = None, n_cov: int = 4):
        super().__init__(cfg, context_length)
        self.items = items
        self.n_cov = int(n_cov)
        self.name = f"TimesFM-3.0(zero-shot+sepet,ctx={context_length})"
        self._cov: np.ndarray | None = None

    def fit(self, z, exog=None):
        super().fit(z)
        self._cov = None
        if self.items is None:
            return self
        from ..features import item_summaries
        aux = item_summaries(self.items, upto=z.index[-1])
        if aux is None or aux.empty:
            return self
        aux = aux.reindex(z.index).ffill()
        cols = [c for c in aux.columns if aux[c].notna().all()][: self.n_cov]
        if not cols:
            return self
        mat = aux[cols].to_numpy(dtype=np.float32).T          # (n_cov, T)
        self._cov = mat[:, -len(self._ctx):]
        return self

    def predict(self, h):
        kw = {}
        if self._cov is not None and self._cov.shape[1] == len(self._ctx):
            kw["past_only_covariates"] = [self._cov]
        out = list(self._forecaster().predict_batch(
            contexts=[self._ctx], horizon=h, return_quantiles=False,
            make_positive=False, **kw))
        return np.asarray(out[0].forecast, dtype=float).reshape(-1)[:h]


# --------------------------------------------------------------------------- #
def batch_backtest_paths(cfg: dict, z: pd.Series, origins: list[pd.Period],
                         horizon: int, context_length: int,
                         model_key: str, batch_size: int = 64,
                         log=print) -> pd.DataFrame:
    """Zero-shot TimesFM için toplu (batched) geriye dönük test.

    TimesFM ince ayarsız kullanıldığı için her başlangıçta yeniden eğitim
    yoktur; yalnızca farklı bağlam pencereleriyle çıkarım yapılır. Bu nedenle
    tüm başlangıçların bağlamları tek seferde toplu olarak verilebilir.
    Sonuç, tek tek çalıştırmayla ÖZDEŞTİR — yalnızca daha hızlıdır.

    Sızıntı kuralı korunur: her bağlam yalnızca ``z[<= origin]`` içerir.
    """
    import time
    f = load_forecaster(cfg["timesfm"]["hf_model"], cfg["timesfm"].get("device"))
    rows: list[dict] = []
    for start in range(0, len(origins), batch_size):
        chunk = origins[start:start + batch_size]
        contexts, keep = [], []
        for o in chunk:
            hist = z[z.index <= o]
            if len(hist) < context_length // 8:
                continue
            contexts.append(np.asarray(hist, dtype=np.float32)[-context_length:])
            keep.append(o)
        if not contexts:
            continue
        t0 = time.perf_counter()
        outs = list(f.predict_batch(contexts=contexts, horizon=horizon,
                                    return_quantiles=False, make_positive=False))
        dt = (time.perf_counter() - t0) / max(len(keep), 1)
        for o, out in zip(keep, outs):
            path = np.asarray(out.forecast, dtype=float).reshape(-1)[:horizon]
            for h in range(1, horizon + 1):
                rows.append({"origin": o, "model": model_key, "h": h,
                             "z_pred": float(path[h - 1]),
                             "runtime_sec": dt if h == 1 else np.nan})
        log(f"    TimesFM toplu çıkarım: {start + len(keep)}/{len(origins)} başlangıç")
    out = pd.DataFrame(rows)
    if not out.empty:
        out["origin"] = pd.PeriodIndex(out["origin"], freq="M")
    return out
