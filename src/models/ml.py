"""Regresyon ve ağaç tabanlı modeller (doğrudan ufuk / direct-h).

Her ufuk için ayrı model eğitilir. Eğitim örneklerinin hedefi, eğitim kesimine
kadar GERÇEKLEŞMİŞ olmak zorundadır (bkz. features.build_direct_dataset).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..features import build_feature_frame, build_direct_dataset, item_summaries
from .base import BaseModel


class DirectHModel(BaseModel):
    """Ufuk başına bir tahminci eğiten ortak iskelet."""

    family, complexity_rank, min_obs = "ml", 5, 60
    max_h = 12

    def __init__(self, use_items: bool = False, items: pd.DataFrame | None = None):
        self.use_items = use_items
        self.items = items
        self.uses_exog = use_items

    def _make_estimator(self):
        raise NotImplementedError

    def _features(self, z: pd.Series) -> pd.DataFrame:
        feats = build_feature_frame(z)
        if self.use_items and self.items is not None:
            aux = item_summaries(self.items, upto=z.index[-1])
            if aux is not None:
                feats = feats.join(aux, how="left")
                self._aux_cols = list(aux.columns)
            else:
                self._aux_cols = []
        return feats

    def fit(self, z, exog=None):
        self._z = z.astype(float)
        cutoff = z.index[-1]
        feats = self._features(self._z)
        self._x_last = feats.loc[[cutoff]]
        self._models: dict[int, object] = {}
        self._fallback = float(self._z.iloc[-12:].mean())
        for h in range(1, self.max_h + 1):
            X, y = build_direct_dataset(self._z, h, feats, cutoff)
            X = X.dropna(axis=1, how="all")
            keep = X.columns[X.notna().all()]
            X = X[keep]
            if len(X) < 24 or X.shape[1] == 0:
                continue
            est = self._make_estimator()
            est.fit(X.to_numpy(), y.to_numpy())
            self._models[h] = (est, list(keep))
        return self

    def predict(self, h):
        out = np.empty(h, dtype=float)
        for i in range(1, h + 1):
            entry = self._models.get(i)
            if entry is None:
                out[i - 1] = self._fallback
                continue
            est, cols = entry
            x = self._x_last.reindex(columns=cols)
            if x.isna().any().any():
                out[i - 1] = self._fallback
                continue
            out[i - 1] = float(est.predict(x.to_numpy())[0])
        return out


class RidgeDirect(DirectHModel):
    """Ridge regresyon (standartlaştırma eğitim diliminde yapılır)."""
    complexity_rank = 5

    def __init__(self, alpha: float = 1.0, **kw):
        super().__init__(**kw)
        self.alpha = alpha
        self.name = f"Ridge(alpha={alpha}{',sepet' if self.use_items else ''})"

    def _make_estimator(self):
        from sklearn.linear_model import RidgeCV
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        return make_pipeline(StandardScaler(),
                             RidgeCV(alphas=np.logspace(-2, 3, 12)))


class ElasticNetDirect(DirectHModel):
    complexity_rank = 5

    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = f"ElasticNet{'(sepet)' if self.use_items else ''}"

    def _make_estimator(self):
        from sklearn.linear_model import ElasticNetCV
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        return make_pipeline(StandardScaler(),
                             ElasticNetCV(l1_ratio=[0.1, 0.5, 0.9], cv=5,
                                          max_iter=5000, random_state=0))


class LightGBMDirect(DirectHModel):
    """Sığ ve güçlü düzenlileştirilmiş LightGBM."""
    complexity_rank = 6

    def __init__(self, **kw):
        super().__init__(**kw)
        self.name = f"LightGBM(sig{',sepet' if self.use_items else ''})"

    def _make_estimator(self):
        import lightgbm as lgb
        return lgb.LGBMRegressor(
            n_estimators=300, learning_rate=0.03, num_leaves=4, max_depth=3,
            min_child_samples=15, subsample=0.8, subsample_freq=1,
            colsample_bytree=0.6, reg_alpha=1.0, reg_lambda=5.0,
            random_state=0, verbose=-1, n_jobs=1)
