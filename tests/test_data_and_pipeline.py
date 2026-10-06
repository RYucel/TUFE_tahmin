"""API şeması, sayfalama, kesim ve uçtan uca boru hattı testleri."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src import data as DATA
from src import backtest as BT
from src import forecast as FC
from src.config import load_config
from src.transforms import to_log
from src.models.base import ModelSpec, BaseModel


def test_monthly_from_records_schema_and_sorting():
    rows = [{"year": 2026, "month": 2, "aylikYuzde": 2.0, "yilBasindanYuzde": 3.0,
             "yillikYuzde": 30.0},
            {"year": 2026, "month": 1, "aylikYuzde": 1.0, "yilBasindanYuzde": 1.0,
             "yillikYuzde": 29.0}]
    df = DATA._monthly_from_records(rows)
    assert list(df.index.astype(str)) == ["2026-01", "2026-02"]
    assert list(df.columns) == DATA.MONTH_COLS


def test_monthly_from_records_rejects_missing_fields():
    with pytest.raises(ValueError):
        DATA._monthly_from_records([{"year": 2026, "aylikYuzde": 1.0}])


def test_monthly_from_records_deduplicates():
    rows = [{"year": 2026, "month": 1, "aylikYuzde": 1.0},
            {"year": 2026, "month": 1, "aylikYuzde": 9.0}]
    df = DATA._monthly_from_records(rows)
    assert len(df) == 1 and df["aylikYuzde"].iloc[0] == 9.0   # son kayıt kazanır


def test_api_pagination_consumes_all_pages(monkeypatch, tmp_path):
    """Tek yanıtın bütün seriyi içerdiği VARSAYILMAZ."""
    cfg = load_config()
    cfg["data"]["page_limit"] = 2
    all_rows = [{"year": 2020, "month": m, "aylikYuzde": float(m)} for m in range(1, 8)]
    calls = []

    def fake_get(url, timeout, params=None):
        if "openapi" in url:
            return json.dumps({"paths": {"/api/v1/tufe": {}}}).encode(), 200, ""
        if "meta" in url:
            return json.dumps({"records": 7}).encode(), 200, ""
        off = int(params["offset"])
        lim = int(params["limit"])
        calls.append(off)
        return json.dumps({"data": all_rows[off:off + lim]}).encode(), 200, ""

    monkeypatch.setattr(DATA, "_get", fake_get)
    df, meta, eps, recs = DATA.fetch_api(cfg, tmp_path)
    assert len(df) == 7
    assert calls == [0, 2, 4, 6]
    assert eps == ["/api/v1/tufe"]


def test_api_failure_returns_none(monkeypatch, tmp_path):
    cfg = load_config()
    monkeypatch.setattr(DATA, "_get", lambda *a, **k: (None, None, "ProxyError 403"))
    df, meta, eps, recs = DATA.fetch_api(cfg, tmp_path)
    assert df is None
    assert all(r.status in ("blocked", "error") for r in recs)


def test_cutoff_is_applied():
    cfg = load_config()
    bundle = DATA.get_data(cfg, refresh=False)
    cutoff = pd.Period(cfg["data"]["cutoff"], freq="M")
    assert bundle.monthly.index.max() == cutoff
    if bundle.items is not None:
        assert bundle.items.index.max() <= cutoff


def test_real_data_audit_core_checks():
    cfg = load_config()
    bundle = DATA.get_data(cfg, refresh=False)
    audit = DATA.audit(bundle, cfg)
    must_pass = ["Aylar tekil mi", "Ana seri kesintisiz mi", "Aylık değişim > -%100",
                 "Son ay aylık %", "Son ay YTD %", "Son ay yıllık %"]
    for name in must_pass:
        row = audit[audit["kontrol"] == name].iloc[0]
        assert row["durum"] == "GEÇTİ", f"{name}: {row['ayrinti']}"


# --------------------------------------------------------------------------- #
class ConstModel(BaseModel):
    name, family, min_obs = "sabit", "test", 1

    def __init__(self, v=0.01):
        self.v = v

    def fit(self, z, exog=None):
        return self

    def predict(self, h):
        return np.full(h, self.v)


def _z(n=80, start="2020-01"):
    idx = pd.period_range(start, periods=n, freq="M")
    return pd.Series(to_log(np.full(n, 2.0)), index=idx)


def test_forecast_covers_full_12_months():
    z = _z()
    cutoff = z.index[-1]
    path = np.full(12, np.log(1.02))
    monthly = pd.DataFrame({"yilBasindanYuzde": [10.0]}, index=[cutoff])
    table = FC.build_forecast_table(z, path, cutoff, monthly, "test")
    assert len(table) == 12
    assert list(pd.PeriodIndex(table["tarih"], freq="M")) == [cutoff + i for i in range(1, 13)]
    assert table["aylik_pct"].notna().all()
    assert table[f"kumulatif_{cutoff}_sonrasi_pct"].iloc[-1] == pytest.approx(
        (1.02 ** 12 - 1) * 100)


def test_yearend_uses_official_ytd_start():
    z = _z(start="2026-01", n=8)                 # Oca–Ağu 2026
    cutoff = z.index[-1]
    monthly = pd.DataFrame({"yilBasindanYuzde": [24.0081]}, index=[cutoff])
    path = np.full(12, np.log(1.02))
    summ = FC.period_summaries(z, path, cutoff, monthly)
    ye = summ[summ["olcu"].str.contains("yılsonu")].iloc[0]
    assert ye["deger_pct"] == pytest.approx((1.240081 * 1.02 ** 4 - 1) * 100)


def test_period_summaries_separate_measures():
    z = _z(start="2026-01", n=8)
    cutoff = z.index[-1]
    monthly = pd.DataFrame({"yilBasindanYuzde": [24.0081]}, index=[cutoff])
    summ = FC.period_summaries(z, np.full(12, np.log(1.02)), cutoff, monthly)
    labels = summ["olcu"].tolist()
    assert any("6 ayın BİLEŞİK" in s for s in labels)
    assert any("YILLIK" in s for s in labels)
    assert any("Ocak–Haziran" in s for s in labels)
    # ileri 6 ay bileşiği ile Şubat 2027 yıllık aynı değer OLMAMALI
    c6 = summ[summ["olcu"].str.contains("6 ayın")]["deger_pct"].iloc[0]
    yoy = summ[summ["olcu"].str.contains("YILLIK")]["deger_pct"].iloc[0]
    assert c6 != pytest.approx(yoy)


def test_realized_and_predicted_frames_agree_on_perfect_model():
    z = _z(n=60)
    origins = [z.index[40]]
    paths = pd.DataFrame({"origin": origins * 12, "model": ["p"] * 12,
                          "h": range(1, 13),
                          "z_pred": [z.loc[origins[0] + h] for h in range(1, 13)],
                          "runtime_sec": np.nan})
    actual = BT.realized_frame(z, origins, 12, z.index[-1])
    pred = BT.predicted_frame(z, paths, 12)
    scored = BT.score_frame(pred, actual)
    assert not scored.empty
    assert np.allclose(scored["err"].to_numpy(), 0.0, atol=1e-9)


def test_ensemble_requires_all_members():
    origins = pd.period_range("2020-01", periods=3, freq="M")
    rows = []
    for o in origins:
        for h in range(1, 13):
            rows.append({"origin": o, "model": "A", "h": h, "z_pred": 0.01,
                         "runtime_sec": np.nan})
    for h in range(1, 13):     # B yalnızca ilk başlangıçta var
        rows.append({"origin": origins[0], "model": "B", "h": h, "z_pred": 0.03,
                     "runtime_sec": np.nan})
    ens = BT.ensemble_paths(pd.DataFrame(rows), ["A", "B"], "E", "mean")
    assert set(ens["origin"]) == {origins[0]}
    assert ens["z_pred"].iloc[0] == pytest.approx(0.02)


def test_yearend_only_from_configured_origin_months():
    """Yılsonu hedefi yalnızca Haziran/Ağustos/Ekim sonu başlangıçlarında üretilir."""
    idx = pd.period_range("2020-01", periods=36, freq="M")
    z = pd.Series(to_log(np.full(36, 2.0)), index=idx)
    origins = [p for p in idx if p.year == 2021]
    actual = BT.realized_frame(z, origins, 12, idx[-1], (6, 8, 10))
    ye = actual[actual["target"] == "yearend"]
    assert sorted(pd.PeriodIndex(ye["origin"].astype(str), freq="M").month) == [6, 8, 10]


def test_complete_yearend_years_split():
    rows = []
    for yil, months in ((2020, [6, 8, 10]), (2021, [6, 8])):
        for m in months:
            o = pd.Period(year=yil, month=m, freq="M")
            rows.append({"origin": o, "model": "A", "target": "yearend",
                         "target_end": pd.Period(year=yil, month=12, freq="M"),
                         "pred": 1.0, "actual": 0.0, "err": 1.0})
    rows.append({"origin": pd.Period("2020-06", "M"), "model": "A", "target": "c6",
                 "target_end": pd.Period("2020-12", "M"), "pred": 0.0,
                 "actual": 0.0, "err": 0.0})
    scored = pd.DataFrame(rows)
    tam, kismi = BT.complete_yearend_years(scored, 3)
    assert set(tam["yil"]) == {2020}
    assert set(kismi["yil"]) == {2021}
    sel = BT.scored_for_selection(scored, 3)
    assert len(sel[sel["target"] == "yearend"]) == 3     # yalnızca tam yıl
    assert len(sel[sel["target"] == "c6"]) == 1


def test_horizon_covers_12_and_no_gap():
    """Tahmin çıktısı 12 ayı eksiksiz ve boşluksuz kapsar."""
    z = _z(n=40, start="2023-01")
    cutoff = z.index[-1]
    monthly = pd.DataFrame({"yilBasindanYuzde": [5.0]}, index=[cutoff])
    t = FC.build_forecast_table(z, np.full(12, np.log(1.01)), cutoff, monthly, "m")
    per = pd.PeriodIndex(t["tarih"], freq="M")
    assert len(per) == 12
    assert all((per[i + 1] - per[i]).n == 1 for i in range(11))


# --------------------------------------------------------------------------- #
# TimesFM yardımcı değişkenli varyant — sessiz düşüş regresyon testleri
# --------------------------------------------------------------------------- #
class _SahteForecaster:
    """predict_batch çağrısının aldığı argümanları kaydeden sahte model."""

    def __init__(self):
        self.cagrilar = []

    def predict_batch(self, contexts, horizon, **kw):
        self.cagrilar.append({"contexts": contexts, "horizon": horizon, **kw})

        class _Cikti:
            forecast = np.zeros(horizon)
        return iter([_Cikti()])


def _sepet_ornegi(start="2015-01", n=140, n_item=40):
    idx = pd.period_range(start, periods=n, freq="M")
    rng = np.random.default_rng(3)
    taban = np.exp(np.cumsum(rng.normal(0.02, 0.01, (n, n_item)), axis=0)) * 100
    return pd.DataFrame(taban, index=idx,
                        columns=[f"kalem{i}" for i in range(n_item)])


def test_timesfm_sepet_varyanti_gercekten_kovaryat_gonderir(monkeypatch):
    """Sepet varyantı, past_only_covariates'i GERÇEKTEN göndermeli.

    Regresyon: bağlam 1977'de başlayıp yardımcı seri 2015'te başladığı için
    hizalama başarısız oluyor ve model sessizce düz zero-shot'a düşüyordu; iki
    varyant o zaman ayırt edilemez skorlar üretiyordu.
    """
    from src.models import timesfm_adapter as TFM

    items = _sepet_ornegi()
    z = pd.Series(to_log(np.full(600, 2.0)),
                  index=pd.period_range("1977-03", periods=600, freq="M"))
    cfg = {"timesfm": {"hf_model": "sahte", "device": "cpu"}}

    sahte = _SahteForecaster()
    monkeypatch.setattr(TFM, "load_forecaster", lambda *a, **k: sahte)

    model = TFM.TimesFMWithPastCovariates(cfg, context_length=512, items=items)
    model.fit(z)
    model.predict(12)

    cagri = sahte.cagrilar[-1]
    assert "past_only_covariates" in cagri, "yardımcı değişkenler gönderilmedi"
    cov = cagri["past_only_covariates"][0]
    ctx = cagri["contexts"][0]
    assert cov.ndim == 2 and cov.shape[0] >= 1
    assert cov.shape[1] == len(ctx), "kovaryat uzunluğu bağlamla hizalı değil"
    assert np.isfinite(cov).all()
    # bağlam, sepetin bulunduğu döneme kırpılmış olmalı (512 aya değil)
    assert len(ctx) <= len(items), "bağlam sepet dönemine kırpılmamış"


def test_timesfm_sepet_varyanti_sessizce_dusmez(monkeypatch):
    """Yardımcı değişken kurulamıyorsa HATA vermeli, düz zero-shot'a düşmemeli."""
    from src.models import timesfm_adapter as TFM

    cfg = {"timesfm": {"hf_model": "sahte", "device": "cpu"}}
    z = pd.Series(to_log(np.full(200, 2.0)),
                  index=pd.period_range("1990-01", periods=200, freq="M"))

    with pytest.raises(RuntimeError, match="sepet verisi verilmedi"):
        TFM.TimesFMWithPastCovariates(cfg, 512, items=None).fit(z)

    # sepet özeti üretilemeyecek kadar kısa geçmiş → hata
    cok_kisa = _sepet_ornegi(start="1990-01", n=12, n_item=40)
    with pytest.raises(RuntimeError, match="sepet özetleri üretilemedi"):
        TFM.TimesFMWithPastCovariates(cfg, 512, items=cok_kisa).fit(z)

    # sepet var ama ana seriyle ortak dönem çok kısa → hata
    z_kisa = pd.Series(to_log(np.full(36, 2.0)),
                       index=pd.period_range("2019-01", periods=36, freq="M"))
    items = _sepet_ornegi()          # 2015-01'den itibaren 140 ay
    with pytest.raises(RuntimeError, match="ortak dönemi"):
        TFM.TimesFMWithPastCovariates(cfg, 512, items=items).fit(z_kisa)
