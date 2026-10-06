"""İstatistiksel zaman serisi modelleri (statsmodels tabanlı adaptörler)."""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from .base import BaseModel

warnings.filterwarnings("ignore")


def _to_ts(z: pd.Series) -> pd.Series:
    """PeriodIndex -> aylık DatetimeIndex (statsmodels frekans uyarılarını önler)."""
    s = z.astype(float).copy()
    s.index = s.index.to_timestamp(how="start")
    s = s.asfreq("MS")
    return s


class ETSModel(BaseModel):
    """Üstel düzleştirme (Holt-Winters). Küçük, kayıtlı bir arama uzayı."""
    family, complexity_rank, min_obs = "ets", 2, 36

    def __init__(self, seasonal: bool = True, damped: bool = True):
        self.seasonal, self.damped = seasonal, damped
        self.name = f"ETS(trend=add,damped={damped},seasonal={'add' if seasonal else 'yok'})"

    def fit(self, z, exog=None):
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
        s = _to_ts(z)
        kw = dict(trend="add", damped_trend=self.damped,
                  initialization_method="estimated")
        if self.seasonal and len(s) >= 24:
            kw.update(seasonal="add", seasonal_periods=12)
        self._res = ExponentialSmoothing(s, **kw).fit(optimized=True)
        return self

    def predict(self, h):
        return np.asarray(self._res.forecast(h), dtype=float)


class SarimaSmallGrid(BaseModel):
    """Sınırlı ve KAYITLI SARIMA araması; her başlangıçta AICc ile seçim.

    Arama uzayı bilerek küçük tutulmuştur (yüzlerce gelişigüzel yapılandırma
    denenmez).
    """
    family, complexity_rank, min_obs = "arima", 4, 48

    GRID = [
        ((1, 0, 0), (0, 0, 0, 0)),
        ((0, 0, 1), (0, 0, 0, 0)),
        ((1, 0, 1), (0, 0, 0, 0)),
        ((2, 0, 0), (0, 0, 0, 0)),
        ((1, 0, 0), (1, 0, 0, 12)),
        ((1, 0, 1), (0, 0, 1, 12)),
    ]

    def __init__(self, seasonal: bool = True):
        self.seasonal = seasonal
        self.name = f"SARIMA(kucuk-izgara,seasonal={seasonal})"

    def fit(self, z, exog=None):
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        s = _to_ts(z)
        grid = self.GRID if self.seasonal else [g for g in self.GRID if g[1][3] == 0]
        best, best_ic = None, np.inf
        for order, sorder in grid:
            try:
                res = SARIMAX(s, order=order, seasonal_order=sorder,
                              trend="c", enforce_stationarity=False,
                              enforce_invertibility=False).fit(disp=False, maxiter=100)
                k = res.df_model + 1
                n = len(s)
                aicc = res.aic + (2 * k * (k + 1)) / max(n - k - 1, 1)
                if np.isfinite(aicc) and aicc < best_ic:
                    best, best_ic = res, aicc
                    self.chosen = (order, sorder)
            except Exception:
                continue
        if best is None:
            raise RuntimeError("SARIMA ızgarasında hiçbir yapılandırma uymadı.")
        self._res = best
        return self

    def predict(self, h):
        return np.asarray(self._res.forecast(h), dtype=float)

    def predict_quantiles(self, h, levels):
        try:
            fc = self._res.get_forecast(h)
            out = {}
            for lv in levels:
                ci = fc.conf_int(alpha=1.0 - lv)
                out[lv] = (np.asarray(ci.iloc[:, 0]), np.asarray(ci.iloc[:, 1]))
            return out
        except Exception:
            return None


class AutoTheta(BaseModel):
    """Theta yöntemi (statsmodels ThetaModel), mevsimsellik testi ile."""
    family, complexity_rank, min_obs = "theta", 2, 36

    name = "AutoTheta"

    def fit(self, z, exog=None):
        from statsmodels.tsa.forecasting.theta import ThetaModel
        s = _to_ts(z)
        self._res = ThetaModel(s, period=12, deseasonalize=len(s) >= 36,
                               method="auto").fit()
        return self

    def predict(self, h):
        return np.asarray(self._res.forecast(h), dtype=float)


class LocalLevelTrend(BaseModel):
    """Yerel düzey/trend durum uzayı modeli (isteğe bağlı mevsimsellik)."""
    family, complexity_rank, min_obs = "ucm", 3, 36

    def __init__(self, level: str = "local linear trend", seasonal: bool = True):
        self.level, self.seasonal = level, seasonal
        self.name = f"UCM({level},mevsimsel={seasonal})"

    def fit(self, z, exog=None):
        from statsmodels.tsa.statespace.structural import UnobservedComponents
        s = _to_ts(z)
        kw = dict(level=self.level)
        if self.seasonal and len(s) >= 36:
            kw["seasonal"] = 12
        self._res = UnobservedComponents(s, **kw).fit(disp=False, maxiter=200)
        return self

    def predict(self, h):
        return np.asarray(self._res.forecast(h), dtype=float)

    def predict_quantiles(self, h, levels):
        try:
            fc = self._res.get_forecast(h)
            out = {}
            for lv in levels:
                ci = fc.conf_int(alpha=1.0 - lv)
                out[lv] = (np.asarray(ci.iloc[:, 0]), np.asarray(ci.iloc[:, 1]))
            return out
        except Exception:
            return None
