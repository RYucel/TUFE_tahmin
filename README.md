# KKTC TÜFE Tahmin Sistemi

KKTC Tüketici Fiyat Endeksi (TÜFE) verisini kullanarak aday tahmin modellerini
**geçmiş tahmin performansına göre** karşılaştıran, kazananı önceden tanımlanmış
bir kuralla seçen ve seçilen yapılandırmayla gelecek 12 ayı tahmin eden,
tekrarlanabilir bir Python uygulaması.

Bu çalışma için **veri kesimi Ağustos 2026**, **tahmin dönemi Eylül 2026 –
Ağustos 2027**'dir.

---

## Ana hedefler (öncelik sırasıyla)

| # | Hedef | Tanım |
|---|-------|-------|
| 1 | **Yılsonu enflasyonu** | Aralık 2026'nın Aralık 2025'e göre değişimi |
| 2 | **Gelecek 6 ayın bileşik enflasyonu** | Eylül 2026 – Şubat 2027 |
| 3 | **Gelecek 12 ayın bileşik enflasyonu** | Eylül 2026 – Ağustos 2027 |
| 4 | Aylık ve yıllık enflasyon | Her ay için |

Ek çıktılar: Temmuz–Aralık 2026 bileşik değişimi (2 ay gerçekleşme + 4 ay
tahmin), Ocak–Haziran 2027 bileşik değişimi, Şubat 2027 yıllık enflasyonu.

> **Ölçüler karıştırılmaz.** “Gelecek 6 ayın bileşik enflasyonu”, “6 ay sonra
> yıllık enflasyon” ve “takvim yarıyılı enflasyonu” farklı büyüklüklerdir ve
> tüm tablo/grafiklerde ayrı gösterilir.

## Seçim skoru

```
S = 0,60 × MAE_yılsonu + 0,30 × MAE_6ay + 0,10 × MAE_12ay      (yüzde puan)
```

Ağırlıklar `config.yaml` içinde, **sonuçlar görülmeden** sabitlenmiştir.
Seçim **yalnızca geliştirme doğrulaması** skoruyla yapılır; nihai holdout
yalnızca denetim amaçlıdır.

---

## Kurulum

Gereksinim: Python 3.11+

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

TimesFM 3 (isteğe bağlı, ağ erişimi gerekir):

```bash
pip install "timesfm[torch]"                       # kod (Apache-2.0)
# ağırlıklar: https://huggingface.co/google/timesfm-3.0-pytorch
```

> **Lisans uyarısı.** TimesFM kaynak kodu Apache-2.0'dır; **TimesFM 3.0 ön
> eğitimli ağırlıkları `timesfm-non-commercial-license-v1.0` altındadır ve
> ticari/üretim kullanımına kapalıdır.** Bu nedenle rapor, "araştırmada en
> başarılı model" ile "lisans açısından üretimde kullanılabilecek en başarılı
> model"i ayrı belirtir.

## Çalıştırma

```bash
python run.py data        # veri indirme, önbellek, kalite denetimi, manifest
python run.py backtest    # geliştirme doğrulaması (kayan başlangıç)
python run.py select      # seçim + DONDURULMUŞ seçim dosyası
python run.py evaluate    # nihai holdout (dondurulmuş dosya olmadan çalışmaz)
python run.py forecast    # Eylül 2026 – Ağustos 2027 tahmini + arşiv
python run.py report      # grafikler + Türkçe HTML/Markdown rapor + Excel
python run.py all         # hepsi, sırayla
```

Faydalı seçenekler:

* `--refresh` — ham veriyi yeniden indirir (varsayılan: önbellekten çalışır)
* `--smoke N` — yalnızca son N başlangıçla küçük deneme (süre/bellek ölçümü için)

`evaluate` aşaması `artifacts/selection/frozen_selection.json` yoksa
**çalışmaz**; bu, nihai testin seçimden sonra geldiğini garanti eder.

---

## Veri kaynağı

Birincil kaynak KKTC TÜFE API'sidir:
`https://kktc-tufe-api.stevevaius.workers.dev`
(uç noktalar `/api/v1/meta`, `/api/v1/latest`, `/api/v1/tufe`, `/api/v1/periods`,
`/api/openapi.json`; uç nokta adları OpenAPI belgesinden doğrulanır, sayfalama
`limit`/`offset` ile tüketilir).

API'ye ulaşılamazsa uygulama, **API'nin kendi beslendiği** yukarı akış veri
deposuna düşer (`https://github.com/RYucel/kktc_tufe` →
`docs/data/tufe.json` ve `GRETL_TUFE.csv`) ve bu durum manifest'e, denetim
tablosuna ve rapora **açıkça** yazılır. Kaynak sessizce değiştirilmez.

Kapsam (bu çalışmada doğrulanmıştır):

* Ana seri: **Mart 1977 – Ağustos 2026, 594 aylık kayıt**
* Sepet madde fiyatları: **Ocak 2015 – Ağustos 2026, 520 kalem × 140 ay**
* Ağustos 2026: aylık %3,0443 · YTD %24,0081 · yıllık %37,6979

## Birim sözleşmesi

| Sembol | Anlam |
|--------|-------|
| `r_t` | aylık yüzde değişim (ör. `3.0443` = %3,0443) |
| `z_t` | `log(1 + r_t/100)` — **100 ile çarpılmamış** log değişim |

```
r_t          = 100 × (exp(z_t) − 1)
C(t,h)       = 100 × [exp(Σ z_(t+j), j=1…h) − 1]
yılsonu      = 100 × [(1 + gerçekleşmiş_YTD/100) × exp(Σ gelecek_log) − 1]
yıllık       = 100 × [exp(son 12 ayın log toplamı) − 1]
```

Aylık yüzdeler **toplanarak** bileşik enflasyon üretilmez; log ölçekteki hata
yüzde puan hatası olarak raporlanmaz. API endeks düzeyi vermediğinden oranlardan
üretilen endeks **sentetik zincir endeks** olarak etiketlenir (pozitiftir,
monoton artması gerekmez).

## Zaman ayrımı

* **Geliştirme doğrulaması:** Ocak 2015 – Ağustos 2024 içinde *tamamlanmış*
  hedefler, kayan başlangıçlı. Rastgele eğitim/test bölmesi yoktur.
* **Nihai holdout:** Eylül 2024 – Ağustos 2026 (24 ay). Ağustos 2024
  başlangıcından itibaren ay ay ilerlenir. Holdout açılmadan önce model,
  pencere, dönüşüm, hiperparametre, özellik, birleşim üyeleri/ağırlıkları,
  seçim metriği, eşitlik kuralı ve aralık kalibrasyonu **dondurulur**.

> Geçmiş veri sürümleri (vintage) mevcut değildir; bu nedenle değerlendirme
> **“son veri sürümüyle geriye dönük test”**tir, o tarihte gerçekten yapılmış
> canlı tahmin değildir.

## Proje yapısı

```
config.yaml                 tüm ayarlar, seçim ağırlıkları ve kuralları
run.py                      aşama yürütücüsü
src/
  config.py                 yapılandırma yükleme
  data.py                   veri alma (API + yukarı akış), önbellek, denetim
  transforms.py             log dönüşümü, bileşik/YTD/yılsonu/yarıyıl hesapları
  features.py               sızıntısız özellikler + sepet özet/faktörleri
  models/
    base.py                 ortak model arayüzü (adaptör)
    baselines.py            zorunlu referans modeller
    statistical.py          ETS, SARIMA (küçük ızgara), AutoTheta, UCM
    ml.py                   Ridge / ElasticNet / LightGBM (doğrudan ufuk)
    timesfm_adapter.py      TimesFM 3 (resmî arayüz) + erişilebilirlik denetimi
  registry.py               aday model/pencere/dönüşüm listesi
  backtest.py               kayan başlangıçlı test, hedef türetme, MASE paydası
  metrics.py                MAE/RMSE/ME/MASE/interval score/WIS/bootstrap/DM
  calibration.py            conformal aralıklar (yalnızca gerçekleşmiş hatalar)
  selection.py              ortak başlangıç, seçim skoru, dondurma
  forecast.py               nihai tahmin, dönem özetleri, arşiv
  plots.py                  Türkçe grafikler (PNG + SVG)
  report.py                 Türkçe HTML/Markdown rapor + Excel
tests/                      pytest testleri
artifacts/                  çıktılar (tablolar, grafikler, rapor, manifest)
```

## Çıktılar

* `artifacts/rapor.html`, `artifacts/rapor.md` — Türkçe rapor
* `artifacts/tables/*.csv`, `artifacts/tablolar.xlsx` — tablolar
* `artifacts/figures/*.png|svg` — grafikler
* `artifacts/forecast/nihai_tahmin.json` — nihai tahmin
* `artifacts/forecast/arsiv/` — tarihli tahmin arşivi (sonradan gerçekleşmelerle
  karşılaştırmak için; zamanlanmış otomasyon bu görevin kapsamında değildir)
* `artifacts/ham_gecmis_tahminler.parquet` — tüm ham geriye dönük tahmin yolları
* `artifacts/selection/frozen_selection.json` — dondurulmuş seçim
* `artifacts/manifest_*.json` — ayarlar, veri özeti, paket sürümleri, seed,
  süre, donanım

## Testler

```bash
python -m pytest tests -q
```

Testler; API şeması ve sayfalamayı, tarih kesimini, log dönüşümünün ters
dönüşümünü, bileşik/YTD/yarıyıl/Aralık-Aralık hesaplarını, negatif enflasyonda
sentetik endeksi, gecikmeli özelliklerde sızıntıyı, çok adımlı eğitim
hedeflerinin kesim sınırını, kalibrasyonda yalnızca gerçekleşmiş hataların
kullanılmasını, MAE/MASE/seçim skorunu, ortak MASE paydasını, tahminin 12 ayı
eksiksiz kapsamasını ve seçim sonrası eğitim penceresinin korunmasını doğrular.

**Kabul koşulu olmayanlar (bilerek):** karmaşık modelin referansı yenmesi, bir
modelin MASE < 0,9 olması, belirli bir kapsama bandı, sentetik endeksin sürekli
artması. Başarı ölçütü **doğru, sızıntısız, tekrarlanabilir karşılaştırma ve
dürüst raporlamadır.**

## Tekrarlanabilirlik

Sabit seed (`config.yaml → project.seed`) kullanılır. LightGBM/BLAS iş parçacığı
sayısı ve donanım farklılıkları nedeniyle son basamak düzeyinde tam determinizm
garanti edilmez; bu, her manifest içinde belirtilir.

## Sınırlar

* 24 aylık nihai testte yalnızca **iki tamamlanmış yılsonu** vardır; yılsonu
  üstünlüğü yüksek kesinlikle kanıtlanmış sayılamaz.
* Conformal aralıklar rejim değişimlerinde otomatik geçerli kapsama garanti
  etmez; örnek yetersizse aralık üretilmez.
* **“En iyi model”**, bu veri ve önceden tanımlanan protokolde en başarılı aday
  anlamındadır; gelecek performans garantisi değildir.
* Üretime dağıtım bu görevin kapsamı dışındadır.
