"""Ortak model arayüzü.

Her model, aylık log değişim serisi ``z`` (pandas Series, PeriodIndex[M]) ile
eğitilir ve ``predict(h)`` çağrısında gelecek ``h`` ayın LOG DEĞİŞİM
tahminlerini döndürür. İsteğe bağlı ``exog`` yardımcı değişken çerçevesidir ve
yalnızca tahmin başlangıcına kadar bilinen değerleri içerir.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


class BaseModel:
    """Tüm adayların uyduğu adaptör arayüzü."""

    name: str = "base"
    family: str = "base"
    complexity_rank: int = 99      # küçük = daha basit (yapılandırmada önceden tanımlı)
    uses_exog: bool = False
    min_obs: int = 13

    def fit(self, z: pd.Series, exog: pd.DataFrame | None = None) -> "BaseModel":
        raise NotImplementedError

    def predict(self, h: int) -> np.ndarray:
        """Gelecek h ayın log değişim tahminleri (uzunluk h)."""
        raise NotImplementedError

    # isteğe bağlı: modelin kendi kuantilleri
    def predict_quantiles(self, h: int, levels: list[float]) -> dict[float, np.ndarray] | None:
        return None

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} {self.name}>"


@dataclass
class ModelSpec:
    """Bir aday yapılandırması: model + eğitim penceresi + dönüşüm."""

    key: str
    factory: Any                    # () -> BaseModel
    family: str
    window: int                     # 0 = erişilebilir tüm geçmiş
    transform: str = "log"          # "log" | "pct"
    complexity_rank: int = 99
    uses_exog: bool = False
    min_history: int = 24
    meta: dict = field(default_factory=dict)

    def build(self) -> BaseModel:
        return self.factory()


def slice_window(z: pd.Series, window: int) -> pd.Series:
    """Eğitim penceresini uygular. window=0 ise tüm erişilebilir geçmiş."""
    if window and window > 0 and len(z) > window:
        return z.iloc[-window:]
    return z
