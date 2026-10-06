"""Özellik üretimi.

Sızıntı kuralı: her özellik, tahmin başlangıcı ``t`` itibarıyla BİLİNEN
değerlerden üretilir. Hareketli özetlere hedef veya gelecekteki değerler
girmez; tüm gecikmeler ``t`` ve öncesini kullanır.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

LAGS = [1, 2, 3, 6, 12, 24]
ROLL = [3, 6, 12]


def build_feature_frame(z: pd.Series) -> pd.DataFrame:
    """Her ay ``t`` için, o ay dahil bilinen bilgiden türetilen özellikler.

    Satır ``t``'deki değerler yalnızca ``z[<= t]`` kullanır. Bu çerçeve, ``t``
    başlangıcından yapılan tahminlerde girdi olarak kullanılabilir.
    """
    z = z.astype(float)
    df = pd.DataFrame(index=z.index)
    for lag in LAGS:
        df[f"lag{lag}"] = z.shift(lag - 1)  # lag1 = z_t (başlangıçta bilinen son ay)
    for w in ROLL:
        df[f"ma{w}"] = z.rolling(w).mean()
        df[f"sd{w}"] = z.rolling(w).std()
    df["comp12"] = z.rolling(12).sum()      # son 12 ayın log toplamı
    month = pd.Series(z.index.month, index=z.index)
    df["ay_sin"] = np.sin(2 * np.pi * month / 12.0)
    df["ay_cos"] = np.cos(2 * np.pi * month / 12.0)
    for m in range(1, 13):
        df[f"ay_{m:02d}"] = (month == m).astype(float)
    return df


def build_direct_dataset(z: pd.Series, h: int, feats: pd.DataFrame,
                         cutoff: pd.Period) -> tuple[pd.DataFrame, pd.Series]:
    """Doğrudan ufuk (direct-h) eğitim kümesi.

    Her eğitim örneğinin hedefi ``t+h`` ayıdır ve YALNIZCA ``t+h <= cutoff``
    olduğunda kullanılır — yani eğitim kesimine kadar gerçekleşmiş olmalıdır.
    """
    y = z.shift(-h)
    valid = feats.dropna().index
    idx = [t for t in valid if (t + h) in z.index and (t + h) <= cutoff and t <= cutoff]
    if not idx:
        return feats.iloc[0:0], pd.Series(dtype=float)
    idx = pd.PeriodIndex(idx, freq="M")
    return feats.loc[idx], y.loc[idx]


# --------------------------------------------------------------------------- #
# sepet (madde fiyatları) yardımcı özetleri
# --------------------------------------------------------------------------- #
def item_summaries(items: pd.DataFrame, upto: pd.Period, n_factors: int = 3,
                   min_coverage: float = 0.9) -> pd.DataFrame | None:
    """Sepet madde fiyatlarından SINIRLI sayıda özet/faktör üretir.

    520+ kalem doğrudan modele verilmez. Kalem seçimi, doldurma, ölçekleme ve
    faktör çıkarımı YALNIZCA ``upto`` ayına kadarki eğitim geçmişinde yapılır;
    her eğitim diliminde yeniden hesaplanır.

    Not: geçerli tarihsel sepet ağırlıkları bulunmadığından bu özetler resmî
    TÜFE tahmini olarak sunulmaz; yalnızca yardımcı bilgi olarak kullanılır.
    """
    if items is None:
        return None
    hist = items[items.index <= upto]
    if len(hist) < 24:
        return None
    cov = hist.notna().mean()
    cols = cov[cov >= min_coverage].index
    if len(cols) < 20:
        return None
    px = hist[cols].astype(float)
    # sıfır fiyat "fiyatlanmadı" demektir; log dönüşümü için eksik sayılır
    px = px.replace(0.0, np.nan)
    px = px.ffill()                       # yalnızca eğitim geçmişi içinde
    px = px.dropna(axis=1, how="any")
    if px.shape[1] < 20:
        return None
    dl = np.log(px).diff().iloc[1:]       # kalem bazında log fiyat değişimi
    dl = dl.replace([np.inf, -np.inf], np.nan).dropna(axis=1, how="any")
    if dl.shape[1] < 20 or len(dl) < 18:
        return None

    out = pd.DataFrame(index=dl.index)
    out["sepet_ortalama"] = dl.mean(axis=1)
    out["sepet_medyan"] = dl.median(axis=1)
    out["sepet_yayilim"] = dl.std(axis=1)
    out["sepet_artan_pay"] = (dl > 0).mean(axis=1)
    out["sepet_kirpilmis_ort"] = dl.apply(
        lambda row: row[(row >= row.quantile(0.1)) & (row <= row.quantile(0.9))].mean(),
        axis=1)

    # faktörler: eğitim diliminde ölçekleme + PCA
    mu, sd = dl.mean(), dl.std().replace(0, np.nan)
    zz = ((dl - mu) / sd).dropna(axis=1, how="any")
    if zz.shape[1] >= 20:
        from sklearn.decomposition import PCA
        k = min(n_factors, zz.shape[1], max(len(zz) - 1, 1))
        pca = PCA(n_components=k, random_state=0)
        f = pca.fit_transform(zz.to_numpy())
        for i in range(k):
            out[f"sepet_faktor{i+1}"] = f[:, i]
    return out
