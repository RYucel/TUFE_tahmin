"""TimesFM 3 adaptörü (resmî kullanım arayüzü).

Resmî kaynaklar:
  * kod    : https://github.com/google-research/timesfm  (paket ``timesfm`` 3.0.1,
             TimesFM 3.0 arayüzü ``timesfm3`` modülünde)
  * ağırlık: https://huggingface.co/google/timesfm-3.0-pytorch

Resmî belgeden doğrulanan kullanım (README, "Code Examples: TimesFM 3.0")::

    from timesfm3 import TimesFM3Evaluator, ModelConfig
    config = ModelConfig(checkpoint_path="google/timesfm-3.0-pytorch",
                         per_core_batch_size=32, device="cuda")
    forecaster = TimesFM3Evaluator(config)
    outputs = list(forecaster.predict_batch([ts], horizon=12, return_quantiles=True))

LİSANS UYARISI (resmî README'den): TimesFM kaynak kodu Apache-2.0'dır ve 2.5'e
kadarki ağırlıklar da Apache-2.0'dır. Ancak **TimesFM 3.0 ön eğitimli
ağırlıkları ayrı bir ``timesfm-non-commercial-license-v1.0`` lisansı altındadır
ve ticari/üretim kullanımına KAPALIDIR.** Bu nedenle TimesFM 3.0 yalnızca
"araştırmada en başarılı model" tarafında değerlendirilebilir; üretimde
kullanılabilecek en başarılı model ayrıca raporlanır.

TimesFM 3 yerine sessizce 2.5 veya başka bir sürüm KULLANILMAZ.
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass

import numpy as np

from .base import BaseModel

HF_MODEL_DEFAULT = "google/timesfm-3.0-pytorch"
WEIGHTS_LICENSE = "timesfm-non-commercial-license-v1.0 (ticari/üretim kullanımı yasak)"
CODE_LICENSE = "Apache-2.0"


@dataclass
class TimesFMStatus:
    available: bool
    detail: str
    package_version: str | None = None
    code_import: str = ""
    weights_ref: str = HF_MODEL_DEFAULT
    weights_revision: str | None = None
    weights_license: str = WEIGHTS_LICENSE
    code_license: str = CODE_LICENSE
    device: str = "cpu"

    def dict(self) -> dict:
        return self.__dict__.copy()


def _pkg_version() -> str | None:
    try:
        import importlib.metadata as md
        return md.version("timesfm")
    except Exception:
        return None


def probe(cfg: dict) -> TimesFMStatus:
    """TimesFM 3'ün bu ortamda gerçekten çalıştırılabilirliğini dener.

    Üç aşama ayrı ayrı raporlanır: paket içe aktarma, ağırlık indirme, model
    kurma. Hangi aşamada takıldığı gizlenmez.
    """
    hf_model = cfg.get("timesfm", {}).get("hf_model", HF_MODEL_DEFAULT)
    version = _pkg_version()

    try:
        mod = importlib.import_module("timesfm3")
        ModelConfig = getattr(mod, "ModelConfig")
        TimesFM3Evaluator = getattr(mod, "TimesFM3Evaluator")
    except Exception as exc:
        return TimesFMStatus(
            False,
            f"TimesFM 3 kodu içe aktarılamadı: {type(exc).__name__}: {exc}",
            version, code_import="başarısız", weights_ref=hf_model)

    # Ağırlıkları indirmeyi dene (asıl engel genellikle burada ortaya çıkar).
    try:
        from huggingface_hub import snapshot_download
        path = snapshot_download(hf_model)
    except Exception as exc:
        return TimesFMStatus(
            False,
            "TimesFM 3 kodu yüklendi (import başarılı) ancak ön eğitimli "
            f"ağırlıklar indirilemedi ({hf_model}): {type(exc).__name__}: {exc}. "
            "Bu ortamda huggingface.co çıkış politikası tarafından "
            "engellenmektedir; TimesFM 3 çalıştırılamamıştır.",
            version, code_import="başarılı", weights_ref=hf_model)

    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        device = "cpu"

    try:
        conf = ModelConfig(checkpoint_path=path, per_core_batch_size=8, device=device)
        TimesFM3Evaluator(conf)
    except Exception as exc:
        return TimesFMStatus(
            False,
            f"Ağırlıklar indirildi ancak model kurulamadı: {type(exc).__name__}: {exc}",
            version, code_import="başarılı", weights_ref=hf_model, device=device)

    return TimesFMStatus(True, "TimesFM 3 kullanılabilir.", version,
                         code_import="başarılı", weights_ref=hf_model, device=device)


class TimesFMZeroShot(BaseModel):
    """Tek değişkenli, İNCE AYARSIZ (zero-shot) TimesFM 3.0.

    Girdi dönüşümü ve bağlam uzunluğu geliştirme doğrulamasında seçilir.
    """

    family, complexity_rank, min_obs = "foundation", 8, 36

    def __init__(self, cfg: dict, context_length: int = 512):
        self.cfg = cfg
        self.context_length = context_length
        self.name = f"TimesFM-3.0(zero-shot,ctx={context_length})"
        self._forecaster = None

    def _load(self):
        if self._forecaster is not None:
            return self._forecaster
        from timesfm3 import TimesFM3Evaluator, ModelConfig
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        conf = ModelConfig(checkpoint_path=self.cfg["timesfm"]["hf_model"],
                           per_core_batch_size=8, device=device)
        self._forecaster = TimesFM3Evaluator(conf)
        return self._forecaster

    def fit(self, z, exog=None):
        # Ön eğitimli model: "eğitim" yerine yalnızca geçmiş bağlam verilir.
        self._ctx = np.asarray(z, dtype=np.float32)[-self.context_length:]
        return self

    def predict(self, h):
        fc = self._load()
        out = list(fc.predict_batch([self._ctx], horizon=h, return_quantiles=False))
        return np.asarray(out[0].forecast, dtype=float).reshape(-1)[:h]

    def predict_quantiles(self, h, levels):
        fc = self._load()
        out = list(fc.predict_batch([self._ctx], horizon=h, return_quantiles=True))
        q = np.asarray(out[0].quantiles, dtype=float)   # (h, 9) -> 0.1 ... 0.9
        grid = np.round(np.arange(1, 10) / 10.0, 2)
        res = {}
        for lv in levels:
            lo_q, hi_q = round((1 - lv) / 2, 2), round(1 - (1 - lv) / 2, 2)
            if lo_q in grid and hi_q in grid:
                res[lv] = (q[:, list(grid).index(lo_q)], q[:, list(grid).index(hi_q)])
        # %95 aralık modelin kuantil ızgarasında yoktur (en dış 0.1/0.9);
        # ek yöntem olmadan %95 aralık ÜRETİLMEZ.
        return res or None
