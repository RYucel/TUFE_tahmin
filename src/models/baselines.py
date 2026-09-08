"""Zorunlu referans (benchmark) modeller."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .base import BaseModel


class LastValue(BaseModel):
    """Son aylık değerin devamı (naive)."""
    name, family, complexity_rank, min_obs = "naive_son_ay", "baseline", 0, 1

    def fit(self, z, exog=None):
        self._v = float(z.iloc[-1])
        return self

    def predict(self, h):
        return np.full(h, self._v)


class SeasonalNaive(BaseModel):
    """Geçen yılın aynı ayı (mevsimsel naive, m=12)."""
    name, family, complexity_rank, min_obs = "naive_mevsimsel_12", "baseline", 0, 12

    def fit(self, z, exog=None):
        self._last12 = z.iloc[-12:].to_numpy(dtype=float)
        return self

    def predict(self, h):
        return np.array([self._last12[i % 12] for i in range(h)], dtype=float)


class RollingMean(BaseModel):
    """Son k ayın ortalama log değişimi."""
    family, complexity_rank = "baseline", 0

    def __init__(self, k: int):
        self.k = k
        self.name = f"ortalama_{k}ay"
        self.min_obs = k

    def fit(self, z, exog=None):
        self._v = float(z.iloc[-self.k:].mean())
        return self

    def predict(self, h):
        return np.full(h, self._v)
