"""Veri alma, önbellekleme ve kalite denetimi.

Birincil kaynak KKTC TÜFE API'sidir. API'ye ulaşılamadığında (ağ/egress
politikası) API'nin kendi beslendiği yukarı akış veri deposu kullanılır ve bu
durum manifest'e ve denetim tablosuna açıkça yazılır. Kaynak sessizce
değiştirilmez.
"""
from __future__ import annotations

import hashlib
import io
import json
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

MONTH_COLS = ["aylikYuzde", "yilBasindanYuzde", "yillikYuzde"]


# --------------------------------------------------------------------------- #
# yardımcılar
# --------------------------------------------------------------------------- #
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def to_period(year: int, month: int) -> pd.Period:
    return pd.Period(year=int(year), month=int(month), freq="M")


@dataclass
class SourceRecord:
    """Tek bir indirmenin kökeni."""

    name: str
    url: str
    status: str                # "ok" | "blocked" | "error"
    http_code: int | None = None
    fetched_at: str = ""
    sha256: str = ""
    n_bytes: int = 0
    cache_path: str = ""
    detail: str = ""

    def dict(self) -> dict:
        return asdict(self)


@dataclass
class DataBundle:
    monthly: pd.DataFrame            # index: PeriodIndex[M], MONTH_COLS
    items: pd.DataFrame | None       # index: PeriodIndex[M], sütunlar = sepet kalemleri
    sources: list[SourceRecord] = field(default_factory=list)
    api_meta: dict | None = None
    api_openapi_endpoints: list[str] = field(default_factory=list)
    cutoff: str = ""
    provenance: str = ""             # "api" | "upstream"


# --------------------------------------------------------------------------- #
# indirme
# --------------------------------------------------------------------------- #
def _get(url: str, timeout: int, params: dict | None = None) -> tuple[bytes | None, int | None, str]:
    try:
        resp = requests.get(url, timeout=timeout, params=params)
        return resp.content, resp.status_code, ""
    except Exception as exc:  # ağ/egress hataları dahil
        return None, None, f"{type(exc).__name__}: {exc}"


def _cache_write(raw_dir: Path, fname: str, content: bytes) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / fname
    path.write_bytes(content)
    return path


def _record(name: str, url: str, content: bytes | None, code: int | None,
            err: str, raw_dir: Path, fname: str) -> SourceRecord:
    now = datetime.now(timezone.utc).isoformat()
    if content is not None and code == 200:
        path = _cache_write(raw_dir, fname, content)
        return SourceRecord(name, url, "ok", code, now, sha256_bytes(content),
                            len(content), str(path))
    status = "blocked" if (code in (401, 403, 405, 407) or err) else "error"
    return SourceRecord(name, url, status, code, now, "", 0, "",
                        err or f"HTTP {code}")


def fetch_api(cfg: dict, raw_dir: Path) -> tuple[pd.DataFrame | None, dict | None,
                                                 list[str], list[SourceRecord]]:
    """API'den ana seriyi sayfalama ile çeker. Başarısızsa (None, ...) döner."""
    base = cfg["data"]["api_base"].rstrip("/")
    eps = cfg["data"]["endpoints"]
    timeout = cfg["data"]["timeout_sec"]
    recs: list[SourceRecord] = []

    # 1) OpenAPI — uç nokta adlarını varsaymak yerine doğrula
    content, code, err = _get(base + eps["openapi"], timeout)
    rec = _record("openapi", base + eps["openapi"], content, code, err, raw_dir, "openapi.json")
    recs.append(rec)
    endpoints: list[str] = []
    if rec.status == "ok":
        try:
            endpoints = sorted(json.loads(content.decode("utf-8")).get("paths", {}).keys())
        except Exception as exc:
            rec.detail = f"openapi parse: {exc}"

    # 2) meta
    content, code, err = _get(base + eps["meta"], timeout)
    rec_meta = _record("meta", base + eps["meta"], content, code, err, raw_dir, "meta.json")
    recs.append(rec_meta)
    api_meta = None
    if rec_meta.status == "ok":
        try:
            api_meta = json.loads(content.decode("utf-8"))
        except Exception as exc:
            rec_meta.detail = f"meta parse: {exc}"

    # 3) tufe — sayfalamayı varsayma, offset/limit ile tüket
    limit = int(cfg["data"]["page_limit"])
    rows: list[dict] = []
    offset = 0
    ok = False
    while True:
        url = base + eps["tufe"]
        content, code, err = _get(url, timeout, params={"limit": limit, "offset": offset,
                                                        "sort": "asc"})
        page_rec = _record(f"tufe[offset={offset}]", url, content, code, err, raw_dir,
                           f"tufe_{offset}.json")
        recs.append(page_rec)
        if page_rec.status != "ok":
            break
        try:
            payload = json.loads(content.decode("utf-8"))
        except Exception as exc:
            page_rec.status = "error"
            page_rec.detail = f"json parse: {exc}"
            break
        chunk = payload.get("data", payload) if isinstance(payload, dict) else payload
        if not isinstance(chunk, list) or not chunk:
            ok = bool(rows)
            break
        rows.extend(chunk)
        ok = True
        if len(chunk) < limit:
            break
        offset += len(chunk)
        if offset > 20000:  # güvenlik freni
            break

    if not ok or not rows:
        return None, api_meta, endpoints, recs

    df = _monthly_from_records(rows)
    return df, api_meta, endpoints, recs


def fetch_upstream(cfg: dict, raw_dir: Path) -> tuple[pd.DataFrame | None, pd.DataFrame | None,
                                                      list[SourceRecord]]:
    """API'nin beslendiği yukarı akış deposundan aynı veriyi çeker."""
    timeout = cfg["data"]["timeout_sec"]
    recs: list[SourceRecord] = []

    url = cfg["data"]["upstream_monthly_url"]
    content, code, err = _get(url, timeout)
    rec = _record("upstream_monthly", url, content, code, err, raw_dir, "tufe_upstream.json")
    recs.append(rec)
    monthly = None
    if rec.status == "ok":
        monthly = _monthly_from_records(json.loads(content.decode("utf-8")))

    url = cfg["data"]["upstream_items_url"]
    content, code, err = _get(url, timeout)
    rec = _record("upstream_items", url, content, code, err, raw_dir, "GRETL_TUFE.csv")
    recs.append(rec)
    items = None
    if rec.status == "ok":
        items = _items_from_csv(content)

    return monthly, items, recs


def _monthly_from_records(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    missing = {"year", "month", "aylikYuzde"} - set(df.columns)
    if missing:
        raise ValueError(f"Ana seride beklenen alanlar eksik: {sorted(missing)}")
    for col in MONTH_COLS:
        if col not in df.columns:
            df[col] = np.nan
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["period"] = [to_period(y, m) for y, m in zip(df["year"], df["month"])]
    df = df.drop_duplicates(subset="period", keep="last").sort_values("period")
    df = df.set_index(pd.PeriodIndex(df["period"], freq="M"))[MONTH_COLS]
    df.index.name = "period"
    return df


def _items_from_csv(content: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")
    date_col = df.columns[0]
    dates = pd.to_datetime(df[date_col], format="%d/%m/%Y", errors="coerce")
    if dates.isna().any():
        dates = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
    df = df.drop(columns=[date_col])
    # tamamen boş sütunları at (CSV sonundaki ayraç artıkları)
    df = df.loc[:, [c for c in df.columns if not str(c).startswith("Unnamed")]]
    df = df.apply(pd.to_numeric, errors="coerce")
    df.index = pd.PeriodIndex(dates, freq="M")
    df.index.name = "period"
    return df.sort_index()


# --------------------------------------------------------------------------- #
# ana giriş noktası
# --------------------------------------------------------------------------- #
def get_data(cfg: dict, refresh: bool = False) -> DataBundle:
    """Ham veriyi indirir (veya önbellekten okur) ve kesim uygular."""
    root = Path(cfg["_root"])
    raw_dir = root / cfg["data"]["raw_dir"]
    cutoff = pd.Period(cfg["data"]["cutoff"], freq="M")
    bundle_path = raw_dir / "bundle_meta.json"

    cached_ok = (not refresh and bundle_path.exists()
                 and (raw_dir / "monthly.parquet").exists())
    if cached_ok:
        meta = json.loads(bundle_path.read_text(encoding="utf-8"))
        monthly = pd.read_parquet(raw_dir / "monthly.parquet")
        monthly.index = pd.PeriodIndex(monthly.index, freq="M")
        items = None
        if (raw_dir / "items.parquet").exists():
            items = pd.read_parquet(raw_dir / "items.parquet")
            items.index = pd.PeriodIndex(items.index, freq="M")
        srcs = [SourceRecord(**s) for s in meta["sources"]]
        return DataBundle(monthly, items, srcs, meta.get("api_meta"),
                          meta.get("api_openapi_endpoints", []), meta["cutoff"],
                          meta["provenance"])

    sources: list[SourceRecord] = []
    monthly, api_meta, endpoints, api_recs = fetch_api(cfg, raw_dir)
    sources += api_recs
    provenance = "api"
    items = None

    if monthly is None:
        provenance = "upstream"
        up_monthly, up_items, up_recs = fetch_upstream(cfg, raw_dir)
        sources += up_recs
        monthly, items = up_monthly, up_items
    else:
        # sepet fiyatları API'de ayrı uç noktada olabilir; OpenAPI'de yoksa
        # yukarı akıştan alınır (aynı dosya, API'nin kendi kaynağı).
        _, up_items, up_recs = fetch_upstream(cfg, raw_dir)
        sources += [r for r in up_recs if r.name == "upstream_items"]
        items = up_items

    if monthly is None:
        raise RuntimeError(
            "Ana TÜFE serisi ne API'den ne de yukarı akış deposundan alınabildi. "
            "Kaynak kayıtları: " + json.dumps([s.dict() for s in sources], ensure_ascii=False)
        )

    monthly = monthly[monthly.index <= cutoff]
    if items is not None:
        items = items[items.index <= cutoff]

    raw_dir.mkdir(parents=True, exist_ok=True)
    monthly.to_parquet(raw_dir / "monthly.parquet")
    if items is not None:
        items.to_parquet(raw_dir / "items.parquet")
    bundle_path.write_text(json.dumps({
        "sources": [s.dict() for s in sources],
        "api_meta": api_meta,
        "api_openapi_endpoints": endpoints,
        "cutoff": str(cutoff),
        "provenance": provenance,
        "written_at": datetime.now(timezone.utc).isoformat(),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    return DataBundle(monthly, items, sources, api_meta, endpoints, str(cutoff), provenance)


# --------------------------------------------------------------------------- #
# kalite denetimi
# --------------------------------------------------------------------------- #
def audit(bundle: DataBundle, cfg: dict) -> pd.DataFrame:
    """Veri kalite kontrolleri. Hiçbir kontrol veriyi sessizce düzeltmez."""
    from .transforms import to_log, compound_pct

    tol = cfg["data"]["tolerance"]
    exp = cfg["data"]["expected"]
    m = bundle.monthly
    checks: list[dict] = []

    def add(name: str, status: str, detail: str, value: Any = "") -> None:
        checks.append({"kontrol": name, "durum": status, "ayrinti": detail,
                       "deger": value})

    add("Veri kökeni", "BİLGİ",
        {"api": "Birincil API kullanıldı",
         "upstream": "API'ye ulaşılamadı; API'nin beslendiği yukarı akış deposu kullanıldı"}
        [bundle.provenance], bundle.provenance)

    for s in bundle.sources:
        if s.status != "ok":
            add(f"Kaynak erişimi: {s.name}", "ENGEL", f"{s.detail}", s.url)

    # 1. tekillik ve sıralılık
    add("Aylar tekil mi", "GEÇTİ" if m.index.is_unique else "KALDI",
        f"{m.index.duplicated().sum()} yinelenen ay", int(m.index.duplicated().sum()))
    add("Aylar sıralı mı", "GEÇTİ" if m.index.is_monotonic_increasing else "KALDI", "", "")

    # 2. kesintisizlik
    full = pd.period_range(m.index.min(), m.index.max(), freq="M")
    gaps = full.difference(m.index)
    add("Ana seri kesintisiz mi", "GEÇTİ" if len(gaps) == 0 else "KALDI",
        "Eksik ay yok" if len(gaps) == 0 else
        f"EKSİK AYLAR: {[str(g) for g in gaps[:24]]} — otomatik doldurma YAPILMADI",
        len(gaps))

    # 3. eksik / sayısal olmayan
    n_bad = int(m["aylikYuzde"].isna().sum())
    add("Aylık değişimde eksik/sayısal olmayan", "GEÇTİ" if n_bad == 0 else "KALDI",
        f"{n_bad} kayıt", n_bad)

    # 4. -%100 ve altı
    n_neg = int((m["aylikYuzde"] <= -100).sum())
    add("Aylık değişim > -%100", "GEÇTİ" if n_neg == 0 else "KALDI",
        f"{n_neg} kayıt log dönüşümü için geçersiz", n_neg)

    # 5. resmî YTD / yıllık ile hesaplananın karşılaştırması
    z = to_log(m["aylikYuzde"])
    calc_yoy = pd.Series(index=m.index, dtype=float)
    for i in range(11, len(z)):
        calc_yoy.iloc[i] = compound_pct(z.iloc[i - 11:i + 1].to_numpy())
    calc_ytd = pd.Series(index=m.index, dtype=float)
    for per in m.index:
        dec = pd.Period(year=per.year - 1, month=12, freq="M")
        if dec in m.index or per.month == 1:
            start = pd.Period(year=per.year, month=1, freq="M")
            seg = z[(z.index >= start) & (z.index <= per)]
            if len(seg) == per.month:
                calc_ytd[per] = compound_pct(seg.to_numpy())

    for label, calc, off in (("Yıllık", calc_yoy, m["yillikYuzde"]),
                             ("YTD", calc_ytd, m["yilBasindanYuzde"])):
        both = pd.concat([calc, off], axis=1).dropna()
        if both.empty:
            add(f"{label} oran tutarlılığı", "BİLGİ", "Karşılaştırılabilir kayıt yok", 0)
            continue
        diff = (both.iloc[:, 0] - both.iloc[:, 1]).abs()
        n_round = int((diff <= tol["rounding_pp"]).sum())
        n_material = int((diff > tol["material_pp"]).sum())
        worst = both.index[diff.argmax()]
        status = "GEÇTİ" if n_material == 0 else "UYARI"
        add(f"{label} oran tutarlılığı", status,
            f"{len(both)} kayıt; {n_round} tanesi yuvarlama toleransı içinde "
            f"(<= {tol['rounding_pp']} pp); {n_material} tanesi maddi fark "
            f"(> {tol['material_pp']} pp); en büyük fark {diff.max():.4f} pp @ {worst}. "
            "Farklar düzeltilmedi, olduğu gibi raporlandı.",
            round(float(diff.max()), 4))

    # 6. başlangıç kontrolleri (plan aşamasında doğrulanan değerler)
    add("Kayıt sayısı", "GEÇTİ" if len(m) == exp["n_monthly"] else "UYARI",
        f"beklenen {exp['n_monthly']}, bulunan {len(m)}", len(m))
    add("Seri başlangıcı", "GEÇTİ" if str(m.index.min()) == exp["first"] else "UYARI",
        f"beklenen {exp['first']}, bulunan {m.index.min()}", str(m.index.min()))
    add("Seri sonu (kesim)", "GEÇTİ" if str(m.index.max()) == exp["last"] else "UYARI",
        f"beklenen {exp['last']}, bulunan {m.index.max()}", str(m.index.max()))
    last = m.iloc[-1]
    for key, col, label in (("last_aylik", "aylikYuzde", "Son ay aylık %"),
                            ("last_ytd", "yilBasindanYuzde", "Son ay YTD %"),
                            ("last_yillik", "yillikYuzde", "Son ay yıllık %")):
        got = float(last[col])
        okk = abs(got - exp[key]) <= tol["rounding_pp"]
        add(label, "GEÇTİ" if okk else "UYARI",
            f"beklenen {exp[key]}, bulunan {got}", got)

    # 7. sepet fiyatları
    if bundle.items is None:
        add("Sepet madde fiyatları", "ENGEL", "Kaynak alınamadı", "")
    else:
        it = bundle.items
        add("Sepet kapsamı", "BİLGİ",
            f"{it.shape[1]} kalem × {it.shape[0]} ay ({it.index.min()}–{it.index.max()})",
            f"{it.shape[1]}x{it.shape[0]}")
        okk = (str(it.index.min()) == exp["items_first"]
               and str(it.index.max()) == exp["items_last"]
               and it.shape[0] == exp["items_n_months"])
        add("Sepet dönem kontrolü", "GEÇTİ" if okk else "UYARI",
            f"beklenen {exp['items_first']}–{exp['items_last']} / {exp['items_n_months']} ay",
            f"{it.index.min()}–{it.index.max()} / {it.shape[0]}")
        n_missing = int(it.isna().sum().sum())
        n_zero = int((it == 0).sum().sum())
        add("Sepet eksik değer", "GEÇTİ" if n_missing == 0 else "UYARI",
            f"{n_missing} boş hücre ({100*n_missing/it.size:.3f}%)", n_missing)
        add("Sepet sıfır değer", "GEÇTİ" if n_zero == 0 else "UYARI",
            f"{n_zero} sıfır hücre", n_zero)
        allnan = [c for c in it.columns if it[c].isna().all()]
        add("Tamamen boş kalem", "GEÇTİ" if not allnan else "UYARI",
            f"{len(allnan)} kalem", len(allnan))
        # kesinti / tanım değişikliği izi: uzun boşluktan sonra yeniden başlayan seriler
        breaks = []
        for c in it.columns:
            s = it[c]
            valid = s.notna().to_numpy()
            if valid.any():
                first, last_i = valid.argmax(), len(valid) - 1 - valid[::-1].argmax()
                if (~valid[first:last_i + 1]).sum() > 0:
                    breaks.append(c)
        add("Sepet iç kesinti (seri ortasında boşluk)",
            "GEÇTİ" if not breaks else "UYARI",
            f"{len(breaks)} kalemde seri ortasında boşluk var", len(breaks))

    # 8. olağandışı aylar — SİLİNMEZ, yalnızca raporlanır
    r = m["aylikYuzde"].dropna()
    hi = r[r > r.quantile(0.999)]
    add("Olağandışı aylar", "BİLGİ",
        "Şok ayları tahmin probleminin parçasıdır; silinmedi/kırpılmadı. "
        f"En yüksek 3 ay: {', '.join(f'{p}: %{v:.2f}' for p, v in r.nlargest(3).items())}",
        round(float(r.max()), 4))

    # 9. revizyon geçmişi
    add("Veri revizyon geçmişi", "BİLGİ",
        "Geçmiş veri sürümleri (vintage) mevcut değil. Değerlendirme "
        "'son veri sürümüyle geriye dönük test' olarak adlandırılmalıdır; "
        "revizyon olmadığı varsayılmamaktadır.", "yok")

    return pd.DataFrame(checks)
