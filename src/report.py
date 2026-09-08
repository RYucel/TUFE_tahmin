"""Türkçe HTML ve Markdown rapor üretimi + CSV/Excel tablo paketleri."""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .config import out_dir

CSS = """
body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
 max-width:1180px;margin:0 auto;padding:28px 20px 80px;line-height:1.62;color:#1a1a1a}
h1{font-size:1.9rem;border-bottom:3px solid #1b3a6b;padding-bottom:10px}
h2{font-size:1.35rem;margin-top:2.2em;color:#1b3a6b;border-bottom:1px solid #dcdcdc;padding-bottom:5px}
h3{font-size:1.08rem;margin-top:1.6em;color:#333}
table{border-collapse:collapse;width:100%;margin:1em 0;font-size:.86rem}
th,td{border:1px solid #d8d8d8;padding:6px 9px;text-align:right}
th{background:#eef2f7;text-align:center;font-weight:600}
td:first-child,th:first-child{text-align:left}
tr:nth-child(even) td{background:#fafbfc}
.kutu{background:#f4f7fb;border-left:4px solid #1b3a6b;padding:12px 16px;margin:1.2em 0;border-radius:0 4px 4px 0}
.uyari{background:#fff6e8;border-left:4px solid #c1440e}
.engel{background:#fdecea;border-left:4px solid #b3261e}
.iyi{background:#eef7ee;border-left:4px solid #2e7d32}
figure{margin:1.6em 0}img{max-width:100%;border:1px solid #e2e2e2;border-radius:4px}
figcaption{font-size:.83rem;color:#555;margin-top:6px}
code{background:#f2f2f2;padding:1px 5px;border-radius:3px;font-size:.88em}
.kucuk{font-size:.83rem;color:#555}
"""


MAIN_TARGETS_VIEW = ["yearend", "c6", "c12", "m1", "m3", "m6", "m12"]
FULL_NOTE = ('<p class="kucuk">Okunabilirlik için ana hedefler ve seçilmiş aylık '
             'ufuklar gösterilmiştir; tüm hedefler (m1–m12, yoy1–yoy12) ilgili '
             'CSV dosyasındadır.</p>')


def _view(df, col="hedef"):
    return df[df[col].isin(MAIN_TARGETS_VIEW)] if df is not None and col in df else df


def _fmt(df: pd.DataFrame, floats: int = 3) -> str:
    d = df.copy()
    for c in d.columns:
        if pd.api.types.is_float_dtype(d[c]):
            d[c] = d[c].map(lambda v: "" if pd.isna(v) else f"{v:,.{floats}f}".replace(",", " "))
    return d.to_html(index=False, escape=True, border=0)


def _t(cfg, name: str) -> pd.DataFrame | None:
    p = out_dir(cfg, "tables") / name
    if not p.exists():
        return None
    try:
        return pd.read_csv(p)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _j(cfg, *parts) -> dict | None:
    p = out_dir(cfg, *parts[:-1]) / parts[-1]
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _fig_block(cfg, name: str, caption: str) -> str:
    png = out_dir(cfg, "figures") / f"{name}.png"
    if not png.exists():
        return ""
    rel = f"figures/{name}.png"
    svg = f' · <a href="figures/{name}.svg">SVG</a>' if (out_dir(cfg, "figures") / f"{name}.svg").exists() else ""
    return (f'<figure><img src="{rel}" alt="{html.escape(caption)}">'
            f'<figcaption>{html.escape(caption)}{svg}</figcaption></figure>')


def build(cfg: dict) -> list[Path]:
    adir = out_dir(cfg)
    cutoff = cfg["data"]["cutoff"]
    now = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")

    audit = _t(cfg, "01_veri_denetimi.csv")
    kapsam = _t(cfg, "01_veri_kapsami.csv")
    cfgs = _t(cfg, "02_aday_yapilandirmalar.csv")
    dev_rank = _t(cfg, "03b_gelistirme_siralamasi.csv")
    dev_sum = _t(cfg, "03a_gelistirme_ozet.csv")
    sub_rank = _t(cfg, "03c_alt_donem_siralamasi.csv")
    test_sum = _t(cfg, "03d_nihai_test_ozet.csv")
    ye_tbl = _t(cfg, "05_yilsonu_tahminleri.csv")
    fc_tbl = _t(cfg, "06_aylik_tahminler.csv")
    per_tbl = _t(cfg, "07_donem_ozetleri.csv")
    iv_tbl = _t(cfg, "07b_nihai_tahmin_araliklari.csv")
    comp_tbl = _t(cfg, "08_model_karsilastirmasi.csv")
    cov_tbl = _t(cfg, "09_aralik_kapsamasi.csv")
    fail_dev = _t(cfg, "10_basarisiz_denemeler_dev.csv")
    fail_test = _t(cfg, "10_basarisiz_denemeler_test.csv")
    horizon_tbl = _t(cfg, "04_ufuk_bazli_hatalar.csv")
    boot_tbl = _t(cfg, "11_bootstrap_karsilastirma.csv")

    frozen = _j(cfg, "selection", "frozen_selection.json")
    man_data = _j(cfg, "manifest_data.json")
    man_bt = _j(cfg, "manifest_backtest.json")
    man_ev = _j(cfg, "manifest_evaluate.json")
    man_fc = _j(cfg, "manifest_forecast.json")

    tfm = (man_data or {}).get("timesfm_durumu", {})
    prov = None
    for row in (audit.itertuples() if audit is not None else []):
        if row.kontrol == "Veri kökeni":
            prov = row.ayrinti
    w = cfg["selection"]["weights"]

    S: list[str] = []
    A = S.append

    A(f"<h1>KKTC TÜFE Tahmin Sistemi — Değerlendirme ve Tahmin Raporu</h1>")
    A(f'<p class="kucuk">Veri kesimi: <b>{cutoff}</b> · Tahmin dönemi: '
      f'<b>{man_fc["tahmin_donemi"] if man_fc else "—"}</b> · Rapor: {now}</p>')

    # ---------------- yönetici özeti ----------------
    A("<h2>1. Yönetici özeti</h2>")
    if frozen:
        kz = frozen["frozen_extra"]["kazanan_yapilandirma"]
        A(f'<div class="kutu iyi"><b>Seçilen model:</b> <code>{html.escape(frozen["winner"])}</code>'
          f' — aile: {html.escape(str(kz["aile"]))}, eğitim penceresi: '
          f'{html.escape(str(kz["pencere"]))}, dönüşüm: {html.escape(str(kz["donusum"]))}.<br>'
          f'<b>Geliştirme seçim skoru S = {frozen["score"]:.4f}</b> yüzde puan '
          f'(S = {w["yearend"]:.2f}·MAE<sub>yılsonu</sub> + {w["c6"]:.2f}·MAE<sub>6ay</sub> '
          f'+ {w["c12"]:.2f}·MAE<sub>12ay</sub>).<br>'
          f'<b>Seçim kuralı:</b> {html.escape(frozen["rule"])}<br>'
          f'<span class="kucuk">Donduruldu: {frozen["frozen_at"]} — '
          f'nihai holdout bu aşamada kullanılmamıştır.</span></div>')
    if per_tbl is not None:
        A("<p>Veri kesiminden sonraki ana tahminler:</p>")
        A(_fmt(per_tbl[["olcu", "donem", "deger_pct", "tanim"]].rename(
            columns={"olcu": "Ölçü", "donem": "Dönem", "deger_pct": "Tahmin (%)",
                     "tanim": "Tanım"}), 2))
    A('<div class="kutu"><b>Ölçülerin ayrımı.</b> “Gelecek 6 ayın bileşik enflasyonu”, '
      '“6 ay sonra yıllık enflasyon” ve “takvim yarıyılı enflasyonu” birbirinden '
      'FARKLI büyüklüklerdir ve bu raporda ayrı satırlarda verilmiştir. '
      f'{cutoff} sonrasından bakıldığında yılsonu hedefi 4 ay sonrasıdır.</div>')

    # ---------------- engeller ----------------
    A("<h2>2. Tamamlanmamış / engellenen bileşenler</h2>")
    if tfm and not tfm.get("available"):
        A(f'<div class="kutu engel"><b>TimesFM 3 çalıştırılamadı — karşılaştırma bu '
          f'nedenle TAMAMLANMIŞ SAYILMAZ.</b><br>'
          f'Paket: <code>timesfm {tfm.get("package_version")}</code> '
          f'(kod içe aktarma: {tfm.get("code_import")}), ağırlık: '
          f'<code>{tfm.get("weights_ref")}</code>.<br>'
          f'Ayrıntı: {html.escape(str(tfm.get("detail")))}<br>'
          f'Ağırlık lisansı: <code>{html.escape(str(tfm.get("weights_license")))}</code>; '
          f'kod lisansı: <code>{tfm.get("code_license")}</code>.</div>')
    elif tfm:
        A(f'<div class="kutu iyi">TimesFM 3 çalıştırıldı (paket {tfm.get("package_version")}, '
          f'cihaz {tfm.get("device")}).</div>')
    if prov and "yukarı akış" in str(prov):
        api = cfg["data"]["api_base"]
        A(f'<div class="kutu uyari"><b>Veri kaynağı.</b> {html.escape(str(prov))} '
          f'(<code>{api}</code> bu ortamın çıkış politikasınca engellidir — HTTP 403). '
          f'Kullanılan kaynak, API’nin kendi beslendiği '
          f'<code>{cfg["data"]["upstream_repo"]}</code> deposudur; içerik, plan '
          f'aşamasında doğrulanan başlangıç kontrolleriyle (594 kayıt, {cutoff} '
          f'aylık %3,0443 / YTD %24,0081 / yıllık %37,6979) birebir uyuşmaktadır.</div>')

    # ---------------- veri ----------------
    A("<h2>3. Veri kapsamı ve kalite denetimi</h2>")
    if kapsam is not None:
        A("<h3>Tablo 1a — Veri kapsamı</h3>")
        A(_fmt(kapsam))
    if audit is not None:
        A("<h3>Tablo 1b — Kalite denetimi</h3>")
        A('<p class="kucuk">Hiçbir kontrol veriyi sessizce düzeltmez. Yuvarlama '
          'farkları maddi uyuşmazlıklardan ayrı raporlanır; olağandışı enflasyon '
          'ayları silinmez veya kırpılmaz.</p>')
        A(_fmt(audit, 4))

    # ---------------- yöntem ----------------
    A("<h2>4. Yöntem ve zaman ayrımı</h2>")
    A(f'<div class="kutu"><b>Geliştirme doğrulaması:</b> hedefler '
      f'{cfg["split"]["dev_origin_start"]} – {cfg["split"]["dev_end"]} arasında '
      f'TAMAMLANMIŞ olmalıdır; kayan başlangıçlı, rastgele bölme yok.<br>'
      f'<b>Nihai holdout:</b> {cfg["split"]["holdout_start_origin"]} başlangıcından '
      f'itibaren ay ay ilerleyen, {cfg["split"]["holdout_end"]} sonuna kadar '
      f'tamamlanmış hedefler (24 ay). Model, pencere, özellik, ağırlık, birleşim '
      f'üyeleri, seçim metriği ve aralık kalibrasyonu holdout AÇILMADAN '
      f'dondurulmuştur.<br>'
      f'<b>Revizyon uyarısı:</b> geçmiş veri sürümleri (vintage) bulunmadığından bu '
      f'değerlendirme “son veri sürümüyle geriye dönük test”tir; o tarihte gerçekten '
      f'yapılmış canlı tahmin değildir.</div>')
    if man_bt:
        A(f'<p class="kucuk">{html.escape(man_bt.get("basitlik_notu", ""))}</p>')
    if cfgs is not None:
        A("<h3>Tablo 2 — Aday model / pencere / dönüşüm yapılandırmaları</h3>")
        A(_fmt(cfgs))

    # ---------------- geliştirme ----------------
    A("<h2>5. Geliştirme sıralaması</h2>")
    A(f'<p>Seçim skoru <code>S = {w["yearend"]}·MAE_yılsonu + {w["c6"]}·MAE_6ay + '
      f'{w["c12"]}·MAE_12ay</code>, tüm adaylar için '
      f'ORTAK başlangıçlarda hesaplanır. Ağırlıklar sonuçlar görülmeden '
      f'sabitlenmiştir ve sonradan değiştirilmemiştir.</p>')
    A('<div class="kutu">Yılsonu bileşeni yalnızca <b>üç başlangıcı da '
      '(Haziran/Ağustos/Ekim sonu) değerlendirilebilen tam yıllardan</b> '
      'hesaplanır; her yıl skora eşit ağırlıkla girer ve aynı yılın birden fazla '
      'tahmini bağımsız yıl gibi sayılmaz. Kısmi yıl sonuçları Tablo 3e’de '
      'ayrıca verilmiştir.<br>'
      '<b>Birleşim adaylarına dair uyarı:</b> birleşim üyeleri geliştirme '
      'skorlarına bakılarak seçildiği için birleşimin GELİŞTİRME skoru bu üye '
      'seçimi açısından iyimserdir. Üyeler ve ağırlıklar nihai testten önce '
      'dondurulmuştur; nihai test tablosu bu iyimserlikten etkilenmez.</div>')
    if dev_rank is not None:
        A("<h3>Tablo 3a — Geliştirme sıralaması (seçim skoru)</h3>")
        A(_fmt(dev_rank))
    if dev_sum is not None:
        A("<h3>Tablo 3b — Geliştirme: hedef bazında ayrıntılı hatalar</h3>")
        A(FULL_NOTE)
        A(_fmt(_view(dev_sum)))
    if sub_rank is not None:
        A("<h3>Tablo 3c — Alt dönem sıralamaları (dayanıklılık; ağırlık değiştirilmedi)</h3>")
        A('<p class="kucuk">Bu kesitler yalnızca sonuçların dayanıklılığını '
          'açıklamak içindir; sonuçlara bakılarak seçim ağırlıkları '
          'değiştirilmemiştir.</p>')
        A(_fmt(sub_rank))
    part = _t(cfg, "03e_kismi_yil_yilsonu.csv")
    if part is not None and len(part):
        A("<h3>Tablo 3e — Kısmi yıl yılsonu tahminleri (seçim skoruna girmez)</h3>")
        A(_fmt(part))
    aug = _t(cfg, "05b_agustos_aralik_mae.csv")
    if aug is not None:
        A("<h3>Tablo 5b — Ağustos → Aralık MAE (güncel kullanımın doğrudan karşılığı)</h3>")
        A(_fmt(aug))
    A(_fig_block(cfg, "g5_hata_isi_haritasi_gelistirme",
                 "Model × hedef ortalama mutlak hata (geliştirme)"))

    # ---------------- nihai test ----------------
    A("<h2>6. Nihai holdout testi (ayrı)</h2>")
    A('<div class="kutu uyari">Nihai test tablosu performansı yalnızca DENETLER. '
      'Test kazananına bakılarak seçilmiş model değiştirilmemiştir. 24 aylık testte '
      'yalnızca iki tamamlanmış yılsonu bulunur; yılsonu üstünlüğü yüksek kesinlikle '
      'kanıtlanmış sayılamaz. Bu testten sonra yapılacak geliştirmeler aynı dönemi '
      'yeniden bağımsız test hâline getirmez.</div>')
    if test_sum is not None:
        A("<h3>Tablo 3d — Nihai test sonuçları</h3>")
        A(FULL_NOTE)
        A(_fmt(_view(test_sum)))
    if horizon_tbl is not None:
        A("<h3>Tablo 4 — Ufuk bazında hatalar ve gözlem sayıları</h3>")
        A('<p class="kucuk">"referansa_gore_iyilesme_pct" sütunu, mevsimsel naive '
          'referansa göre AYNI değerlendirme gözlemlerinde MAE iyileşmesidir '
          '(pozitif = referanstan daha iyi). MASE paydası tüm modeller için '
          'ortaktır.</p>')
        A(FULL_NOTE)
        A(_fmt(_view(horizon_tbl)))
    if ye_tbl is not None:
        A("<h3>Tablo 5 — Yıl bazında yılsonu tahminleri ve gerçekleşmeler</h3>")
        A(_fmt(ye_tbl))
    if boot_tbl is not None:
        A("<h3>Tablo 11 — Blok bootstrap ile model farkları</h3>")
        A('<p class="kucuk">Yılsonu hedefinde blok = yıl. Diebold–Mariano testi '
          'isteğe bağlı destekleyici analizdir; anlamlı fark çıkmaması eşdeğerlik '
          'kanıtı değildir ve az örnek ile çoklu karşılaştırma sınırları geçerlidir.</p>')
        A(_fmt(boot_tbl, 4))
    A(_fig_block(cfg, "g5_hata_isi_haritasi_nihai_test",
                 "Model × hedef ortalama mutlak hata (nihai test)"))
    A(_fig_block(cfg, "g7_gelistirme_vs_nihai_test",
                 "Geliştirme ve nihai test performansının karşılaştırması"))
    A(_fig_block(cfg, "g4_yilsonu_tahmin_gerceklesme",
                 "Geçmiş yılsonu tahminleri ve gerçekleşmeler"))
    A(_fig_block(cfg, "g6_6ay_hatalar_zaman_icinde",
                 "Zaman içinde 6 aylık bileşik enflasyon tahmin hataları"))

    # ---------------- tahmin ----------------
    A("<h2>7. Nihai tahmin</h2>")
    if fc_tbl is not None:
        A("<h3>Tablo 6 — Aylık tahminler</h3>")
        A('<p class="kucuk">Aralıklar AYLIK yüzde değişim ölçüsündedir; bileşik '
          'dönem aralıkları Tablo 7b’de ayrıca verilmiştir. Kümülatif aralıklar '
          'aylık sınırların çarpımıyla ÜRETİLMEZ.</p>')
        A(_fmt(fc_tbl, 3))
    if per_tbl is not None:
        A("<h3>Tablo 7 — Dönem özetleri</h3>")
        A(_fmt(per_tbl, 3))
    if iv_tbl is not None:
        A("<h3>Tablo 7b — Nihai tahmin aralıkları (dönem hedefleri dahil)</h3>")
        A(_fmt(iv_tbl, 3))
    if comp_tbl is not None:
        A("<h3>Tablo 8 — Ana model ve iki alternatifin karşılaştırması</h3>")
        A(_fmt(comp_tbl, 3))
    for n, c in (("g1_aylik_enflasyon_ve_tahmin", "Son 5 yıl aylık enflasyon ve 12 aylık tahmin"),
                 ("g2_yillik_enflasyon_ve_tahmin", "Yıllık enflasyon ve tahmin"),
                 ("g3_kumulatif_tahmin_yolu", f"{cutoff} sonrası kümülatif tahmin yolu"),
                 ("g8_model_tahmin_farklari", "Ana model ve alternatiflerin tahmin farkları")):
        A(_fig_block(cfg, n, c))

    # ---------------- aralıklar ----------------
    A("<h2>8. Belirsizlik aralıkları</h2>")
    A('<div class="kutu">Aralıklar doğrudan İLGİLİ DÖNEM hedefinin geçmiş '
      'hatalarından (conformal, mutlak hata kuantili) üretilir; böylece zamansal '
      'bağımlılık korunur. Kalibrasyona yalnızca hedefi tahmin başlangıcına kadar '
      'GERÇEKLEŞMİŞ hatalar girer. Conformal yaklaşım rejim değişimlerinde otomatik '
      'geçerli kapsama garanti etmez. Örnek sayısı yetersizse aralık üretilmez; '
      'sahte kesinlik verilmez.<br>'
      '<b>Aralıkların yorumu.</b> Kullanılan yöntem mutlak hata kuantiline '
      'dayandığı için aralıklar tanımı gereği SİMETRİKTİR. KKTC serisindeki '
      'geçmiş 12 aylık bileşik hata dağılımı çok geniş olduğundan, özellikle '
      '12 aylık hedefte alt sınır ekonomik olarak zor gerçekleşecek (negatif) '
      'değerlere inebilir. Bu, yöntemin bilinen bir sınırıdır; yöntem sonuçlar '
      'görüldükten sonra değiştirilmemiştir. Aralık genişliği, uzun ufukta '
      'gerçek belirsizliğin büyüklüğü hakkında dürüst bir işarettir.<br>'
      '<b>Kuantil kısıtı.</b> Modelin kendi kuantillerini veren adaylar '
      '(ör. TimesFM 3, en dış kuantilleri 0,1/0,9) tek başına %95 aralığı '
      'desteklemez; ek yöntem olmadan bu adaylardan %95 aralık sunulmaz.</div>')
    if cov_tbl is not None and len(cov_tbl):
        A("<h3>Tablo 9 — Aralık kapsaması, genişliği ve skorları (ana hedefler)</h3>")
        A('<p class="kucuk">WIS yalnızca mevcut aralıklardan hesaplanan yaklaşık bir '
          'değerdir; tam CRPS değildir. Aşağıda ana hedefler ile seçilmiş aylık '
          'ufuklar gösterilmiştir; tüm ufuklar '
          '<code>artifacts/tables/09_aralik_kapsamasi.csv</code> dosyasındadır. '
          'Kapsama için keyfî tek bir "geçer/kalır" bandı kullanılmamıştır; '
          'gözlem sayısı her satırda verilmiştir.</p>')
        keep = ["yearend", "c6", "c12", "m1", "m3", "m6", "m12"]
        A(_fmt(cov_tbl[cov_tbl["hedef"].isin(keep)], 3))
        A('<p class="kucuk"><b>Yorum.</b> Nihai test döneminde kapsama oranları '
          'yüksek, aralıklar ise çok geniştir: kalibrasyon geçmişi 2021–2023 '
          'yüksek enflasyon dönemindeki büyük hataları içerdiğinden, görece '
          'sakin 2024–2026 döneminde aralıklar fazla geniş kalmıştır. Kapsamanın '
          '%100 olması iyi kalibrasyon değil, AŞIRI GENİŞ aralık işaretidir; '
          'gözlem sayısı da (yılsonu için 5) kesin bir kalibrasyon yargısı için '
          'azdır.</p>')

    # ---------------- başarısız denemeler ----------------
    A("<h2>9. Başarısız veya tamamlanmamış denemeler</h2>")
    A("<h3>Tablo 10 — Denemeler</h3>")
    rows = []
    if tfm and not tfm.get("available"):
        rows.append({"deneme": "TimesFM 3 (zero-shot, ctx 512/1024)",
                     "durum": "ÇALIŞTIRILAMADI",
                     "sebep": tfm.get("detail", ""),
                     "etki": "Zorunlu karşılaştırma bileşeni eksik."})
    for name, df in (("geliştirme", fail_dev), ("nihai test", fail_test)):
        if df is not None and not df.empty:
            g = df.groupby(["model", "sebep"]).size().reset_index(name="adet")
            for _, r in g.iterrows():
                rows.append({"deneme": f"{r['model']} ({name})", "durum": "ATLANDI",
                             "sebep": r["sebep"], "etki": f"{r['adet']} başlangıç"})
    if rows:
        A(_fmt(pd.DataFrame(rows)))
    else:
        A("<p>Kaydedilmiş başarısız deneme yok.</p>")

    # ---------------- lisans ve tekrarlanabilirlik ----------------
    A("<h2>10. Lisans, tekrarlanabilirlik ve sınırlar</h2>")
    A('<div class="kutu"><b>Araştırma vs. üretim ayrımı.</b> TimesFM 3.0 ön eğitimli '
      'ağırlıkları <code>timesfm-non-commercial-license-v1.0</code> altındadır ve '
      'ticari/üretim kullanımına kapalıdır (resmî depo README’si). Bu nedenle TimesFM '
      '3.0 yalnızca araştırma tarafında değerlendirilebilir. Bu çalışmadaki diğer tüm '
      'adaylar (statsmodels, scikit-learn, LightGBM) izin verici lisanslıdır ve '
      'üretimde kullanılabilir; dolayısıyla “üretimde kullanılabilecek en başarılı '
      'model”, TimesFM dışındaki adaylar arasından seçilen modeldir. '
      'Üretime dağıtım bu görevin kapsamı dışındadır.</div>')
    if man_fc:
        A(f'<p class="kucuk">Seed: {man_fc.get("seed")} · '
          f'Donanım: {html.escape(json.dumps(man_fc.get("donanim", {}), ensure_ascii=False))} · '
          f'Tepe bellek: {man_fc.get("tepe_bellek_mb")} MB<br>'
          f'{html.escape(man_fc.get("determinizm_notu",""))}</p>')
        A(f'<p class="kucuk">Paket sürümleri: '
          f'{html.escape(json.dumps(man_fc.get("paket_surumleri", {}), ensure_ascii=False))}</p>')
    rt_tbl = _t(cfg, "12_calisma_suresi_bellek.csv")
    if rt_tbl is not None and len(rt_tbl):
        A("<h3>Tablo 12 — Çalışma süresi ve bellek kullanımı</h3>")
        A('<p class="kucuk">Süreler geliştirme geriye dönük testinde başlangıç '
          'başına ölçülmüştür (tek çekirdek, CPU). Birleşim satırlarında süre '
          'üye modellerde sayıldığı için boştur. Bellek, sürecin tepe '
          'kullanımıdır. Önce küçük bir denemeyle (<code>--smoke</code>) '
          'ölçüm yapılmış, süre/GPU garantisi ölçmeden verilmemiştir.</p>')
        A(_fmt(rt_tbl, 3))
    if man_bt or man_ev:
        A(f'<p class="kucuk">Geliştirme geriye dönük test süresi: '
          f'{(man_bt or {}).get("sure_sn","—")} sn · Nihai test süresi: '
          f'{(man_ev or {}).get("sure_sn","—")} sn</p>')
    A('<div class="kutu uyari"><b>“En iyi model” ne demektir?</b> Bu ifade, bu veri '
      've önceden tanımlanan değerlendirme protokolünde en başarılı aday anlamındadır. '
      'Gelecekte en az hatayı yapacağına dair bir garanti içermez.</div>')

    body = "\n".join(S)
    html_doc = (f"<!doctype html><html lang='tr'><head><meta charset='utf-8'>"
                f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
                f"<title>KKTC TÜFE Tahmin Raporu — {cutoff}</title>"
                f"<style>{CSS}</style></head><body>{body}</body></html>")
    hp = adir / "rapor.html"
    hp.write_text(html_doc, encoding="utf-8")

    md = _markdown(cfg, frozen, per_tbl, fc_tbl, dev_rank, test_sum, tfm, prov,
                   cov_tbl, man_fc)
    mp = adir / "rapor.md"
    mp.write_text(md, encoding="utf-8")

    xp = _excel(cfg)
    return [hp, mp] + ([xp] if xp else [])


def _markdown(cfg, frozen, per_tbl, fc_tbl, dev_rank, test_sum, tfm, prov,
              cov_tbl, man_fc) -> str:
    cutoff = cfg["data"]["cutoff"]
    w = cfg["selection"]["weights"]
    L = [f"# KKTC TÜFE Tahmin Raporu (veri kesimi: {cutoff})", ""]
    if frozen:
        kz = frozen["frozen_extra"]["kazanan_yapilandirma"]
        L += [f"**Seçilen model:** `{frozen['winner']}` · aile: {kz['aile']} · "
              f"eğitim penceresi: {kz['pencere']} · dönüşüm: {kz['donusum']}",
              f"**Geliştirme seçim skoru S = {frozen['score']:.4f} yüzde puan** "
              f"(S = {w['yearend']}·MAE_yılsonu + {w['c6']}·MAE_6ay + {w['c12']}·MAE_12ay)",
              f"**Seçim kuralı:** {frozen['rule']}",
              f"**Donduruldu:** {frozen['frozen_at']} (nihai holdout açılmadan önce)", ""]
    if tfm and not tfm.get("available"):
        L += ["## ⚠ Eksik zorunlu bileşen", "",
              f"TimesFM 3 çalıştırılamadı: {tfm.get('detail')}",
              "Bu nedenle karşılaştırma **tamamlanmış sayılmaz**.", ""]
    if prov and "yukarı akış" in str(prov):
        L += [f"> Veri kaynağı notu: {prov} (`{cfg['data']['api_base']}` egress "
              f"politikasınca engelli). Kullanılan kaynak API'nin beslendiği "
              f"`{cfg['data']['upstream_repo']}` deposudur.", ""]
    if per_tbl is not None:
        L += ["## Dönem tahminleri", "", per_tbl.to_markdown(index=False), ""]
    if fc_tbl is not None:
        L += ["## Aylık tahminler", "", fc_tbl.to_markdown(index=False), ""]
    if dev_rank is not None:
        L += ["## Geliştirme sıralaması", "", dev_rank.head(25).to_markdown(index=False), ""]
    if test_sum is not None:
        L += ["## Nihai test (yalnızca denetim)", "",
              test_sum[test_sum["hedef"].isin(["yearend", "c6", "c12"])]
              .to_markdown(index=False), ""]
    if cov_tbl is not None:
        L += ["## Aralık kapsaması", "", cov_tbl.to_markdown(index=False), ""]
    L += ["## Sınırlar", "",
          "- Geçmiş veri sürümleri yoktur; değerlendirme *son veri sürümüyle geriye "
          "dönük test*tir.",
          "- 24 aylık nihai testte yalnızca iki tamamlanmış yılsonu vardır.",
          "- \"En iyi model\", bu veri ve bu protokolde en başarılı adaydır; gelecek "
          "performans garantisi değildir.",
          "- TimesFM 3.0 ağırlıkları ticari/üretim kullanımına kapalıdır "
          "(`timesfm-non-commercial-license-v1.0`).", ""]
    return "\n".join(L)


def _excel(cfg) -> Path | None:
    tdir = out_dir(cfg, "tables")
    files = sorted(tdir.glob("*.csv"))
    if not files:
        return None
    xp = out_dir(cfg) / "tablolar.xlsx"
    with pd.ExcelWriter(xp, engine="openpyxl") as xw:
        for f in files:
            try:
                df = pd.read_csv(f)
            except Exception:
                continue
            if df.empty and not len(df.columns):
                continue
            sheet = f.stem[:31]
            df.to_excel(xw, sheet_name=sheet, index=False)
    return xp
