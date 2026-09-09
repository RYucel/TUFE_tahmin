"""Colab defterini üretir: notebooks/KKTC_TUFE_Tahmin_Colab.ipynb"""
import json, pathlib, re

cells = []

# Her kod hücresinin ÜSTÜNE konacak markdown açıklaması.
# Anahtar: kod içindeki "#@title" başlığı (form süslemesi temizlenmiş hâli).
HUCRE_ACIKLAMA = {
 "AYARLAR": "Defterin tek kontrol noktası. Aşağıdaki değerleri değiştirip "
   "*Tümünü çalıştır* demeniz yeterli; başka hiçbir hücreye dokunmanız gerekmez.\n\n"
   "⚠️ **`HIZLI_MOD` sonuçları anlamlı biçimde değiştirir.** `True` iken "
   "geliştirme doğrulaması yalnızca **son 48 başlangıçla** (2020-09 → 2024-08) "
   "koşar; bu, 2021-2023 yüksek enflasyon dönemine denk gelen dar ve zor bir "
   "kesittir. Yılsonu bileşenine yalnızca **3 yıl × 3 başlangıç = 9 gözlem** "
   "girer, oysa skorun %60'ı bu bileşendir. Alt dönem tablosundaki "
   "*2015-2020* satırları da bu yüzden boş çıkar.\n\n"
   "Sıralamayı ciddiye alacaksanız **`HIZLI_MOD = False`** yapın: 116 başlangıç "
   "(2015-01 → 2024-08), yılsonunda 27 gözlem / 9 yıl. Süre GPU'da ~20-30 dk.",
 "Paketleri kur": "Colab'de hazır gelmeyen paketleri kurar. `TIMESFM_CALISTIR` açıksa "
   "TimesFM 3.0 arayüzü (`timesfm3`) resmî depodan kurulur — PyPI çarkı yalnızca 2.5 "
   "kodunu taşıyabildiği için depo kurulumu 3.0'ı garanti eder.",
 "Donanım ve sürüm tespiti": "Ölçülen süre ve bellek değerleri donanıma bağlıdır; bu "
   "hücre raporlanan sayıların bağlamını kaydeder. GPU yoksa uyarı basar — defter yine "
   "çalışır, yalnızca TimesFM yavaşlar.",
 "Depoyu klonla ve içeri al": "Depo `/content/TUFE_tahmin` altına klonlanır ve "
   "`sys.path`'e eklenir. Çalışılan commit yazdırılır, böylece çıktıların hangi "
   "sürümle üretildiği belli olur.",
 "Yapılandırmayı yükle": "`config.yaml` okunur ve yalnızca ortama özgü alanlar "
   "(kesim, ufuk, TimesFM ayarları) üzerine yazılır. **Seçim ağırlıkları ve beraberlik "
   "kuralı burada değiştirilmez** — sonuçlar görülmeden sabitlenmiştir.",
 "Veriyi indir": "Birincil kaynak KKTC TÜFE API'sidir; uç nokta adları OpenAPI "
   "belgesinden doğrulanır ve sayfalama `limit`/`offset` ile tüketilir. API'ye "
   "ulaşılamazsa **API'nin kendi beslendiği** yukarı akış deposuna düşülür ve bu durum "
   "açıkça yazdırılır — kaynak sessizce değiştirilmez.",
 "Kalite denetimi": "Kontroller veriyi **düzeltmez**, yalnızca raporlar. Yuvarlama "
   "farkları (≤ 0,02 puan) ile maddi uyuşmazlıklar (> 0,25 puan) ayrı sayılır; "
   "olağandışı enflasyon ayları silinmez ve kırpılmaz.",
 "Seri, rejimler ve dağılım": "Üç panel: tüm tarih aylık değişim, resmî yıllık "
   "enflasyon ve oranlardan üretilen **sentetik zincir endeks** (resmî endeks değildir; "
   "pozitiftir ama monoton artması gerekmez).",
 "Rejim tablosu ve mevsimsellik": "Dönem dönem ortalama ve oynaklık, takvim ayı "
   "etkisi ve otokorelasyon. 12. gecikmedeki değer mevsimsel modellerin işe yarayıp "
   "yaramayacağına dair ilk ipucudur.",
 "Sepet madde fiyatları": "520 kalemin özetleri ve resmî TÜFE ile karşılaştırması. "
   "Geçerli tarihsel sepet ağırlıkları bulunmadığından ağırlıksız kalem ortalaması "
   "resmî TÜFE tahmini olarak **sunulmaz**; yalnızca yardımcı bilgidir.",
 "TimesFM 3.0'ı yükle ve doğrula": "Defterin yerel ortama göre asıl farkı budur: "
   "Colab'de huggingface.co erişilebilir olduğu için TimesFM 3.0 gerçekten "
   "çalıştırılabilir. Hücre üç aşamayı ayrı raporlar — kod içe aktarma, ağırlık "
   "indirme, deneme tahmini — ve takılırsa hangi aşamada takıldığını gizlemez.",
 "TimesFM 3.0 tek başına": "Son 12 ay gizlenip modelden tahmin istenir. Bu **tek bir "
   "başlangıçtır ve model karşılaştırması değildir**; amacı modelin bu seride makul "
   "davranıp davranmadığını görmektir. Karşılaştırma aşağıdaki kayan başlangıçlı "
   "testle yapılır.",
 "Aday listesi": "Karşılaştırmaya girecek model/pencere/dönüşüm yapılandırmaları. "
   "Liste sonuçlar görülmeden tanımlanmıştır; `basitlik` sütunu beraberlik bozmada "
   "kullanılan önceden sabitlenmiş sıradır.\n\n"
   "**TimesFM sepet varyantı hakkında:** yardımcı seri 2015'te başladığı ve "
   "TimesFM `past_only_covariates` girdisini bağlamla aynı uzunlukta istediği "
   "için bu varyantın fiili bağlamı sepet dönemine (139 ay) kırpılır. Yardımcı "
   "verinin katkısı bağlam uzunluğu farkıyla karışmasın diye listeye **aynı kısa "
   "bağlamla çalışan tek değişkenli bir kontrol** de eklenir "
   "(`TimesFM3_zeroshot_ctx139`). Karşılaştırma bu ikisi arasında yapılmalıdır.",
 "Geliştirme geriye dönük testini çalıştır": "Her başlangıç `t` için yalnızca "
   "`z[≤ t]` ile eğitilir ve 12 ay tahmin edilir. TimesFM ince ayarsız olduğu için "
   "yeniden eğitim yoktur; tüm başlangıçların bağlamları tek seferde toplu verilir — "
   "sonuç tek tek çalıştırmayla özdeştir, yalnızca çok daha hızlıdır.\n\n"
   "**En uzun süren hücre budur.** `HIZLI_MOD = False` ise 20-30 dakika sürebilir.",
 "Birleşimleri ekle ve hedefleri puanla": "Birleşim üyeleri geliştirme skorlarına "
   "göre farklı ailelerden seçilir ve birleştirme **aylık log değişim ölçeğinde** "
   "yapılır; ekonomik dönüşümler (bileşik, YTD, yılsonu) birleşimden sonra tek ve "
   "tutarlı biçimde uygulanır.",
 "Geliştirme sıralaması": "Skor tüm adaylar için **ortak başlangıçlarda** hesaplanır, "
   "böylece daha az veya daha kolay dönem üzerinde çalışan model avantajlı "
   "gösterilmez. Yılsonu bileşeni yalnızca üç başlangıcı da (Haziran/Ağustos/Ekim "
   "sonu) değerlendirilebilen tam yıllardan gelir.",
 "Kazananı belirle ve SEÇİMİ DONDUR": "Kural önceden sabittir: en iyi skora göre "
   "%2'den yakın adaylar berabere sayılır, sonra daha basit, sonra daha ucuz model "
   "seçilir. Seçim dosyaya yazılır ve **nihai holdout ancak bundan sonra açılır**.\n\n"
   "Birleşim üyeleri geliştirme skorlarına bakılarak seçildiği için birleşimin "
   "*geliştirme* skoru bu açıdan iyimserdir; nihai test bundan etkilenmez.",
 "Alt dönem dayanıklılığı": "Sonuçların tek bir döneme mi bağlı olduğunu gösterir. "
   "Bu kesitlere bakılarak **ağırlıklar değiştirilmez** — yalnızca yorum içindir.",
 "Nihai testi çalıştır": "Dondurulmuş seçim dosyası olmadan bu hücre hata verir; kapı "
   "budur. Ağustos 2024'ten itibaren ay ay ilerlenir ve önceki test ayları sonraki "
   "başlangıçların eğitiminde kullanılabilir — ama test skorlarına bakılarak hiçbir "
   "ayar değiştirilmez.",
 "Nihai test sonuçları": "Bu tablo performansı yalnızca **denetler**. 24 aylık testte "
   "iki tamamlanmış yılsonu vardır; yılsonu üstünlüğü buradan yüksek kesinlikle "
   "kanıtlanamaz. Mevsimsel-naive'in test MASE'si de tanım gereği 1 değildir.",
 "Geliştirme ↔ nihai test tutarlılığı": "İki dönemin sıralamaları ne kadar örtüşüyor? "
   "Düşük korelasyon, tek bir 24 aylık pencerede sıralamanın ne kadar oynak "
   "olabildiğini gösterir — seçim yine de değiştirilmez.",
 "Model farkları": "Fark aralıkları örtüşen hataları hesaba katan blok bootstrap ile "
   "üretilir (yılsonunda blok = yıl). Diebold–Mariano **destekleyicidir**: anlamsız "
   "sonuç eşdeğerlik kanıtı değildir ve az örnek ile çoklu karşılaştırma sınırları "
   "geçerlidir.",
 "Kapsama, genişlik ve skorlar": "Aralıklar doğrudan ilgili dönem hedefinin geçmiş "
   "hatalarından üretilir; aylık sınırlar çarpılarak kümülatif aralık **oluşturulmaz**. "
   "Yüksek kapsama + çok geniş aralık, iyi kalibrasyon değil aşırı genişlik işaretidir.",
 "Yeniden eğit ve 12 aylık yolu üret": "Seçilmiş yapılandırma veri kesimine kadar "
   "yeniden eğitilir ve **seçilmiş eğitim penceresi korunur** — son 60 ay kazandıysa "
   "tüm geçmişe geçilmez.",
 "Dönem özetleri": "\"Gelecek 6 ayın bileşik enflasyonu\", \"6 ay sonra yıllık "
   "enflasyon\" ve \"takvim yarıyılı enflasyonu\" farklı büyüklüklerdir; burada ayrı "
   "satırlarda verilir. Yılsonu, doğrulanmış **resmî** Ağustos YTD değerinden başlar.",
 "Ana model ve iki alternatifin karşılaştırması": "Aynı dönem hedeflerinde ana model "
   "ile iki alternatifin tahminleri yan yana. Aradaki fark, tek bir sayıya ne kadar "
   "güvenilebileceği hakkında fikir verir.",
 "Tahmin grafikleri": "Gerçekleşme ve tahmin çizgi biçimiyle ayrılır, tahmin "
   "başlangıcı işaretlenir; başlık ve eksenlerde veri kesimi ile ölçü birimi bulunur.",
 "Model × hedef hata ısı haritası": "Hangi modelin hangi ufukta iyi olduğunu tek "
   "bakışta gösterir. Geliştirme ve nihai test ayrı ayrı çizilir.",
 "Tabloları, grafikleri ve Türkçe raporu üret": "Tüm çıktıları `artifacts/` altına "
   "yazar: CSV tablolar, Excel, PNG/SVG grafikler, tahmin JSON'u, tarihli arşiv ve "
   "çalıştırmanın manifest'i (ayarlar, sürümler, seed, süre, donanım).",
 "Raporu defterin içinde göster": "Üretilen Türkçe HTML raporunu defterin içine "
   "gömer. Aynı dosya `artifacts/rapor.html` olarak da diskte durur.",
 "Araştırmada ve üretimde en başarılı modeller": "TimesFM 3.0 ağırlıkları ticari ve "
   "üretim kullanımına kapalı olduğundan iki soru ayrı yanıtlanır: bu veride en "
   "başarılı aday hangisi, ve lisans açısından üretimde kullanılabilecek en başarılı "
   "aday hangisi.",
 "Testleri çalıştır": "Depodaki test paketi: sızıntı kontrolleri, ekonomik formüller, "
   "ortak MASE paydası, kalibrasyonun zaman kuralı ve seçim kuralı. Hepsi geçmeli.",
 "Bütün çıktıları ZIP olarak indir": "`artifacts/` dizinini tek dosyada indirir. "
   "Colab çalışma zamanı kapandığında diskteki her şey silinir, bu yüzden saklamak "
   "istediklerinizi buradan indirin.",
}


def _aciklama_bul(baslik: str) -> str:
    """Başlığa en iyi eşleşen açıklamayı bulur (önek eşleşmesi yeterlidir)."""
    if baslik in HUCRE_ACIKLAMA:
        return HUCRE_ACIKLAMA[baslik]
    for anahtar, metin in HUCRE_ACIKLAMA.items():
        if baslik.startswith(anahtar):
            return metin
    return ""


def _lines(src: str) -> list[str]:
    """Metni .ipynb `source` listesine çevirir.

    nbformat sözleşmesi: liste elemanları AYIRAÇSIZ birleştirilir, bu yüzden
    son satır dışında her satır kendi "\n" karakterini taşımalıdır. Aksi hâlde
    hücre görüntüleyicide tek satıra yapışır.
    """
    text = src.strip("\n")
    return [ln + "\n" for ln in text.split("\n")[:-1]] + [text.split("\n")[-1]]


def md(src):
    cells.append({"cell_type": "markdown", "metadata": {},
                  "source": _lines(src)})

def code(src, **meta):
    """Kod hücresi ekler; varsa "#@title" başlığını AYRI bir markdown hücresine taşır.

    Colab, "#@title" ile başlayan hücrelerin kodunu gizler ve yalnızca form
    başlığını gösterir. Başlığı ve açıklamayı markdown hücresine almak kodu
    görünür kılar ve defteri okunur hâle getirir.
    """
    text = src.strip("\n")
    satirlar = text.split("\n")

    baslik = None
    if satirlar and satirlar[0].lstrip().startswith("#@title"):
        ham = satirlar[0].split("#@title", 1)[1]
        baslik = re.sub(r"\{[^}]*\}", "", ham).strip()          # { display-mode: ... } at
        satirlar = satirlar[1:]
        while satirlar and not satirlar[0].strip():
            satirlar = satirlar[1:]

    # Colab form açıklamalarını (#@param) kaldır: kod her ortamda düz Python kalsın
    satirlar = [re.sub(r"\s*#@param\b.*$", "", ln) for ln in satirlar]

    if baslik:
        parcalar = [f"### {baslik}"]
        aciklama = _aciklama_bul(baslik)
        if aciklama:
            parcalar.append(aciklama)
        md("\n\n".join(parcalar))

    m = {"id": f"c{len(cells)}"}
    m.update(meta)
    cells.append({"cell_type": "code", "execution_count": None, "metadata": m,
                  "outputs": [], "source": _lines("\n".join(satirlar))})

# ---------------------------------------------------------------- 0. başlık
md(r"""
<a href="https://colab.research.google.com/github/RYucel/TUFE_tahmin/blob/claude/kktc-tufe-forecast-kq7hpl/notebooks/KKTC_TUFE_Tahmin_Colab.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Colab'de aç"/></a>

# KKTC TÜFE Tahmin Sistemi — Tam Analiz ve Tahmin Defteri (Google Colab)

**Veri kesimi:** Ağustos 2026 · **Tahmin dönemi:** Eylül 2026 – Ağustos 2027

Bu defter, depodaki üretim boru hattının (`run.py`) tamamını Colab'de çalıştırır ve
**yerel ortamda çalıştırılamayan TimesFM 3.0'ı da karşılaştırmaya dâhil eder**
(Colab'de huggingface.co erişimi ve GPU vardır).

---

## Ne yapar?

| Bölüm | İş |
|---|---|
| 1 | Kurulum, GPU ve sürüm tespiti |
| 2 | Depoyu çekme, sabit seed |
| 3 | Veri alma (API → yukarı akış geri düşüşü), kalite denetimi |
| 4 | Keşifsel analiz: seri, rejimler, mevsimsellik, sepet |
| 5 | **TimesFM 3.0 kurulumu, ağırlık indirme ve doğrulama** |
| 6 | Geliştirme doğrulaması (kayan başlangıç, TimesFM dâhil) |
| 7 | Model seçimi ve **seçimin dondurulması** |
| 8 | Nihai holdout testi (yalnızca denetim) |
| 9 | Belirsizlik aralıkları ve kapsama |
| 10 | Eylül 2026 – Ağustos 2027 tahmini |
| 11 | Grafikler ve Türkçe rapor |
| 12 | Araştırma vs. üretim lisansı ayrımı, çıktıların indirilmesi |

## Yöntemin değişmeyen kuralları

* **Seçim yalnızca geliştirme skoruyla yapılır.** Nihai holdout (Eyl 2024 – Ağu 2026)
  yalnızca performansı denetler; test kazananına bakılarak seçim değiştirilmez.
* Seçim skoru sonuçlar görülmeden sabitlenmiştir:
  `S = 0,60·MAE_yılsonu + 0,30·MAE_6ay + 0,10·MAE_12ay` (yüzde puan).
* Birim sözleşmesi `z = log(1 + r/100)`; aylık yüzdeler **toplanmaz**, bileşik alınır.
* Hiçbir aşamada gelecek bilgi kullanılmaz; kalibrasyona yalnızca **gerçekleşmiş**
  hatalar girer.
* Sonuçlar görüldükten sonra ağırlık, metrik veya seçim kuralı değiştirilmez.

> ⚠️ **TimesFM 3.0 ağırlık lisansı:** `timesfm-non-commercial-license-v1.0` —
> ticari/üretim kullanımına **kapalıdır**. Bu defter, "araştırmada en başarılı
> model" ile "üretimde kullanılabilecek en başarılı model"i ayrı raporlar.

> **Çalıştırma sırası:** Çalışma zamanı → Türü değiştir → **GPU (T4 yeterli)**,
> sonra Çalışma zamanı → **Tümünü çalıştır**. GPU'suz da çalışır, TimesFM yavaşlar.
""")

# ---------------------------------------------------------------- 1. kurulum
md(r"""
---
## 1. Ortam kurulumu

`AYARLAR` hücresi defterin tek kontrol noktasıdır. `HIZLI_MOD = True` iken
geliştirme doğrulaması son 48 başlangıçla koşar (~5 dk); tam çalıştırma için
`False` yapın (~20-30 dk, GPU'da).
""")

code(r"""
#@title AYARLAR { display-mode: "form" }

REPO_URL   = "https://github.com/RYucel/TUFE_tahmin.git"  #@param {type:"string"}
REPO_BRANCH= "claude/kktc-tufe-forecast-kq7hpl"           #@param {type:"string"}

HIZLI_MOD  = True   #@param {type:"boolean"}
SON_N_BASLANGIC = 48 #@param {type:"integer"}

TIMESFM_CALISTIR = True  #@param {type:"boolean"}
TIMESFM_CTX = [512, 1024]
TIMESFM_SEPET_VARYANTI = True #@param {type:"boolean"}

VERI_KESIMI = "2026-08" #@param {type:"string"}
UFUK = 12

print(f"Hızlı mod: {HIZLI_MOD} · TimesFM: {TIMESFM_CALISTIR} · kesim: {VERI_KESIMI}")
""")

code(r"""
#@title Paketleri kur (2-4 dk)
import subprocess, sys, os

def sh(cmd, quiet=True):
    print(f"$ {cmd}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2500:]); print(r.stderr[-2500:])
    elif not quiet:
        print(r.stdout[-1500:])
    return r.returncode

# Colab'de zaten var: numpy, pandas, scipy, sklearn, matplotlib, torch
sh("pip install -q 'statsmodels>=0.14' 'lightgbm>=4.3' pyarrow openpyxl "
   "tabulate pyyaml requests pytest")

if TIMESFM_CALISTIR:
    # TimesFM 3.0 arayüzü (timesfm3) resmî depoda; PyPI çarkı yalnızca 2.5 kodunu
    # taşıyabiliyor. Resmî depodan kurulum TimesFM 3.0'ı garanti eder.
    sh("pip install -q 'git+https://github.com/google-research/timesfm.git'")
    sh("pip install -q 'huggingface_hub>=0.28'")
print("kurulum bitti")
""")

code(r"""
#@title Donanım ve sürüm tespiti (raporlanan ölçümlerin bağlamı)
import platform, os, json
import numpy as np, pandas as pd

info = {"platform": platform.platform(), "python": platform.python_version(),
        "cpu": os.cpu_count()}
try:
    import torch
    info["torch"] = torch.__version__
    info["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "yok (CPU)"
    if torch.cuda.is_available():
        info["gpu_bellek_gb"] = round(torch.cuda.get_device_properties(0).total_memory/1e9, 1)
except Exception as e:
    info["torch"] = f"yok ({e})"
try:
    import psutil; info["ram_gb"] = round(psutil.virtual_memory().total/1e9, 1)
except Exception: pass
for k, v in info.items(): print(f"{k:>16}: {v}")

if str(info.get("gpu", "")).startswith("yok"):
    print("\n⚠️  GPU yok. TimesFM CPU'da da çalışır ama belirgin biçimde yavaştır.")
    print("   Çalışma zamanı → Türü değiştir → Donanım hızlandırıcı → GPU")
""")

# ---------------------------------------------------------------- 2. depo
md(r"""
---
## 2. Depoyu çek ve sabit seed'i ayarla

Defter, depodaki modülleri (`src/`) **olduğu gibi** kullanır — yani burada
çalışan kod ile `run.py`'nin çalıştırdığı kod aynıdır. Defterde yeniden yazılmış
bir kopya yoktur; sonuçlar bu yüzden karşılaştırılabilir.
""")

code(r"""
#@title Depoyu klonla ve içeri al
import subprocess, sys, os
from pathlib import Path

ROOT = Path("/content/TUFE_tahmin")
if not ROOT.exists():
    subprocess.run(f"git clone -q --branch {REPO_BRANCH} --depth 1 {REPO_URL} {ROOT}",
                   shell=True, check=True)
else:
    subprocess.run(f"git -C {ROOT} pull -q", shell=True)
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
print("HEAD:", subprocess.run("git rev-parse --short HEAD", shell=True,
                              capture_output=True, text=True).stdout.strip())
print(sorted(p.name for p in (ROOT/'src').iterdir()))
""")

code(r"""
#@title Yapılandırmayı yükle, seed'i sabitle
import random, warnings, numpy as np, pandas as pd
warnings.filterwarnings("ignore")

from src.config import load_config, out_dir
cfg = load_config()
cfg["data"]["cutoff"] = VERI_KESIMI
cfg["horizon"] = UFUK
cfg["timesfm"]["enabled"] = bool(TIMESFM_CALISTIR)
cfg["timesfm"]["context_lengths"] = list(TIMESFM_CTX)
cfg["timesfm"]["with_covariates"] = bool(TIMESFM_SEPET_VARYANTI)

SEED = int(cfg["project"]["seed"])
random.seed(SEED); np.random.seed(SEED); os.environ["PYTHONHASHSEED"] = str(SEED)
try:
    import torch; torch.manual_seed(SEED)
except Exception: pass

pd.set_option("display.width", 200, "display.max_columns", 60,
              "display.float_format", lambda v: f"{v:,.3f}")
print("seed:", SEED)
print("seçim ağırlıkları (sonuçlar görülmeden sabit):", cfg["selection"]["weights"])
print("beraberlik kuralı:", cfg["selection"]["tie_break"],
      f"(eşik %{cfg['selection']['tie_relative_threshold']*100:.0f})")
""")

# ---------------------------------------------------------------- 3. veri
md(r"""
---
## 3. Veri alma ve kalite denetimi

Birincil kaynak KKTC TÜFE API'sidir; uç nokta adları OpenAPI belgesinden
doğrulanır ve sayfalama `limit`/`offset` ile tüketilir (tek yanıtın bütün seriyi
içerdiği varsayılmaz). API'ye ulaşılamazsa uygulama, **API'nin kendi beslendiği**
yukarı akış deposuna düşer ve bunu açıkça raporlar.
""")

code(r"""
#@title Veriyi indir (API → yukarı akış geri düşüşü)
from src import data as DATA
import time

t0 = time.time()
bundle = DATA.get_data(cfg, refresh=True)
print(f"{time.time()-t0:.1f} sn · köken: {bundle.provenance.upper()}")
print(f"Ana seri : {len(bundle.monthly)} ay  {bundle.monthly.index.min()} – {bundle.monthly.index.max()}")
if bundle.items is not None:
    print(f"Sepet    : {bundle.items.shape[1]} kalem × {bundle.items.shape[0]} ay "
          f"{bundle.items.index.min()} – {bundle.items.index.max()}")
if bundle.api_openapi_endpoints:
    print("OpenAPI'den doğrulanan uç noktalar:")
    for e in bundle.api_openapi_endpoints: print("   ", e)
for s in bundle.sources:
    if s.status != "ok":
        print(f"⚠️  ERİŞİLEMEDİ [{s.name}] {s.url}\n     {s.detail[:200]}")
bundle.monthly.tail(6)
""")

code(r"""
#@title Kalite denetimi (Tablo 1)
audit = DATA.audit(bundle, cfg)
def _renk(r):
    c = {"GEÇTİ":"#e8f5e9","UYARI":"#fff8e1","ENGEL":"#ffebee","KALDI":"#ffebee",
         "BİLGİ":"#eef2f7"}.get(r["durum"], "")
    return [f"background-color:{c}"]*len(r)
display(audit.style.apply(_renk, axis=1).set_properties(
    subset=["ayrinti"], **{"white-space":"normal","text-align":"left"}))
print(audit["durum"].value_counts().to_string())
""")

md(r"""
**Denetimin okunuşu.** Kontroller veriyi *düzeltmez*, yalnızca raporlar.
Yuvarlama farkları (≤ 0,02 puan) ile maddi uyuşmazlıklar (> 0,25 puan) ayrı
sayılır. Olağandışı enflasyon ayları **silinmez ve kırpılmaz** — ekonomik şoklar
tahmin probleminin parçasıdır. Geçmiş veri sürümleri (vintage) bulunmadığından
bu çalışma "son veri sürümüyle geriye dönük test"tir.
""")

# ---------------------------------------------------------------- 4. EDA
md(r"""
---
## 4. Keşifsel analiz

Bu bölüm yalnızca **anlamak** içindir; hiçbir model seçimi kararı buradan
alınmaz.
""")

code(r"""
#@title Seri, rejimler ve dağılım
import matplotlib.pyplot as plt
from src.transforms import to_log, synthetic_chain_index, compound_pct

m = bundle.monthly
z = to_log(m["aylikYuzde"]).dropna(); z.name = "z"
r = m["aylikYuzde"]

fig, ax = plt.subplots(3, 1, figsize=(13, 11))
ax[0].plot(r.index.to_timestamp(), r.values, lw=0.8, color="#1b3a6b")
ax[0].set_title(f"Aylık TÜFE değişimi, tüm tarih ({m.index.min()} – {m.index.max()}) · %")
ax[0].set_ylabel("Aylık %")

y = m["yillikYuzde"].dropna()
ax[1].plot(y.index.to_timestamp(), y.values, lw=1.0, color="#c1440e")
ax[1].axhline(0, color="0.5", lw=0.8)
ax[1].set_title("Yıllık enflasyon (resmî) · %"); ax[1].set_ylabel("Yıllık %")

idx = synthetic_chain_index(r)
ax[2].semilogy(idx.index.to_timestamp(), idx.values, lw=1.0, color="#2e7d32")
ax[2].set_title("SENTETİK zincir endeks (oranlardan üretildi — resmî endeks DEĞİLDİR), log ölçek")
ax[2].set_ylabel("Endeks (1977-03 = 100)")
for a in ax: a.grid(alpha=.3)
plt.tight_layout(); plt.show()

print("Endeks pozitif mi:", bool((idx > 0).all()),
      "· monoton artıyor mu:", bool(idx.is_monotonic_increasing),
      "(monoton artması GEREKMEZ)")
""")

code(r"""
#@title Rejim tablosu ve mevsimsellik
donemler = [(1977,1989),(1990,1999),(2000,2009),(2010,2019),(2020,2026)]
rows=[]
for a,b in donemler:
    seg = z[(z.index.year>=a)&(z.index.year<=b)]
    rows.append({"dönem":f"{a}–{b}", "ay":len(seg),
                 "ort. aylık %": float(np.expm1(seg.mean())*100),
                 "yıllıklandırılmış %": float(np.expm1(seg.mean()*12)*100),
                 "aylık std (log)": float(seg.std()),
                 "en yüksek ay %": float(np.expm1(seg.max())*100)})
display(pd.DataFrame(rows))

ay_ort = z.groupby(z.index.month).mean()
genel  = z.mean()
fig, ax = plt.subplots(1, 2, figsize=(13, 4))
(np.expm1(ay_ort)*100).plot(kind="bar", ax=ax[0], color="#1b3a6b")
ax[0].axhline(float(np.expm1(genel)*100), color="#c1440e", ls="--", label="genel ortalama")
ax[0].set_title("Takvim ayı ortalaması (tüm tarih) · aylık %"); ax[0].legend()
son = z[z.index.year>=2015]
(np.expm1(son.groupby(son.index.month).mean())*100).plot(kind="bar", ax=ax[1], color="#2e7d32")
ax[1].axhline(float(np.expm1(son.mean())*100), color="#c1440e", ls="--")
ax[1].set_title("Takvim ayı ortalaması (2015+) · aylık %")
for a in ax: a.grid(alpha=.3); a.set_xlabel("Ay")
plt.tight_layout(); plt.show()

from statsmodels.tsa.stattools import acf
lags = acf(z[z.index.year>=2005], nlags=24)
fig, ax = plt.subplots(figsize=(11,3.2))
ax.bar(range(len(lags)), lags, color="#1b3a6b"); ax.axhline(0, color="0.4", lw=.8)
ax.set_title("Log aylık değişimin otokorelasyonu (2005+) — 12. gecikmeye dikkat")
ax.grid(alpha=.3); plt.tight_layout(); plt.show()
""")

code(r"""
#@title Sepet madde fiyatları: kapsam ve yayılım
if bundle.items is not None:
    it = bundle.items
    dl = np.log(it.replace(0.0, np.nan)).diff().iloc[1:]
    dl = dl.replace([np.inf,-np.inf], np.nan)
    ozet = pd.DataFrame({
        "sepet_medyan_%": np.expm1(dl.median(axis=1))*100,
        "sepet_ortalama_%": np.expm1(dl.mean(axis=1))*100,
        "artan_kalem_payı": (dl>0).mean(axis=1),
    })
    ozet["resmî_TÜFE_%"] = m["aylikYuzde"].reindex(ozet.index)
    fig, ax = plt.subplots(2,1, figsize=(13,7), sharex=True)
    ozet[["sepet_medyan_%","sepet_ortalama_%","resmî_TÜFE_%"]].plot(ax=ax[0], lw=1.2)
    ax[0].set_title("Sepet özetleri ve resmî TÜFE (ağırlıksız — resmî TÜFE tahmini DEĞİLDİR) · %")
    ozet["artan_kalem_payı"].plot(ax=ax[1], color="#6a1b9a", lw=1.2)
    ax[1].set_title("Fiyatı artan kalem payı (yayılım göstergesi)")
    for a in ax: a.grid(alpha=.3)
    plt.tight_layout(); plt.show()
    k = ozet[["sepet_medyan_%","sepet_ortalama_%","resmî_TÜFE_%"]].corr().iloc[:,-1]
    print("Resmî TÜFE ile korelasyon:\n", k.to_string())
    print("\n⚠️  Geçerli tarihsel sepet ağırlıkları bulunmadığından ağırlıksız kalem "
          "ortalaması resmî TÜFE tahmini olarak SUNULMAZ; yalnızca yardımcı bilgidir.")
else:
    print("Sepet verisi alınamadı.")
""")

# ---------------------------------------------------------------- 5. TimesFM
md(r"""
---
## 5. TimesFM 3.0 — kurulum, ağırlık indirme ve doğrulama

Bu, defterin yerel ortama göre **asıl farkıdır**: Colab'de huggingface.co
erişilebilir olduğu için TimesFM 3.0 gerçekten çalıştırılabilir.

Doğrulanan resmî arayüz (`timesfm3/torch/timesfm3_forecaster.py`):

```python
from timesfm3 import TimesFM3Forecaster
f = TimesFM3Forecaster.from_pretrained("google/timesfm-3.0-pytorch", device="cuda")
out = list(f.predict_batch(contexts=[ctx], horizon=12,
                           return_quantiles=True, make_positive=False))
```

İki teknik ayrıntı önemlidir:

1. `TimesFM3Evaluator` alt sınıfı `make_positive=True` varsayılanıyla gelir ve
   **negatif değerleri kırpar**. Modelleme serimiz aylık *log değişim* olduğu ve
   deflasyon aylarında negatif olabildiği için `TimesFM3Forecaster` sınıfı
   `make_positive=False` ile kullanılır.
2. Modelin kuantil ızgarası 0,1–0,9'dur; **%95 aralığı desteklemez**. Ek yöntem
   olmadan bu modelden %95 aralık sunulmaz.
""")

code(r"""
#@title TimesFM 3.0'ı yükle ve doğrula
from src.models import timesfm_adapter as TFM

tfm_status = TFM.probe(cfg)
print("Kullanılabilir :", tfm_status.available)
print("Paket sürümü   :", tfm_status.package_version)
print("Kod içe aktarma:", tfm_status.code_import)
print("Ağırlık        :", tfm_status.weights_ref, "· revizyon:", tfm_status.weights_revision)
print("Cihaz          :", tfm_status.device)
print("Kuantil ızgara :", tfm_status.quantile_grid, "→ %95 destekli mi:", tfm_status.supports_95)
print("Kod lisansı    :", tfm_status.code_license)
print("Ağırlık lisansı:", tfm_status.weights_license)
print("\nAyrıntı:", tfm_status.detail)

if not tfm_status.available:
    print("\n⛔ TimesFM 3 ÇALIŞTIRILAMIYOR. Defterin geri kalanı çalışır, ancak "
          "karşılaştırma TAMAMLANMIŞ SAYILMAZ ve bu durum raporda belirtilir.")
    TIMESFM_CALISTIR = False
    cfg["timesfm"]["enabled"] = False
else:
    cfg["timesfm"]["device"] = tfm_status.device
    cfg["timesfm"]["hf_model"] = tfm_status.weights_local_path or cfg["timesfm"]["hf_model"]
""")

code(r"""
#@title TimesFM 3.0 tek başına: son 12 ayı gizle ve tahmin ettir (akıl sağlığı kontrolü)
if TIMESFM_CALISTIR:
    from src.transforms import to_pct
    kes = z.index[-13]                      # son 12 ayı gizle
    gecmis, gercek = z[z.index <= kes], z[z.index > kes]

    f = TFM.load_forecaster(cfg["timesfm"]["hf_model"], cfg["timesfm"]["device"])
    ctx = np.asarray(gecmis, dtype=np.float32)[-512:]
    out = list(f.predict_batch(contexts=[ctx], horizon=12,
                               return_quantiles=True, make_positive=False))[0]
    tahmin = np.asarray(out.forecast, float).reshape(-1)[:12]
    q = np.asarray(out.quantiles, float)[:12]      # (12, 9) → 0.1 … 0.9

    fig, ax = plt.subplots(figsize=(12,4.5))
    gec = z[z.index >= kes-35]
    ax.plot(gec.index.to_timestamp(), to_pct(gec.values), color="#1b3a6b", lw=1.6,
            label="Gerçekleşme")
    xf = gercek.index.to_timestamp()
    ax.plot(xf, to_pct(tahmin), color="#c1440e", lw=2, ls="--", marker="o", ms=4,
            label="TimesFM 3.0 (zero-shot)")
    ax.fill_between(xf, to_pct(q[:,0]), to_pct(q[:,8]), color="#c1440e", alpha=.15,
                    label="%80 aralık (model kuantilleri 0,1–0,9)")
    ax.axvline(kes.to_timestamp(), color="0.35", ls=":", lw=1.4)
    ax.set_title(f"TimesFM 3.0 akıl sağlığı kontrolü — bağlam {kes}'a kadar, 12 ay ileri\n"
                 f"ölçü: aylık % değişim · cihaz: {tfm_status.device}")
    ax.set_xlabel("Ay"); ax.set_ylabel("Aylık %"); ax.legend(fontsize=8); ax.grid(alpha=.3)
    plt.tight_layout(); plt.show()

    hata = to_pct(tahmin) - to_pct(gercek.values)
    print(f"Aylık MAE: {np.abs(hata).mean():.3f} puan · "
          f"12 ay bileşik tahmin: %{compound_pct(tahmin):.2f} · "
          f"gerçekleşen: %{compound_pct(gercek.values):.2f}")
    print("\nNot: bu tek bir başlangıçtır, model karşılaştırması DEĞİLDİR. "
          "Karşılaştırma 6. bölümdeki kayan başlangıçlı testle yapılır.")
else:
    print("TimesFM çalıştırılamadığı için atlandı.")
""")

# ---------------------------------------------------------------- 6. backtest
md(r"""
---
## 6. Geliştirme doğrulaması (kayan başlangıçlı geriye dönük test)

Her başlangıç `t` için: yalnızca `z[≤ t]` ile eğitilir/bağlam verilir, 12 ay
tahmin edilir, ve **yalnızca geliştirme sınırı (Ağustos 2024) içinde
gerçekleşmiş** hedefler puanlanır. Rastgele eğitim/test bölmesi yoktur.

TimesFM ince ayarsız kullanıldığı için her başlangıçta yeniden eğitim yoktur;
bu yüzden tüm başlangıçların bağlamları **tek seferde toplu** verilir. Sonuç tek
tek çalıştırmayla özdeştir, yalnızca çok daha hızlıdır.
""")

code(r"""
#@title Aday listesi
from src.registry import build_specs, SIMPLICITY_NOTE

specs = build_specs(cfg, items=bundle.items, include_timesfm=TIMESFM_CALISTIR)
tbl = pd.DataFrame([{
    "aday": s.key, "aile": s.family,
    "pencere": "tüm geçmiş" if s.window==0 else f"son {s.window} ay",
    "dönüşüm": s.transform, "basitlik": s.complexity_rank,
    "yardımcı veri": "evet" if s.uses_exog else "hayır",
    "min geçmiş (ay)": s.min_history} for s in specs])
display(tbl)
print(f"{len(specs)} aday yapılandırma")
print(SIMPLICITY_NOTE)
""")

code(r"""
#@title Geliştirme geriye dönük testini çalıştır  (HIZLI_MOD=False ise uzun sürer)
import time
from src import backtest as BT
from src.models import timesfm_adapter as TFM

H = int(cfg["horizon"])
dev_end = pd.Period(cfg["split"]["dev_end"], freq="M")
o0 = pd.Period(cfg["split"]["dev_origin_start"], freq="M")
origins = [p for p in z.index if o0 <= p <= dev_end]
if HIZLI_MOD:
    origins = origins[-int(SON_N_BASLANGIC):]
print(f"{len(specs)} aday × {len(origins)} başlangıç "
      f"({origins[0]} → {origins[-1]})")

batchable = [s for s in specs if s.meta.get("batch_capable")]
rest      = [s for s in specs if not s.meta.get("batch_capable")]

t0 = time.time()
dev_paths, dev_fail = BT.run_backtest(z, rest, origins, H, log=print)
for sp in batchable:
    bp = TFM.batch_backtest_paths(cfg, z, origins, H,
                                  int(sp.meta["context_length"]), sp.key,
                                  int(cfg["timesfm"].get("batch_size", 64)), log=print)
    if not bp.empty:
        dev_paths = pd.concat([dev_paths, bp], ignore_index=True)
        print(f"  {sp.key}: {bp['origin'].nunique()} başlangıç (toplu çıkarım)")
dev_paths["origin"] = pd.PeriodIndex(dev_paths["origin"].astype(str), freq="M")
dev_sure = time.time()-t0
print(f"\nSüre: {dev_sure/60:.1f} dk · üretilen yol: {len(dev_paths)//H}")
if len(dev_fail): display(dev_fail.groupby(["model","sebep"]).size().reset_index(name="adet"))
""")

code(r"""
#@title Birleşimleri ekle ve hedefleri puanla
YEM = tuple(cfg["targets"]["yearend_origin_months"])

def puanla(paths, score_end):
    orgs = sorted(pd.PeriodIndex(paths["origin"].astype(str), freq="M").unique())
    gercek = BT.realized_frame(z, list(orgs), H, score_end, YEM)
    tahmin = BT.predicted_frame(z, paths, H, YEM)
    return BT.score_frame(tahmin, gercek)

from src import selection as SEL
dev_scored = puanla(dev_paths, dev_end)

# Birleşim üyeleri: geliştirme skorlarına göre FARKLI ailelerden en iyi 3
aile = {s.key: s.family for s in specs}
taban = SEL.selection_scores(BT.scored_for_selection(dev_scored, len(YEM)),
                             cfg["selection"]["weights"], 1)
gorulen, uyeler = set(), []
for _, rw in taban[taban["uygun"]].sort_values("S").iterrows():
    fam = aile.get(rw["model"], "?")
    if fam in gorulen: continue
    gorulen.add(fam); uyeler.append(rw["model"])
    if len(uyeler) >= cfg["selection"]["ensemble"]["top_k"]: break
print("Birleşim üyeleri (aylık LOG DEĞİŞİM ölçeğinde birleştirilir):", uyeler)

for yont in cfg["selection"]["ensemble"]["methods"]:
    ep = BT.ensemble_paths(dev_paths, uyeler, f"BIRLESIM_{yont}_{len(uyeler)}", yont)
    if not ep.empty: dev_paths = pd.concat([dev_paths, ep], ignore_index=True)
dev_scored = puanla(dev_paths, dev_end)
print("puanlanan gözlem:", len(dev_scored))
""")

# ---------------------------------------------------------------- 7. seçim
md(r"""
---
## 7. Model seçimi ve seçimin dondurulması

Skor **yalnızca** geliştirme verisinden hesaplanır ve tüm adaylar için **ortak
başlangıçlarda** karşılaştırılır (daha az veya daha kolay dönem üzerinde çalışan
model avantajlı gösterilmez). Yılsonu bileşeni yalnızca üç başlangıcı da
(Haziran/Ağustos/Ekim sonu) değerlendirilebilen **tam yıllardan** gelir.
""")

code(r"""
#@title Geliştirme sıralaması (Tablo 3)
sec_scored = BT.scored_for_selection(dev_scored, len(YEM))
den = BT.mase_denominators(dev_scored, "naive_mevsimsel_12",
                           cfg["backtest"]["mase"]["min_denominator_obs"])
ozet_dev = SEL.summarize(dev_scored, den)

scores = SEL.selection_scores(sec_scored, cfg["selection"]["weights"],
                              cfg["selection"]["min_common_origins"] if not HIZLI_MOD else 3)
goster = scores[["sira","model","S","MAE_yearend","n_yearend","MAE_c6","n_c6",
                 "MAE_c12","n_c12","uygun"]]
display(goster.style.background_gradient(subset=["S"], cmap="RdYlGn_r"))

en_iyi = float(scores["S"].min())
esik = en_iyi*(1+cfg["selection"]["tie_relative_threshold"])
print(f"En iyi S = {en_iyi:.4f} · %2 beraberlik eşiği ≤ {esik:.4f}")
print("Berabere sayılan adaylar:", scores[scores['S']<=esik]['model'].tolist())
""")

code(r"""
#@title Kazananı belirle ve SEÇİMİ DONDUR
import json
rt = dev_paths.groupby("model")["runtime_sec"].mean().to_dict()
meta = {s.key: {"family": s.family, "complexity_rank": s.complexity_rank} for s in specs}
for mk in dev_scored["model"].unique():
    if mk.startswith("BIRLESIM"): meta[mk] = {"family":"ensemble","complexity_rank":9}

sel = SEL.choose(scores, meta, cfg, rt, ensemble_members=uyeler)
spec_map = {s.key: s for s in specs}
ws = spec_map.get(sel.winner)

print("SEÇİLEN :", sel.winner)
print("Skor S  :", round(sel.score,4), "yüzde puan")
print("Kural   :", sel.rule)
print("Berabere:", sel.tied_with)
print("Alternatifler:", sel.alternatives)
print("Pencere :", ("üye modellerin kendi pencereleri" if ws is None else
                    ("tüm geçmiş" if ws.window==0 else f"son {ws.window} ay")))

frozen_extra = {
    "kazanan_yapilandirma": {
        "model": sel.winner,
        "aile": ws.family if ws else "ensemble",
        "pencere": ("üye modellerin kendi pencereleri" if ws is None else
                    ("tüm geçmiş" if ws.window==0 else f"son {ws.window} ay")),
        "pencere_ay": (ws.window if ws else None),
        "donusum": ws.transform if ws else "log"},
    "alternatifler": sel.alternatives,
    "birlesim": {"uyeler": uyeler, "olcek": cfg["selection"]["ensemble"]["scale"],
                 "yontemler": cfg["selection"]["ensemble"]["methods"]},
    "kalibrasyon": cfg["calibration"], "mase": cfg["backtest"]["mase"],
    "aday_listesi": [s.key for s in specs],
    "timesfm_durumu": tfm_status.dict(),
    "colab": {"hizli_mod": HIZLI_MOD, "n_baslangic": len(origins),
              "donanim": info},
}
fpath = out_dir(cfg, "selection")/"frozen_selection.json"
SEL.freeze(sel, fpath, frozen_extra)
kaz, alts = sel.winner, sel.alternatives      # sonraki bölümlerde kullanılır
print("\n🔒 Dondurulmuş seçim yazıldı:", fpath)
print("   Nihai holdout bu ana kadar HİÇ kullanılmadı.")
""")

code(r"""
#@title Alt dönem dayanıklılığı (ağırlıklar DEĞİŞTİRİLMEZ)
_alt_donem = []
for sp in cfg["split"]["subperiods"]:
    a,b = pd.Period(sp["start"],"M"), pd.Period(sp["end"],"M")
    alt = sec_scored[(sec_scored["target_end"]>=a)&(sec_scored["target_end"]<=b)]
    if alt.empty: continue
    sc = SEL.selection_scores(alt, cfg["selection"]["weights"], 1)
    sc["alt_donem"] = sp["name"]; _alt_donem.append(sc)
    print(f"\n=== {sp['name']} ===")
    display(sc[["sira","model","S","MAE_yearend","n_yearend","MAE_c6","MAE_c12"]].head(8))
if _alt_donem:
    pd.concat(_alt_donem).to_csv(out_dir(cfg,"tables")/"03c_alt_donem_siralamasi.csv",
                                 index=False, encoding="utf-8-sig")
print("\nBu kesitler yalnızca dayanıklılığı açıklamak içindir; "
      "sonuçlara bakılarak ağırlık değiştirilmemiştir.")
""")

# ---------------------------------------------------------------- 8. holdout
md(r"""
---
## 8. Nihai holdout testi

Ağustos 2024 başlangıcından itibaren ay ay ilerlenir. Önceki test ayları sonraki
başlangıçların eğitiminde kullanılabilir; **ancak test skorlarına bakılarak ayar
veya model seçimi değiştirilemez.**

> 24 aylık testte yalnızca **iki tamamlanmış yılsonu** bulunur. Yılsonu üstünlüğü
> bu testle yüksek kesinlikle kanıtlanamaz.
""")

code(r"""
#@title Nihai testi çalıştır (dondurulmuş seçim dosyası ZORUNLU)
frozen = SEL.load_frozen(fpath)      # dosya yoksa hata verir — kapı budur
print("Dondurulmuş seçim:", frozen["winner"], "·", frozen["frozen_at"], "\n")

t_o0  = pd.Period(cfg["split"]["holdout_start_origin"], freq="M")
t_end = pd.Period(cfg["split"]["holdout_end"], freq="M")
t_orgs = [p for p in z.index if t_o0 <= p <= t_end]
print(f"{len(specs)} aday × {len(t_orgs)} başlangıç ({t_orgs[0]} → {t_orgs[-1]})")

t0=time.time()
test_paths, test_fail = BT.run_backtest(z, rest, t_orgs, H, log=print)
for sp in batchable:
    bp = TFM.batch_backtest_paths(cfg, z, t_orgs, H, int(sp.meta["context_length"]),
                                  sp.key, int(cfg["timesfm"].get("batch_size",64)), log=print)
    if not bp.empty: test_paths = pd.concat([test_paths, bp], ignore_index=True)
test_paths["origin"] = pd.PeriodIndex(test_paths["origin"].astype(str), freq="M")
for yont in cfg["selection"]["ensemble"]["methods"]:
    ep = BT.ensemble_paths(test_paths, frozen["frozen_extra"]["birlesim"]["uyeler"],
                           f"BIRLESIM_{yont}_{len(uyeler)}", yont)
    if not ep.empty: test_paths = pd.concat([test_paths, ep], ignore_index=True)
test_scored = puanla(test_paths, t_end)
print(f"\nSüre: {(time.time()-t0)/60:.1f} dk")
""")

code(r"""
#@title Nihai test sonuçları (yalnızca DENETİM)
birlesik = pd.concat([dev_scored, test_scored], ignore_index=True)
t_den = BT.mase_denominators(birlesik, "naive_mevsimsel_12",
                             cfg["backtest"]["mase"]["min_denominator_obs"])
t_den = t_den[t_den["origin"].isin(test_scored["origin"].unique())]
ozet_test = SEL.summarize(test_scored, t_den)

for hedef, baslik in (("yearend","YILSONU (Ara/Ara)"),
                      ("c6","İLERİ 6 AY BİLEŞİK"),
                      ("c12","İLERİ 12 AY BİLEŞİK")):
    print(f"\n=== {baslik} ===")
    display(ozet_test[ozet_test["hedef"]==hedef]
            [["model","n","MAE","RMSE","ME","MASE","en_kotu_hata","en_kotu_donem"]]
            .sort_values("MAE").head(10))

print("\n⚠️  Nihai test tablosu performansı yalnızca DENETLER. "
      "Test kazananına bakılarak seçilmiş model DEĞİŞTİRİLMEZ.\n"
      "⚠️  Mevsimsel-naive'in test MASE'si tanım gereği 1 değildir; "
      "MASE<1 ile testte referansı yenmek aynı iddia değildir.")
""")

code(r"""
#@title Geliştirme ↔ nihai test tutarlılığı
w = cfg["selection"]["weights"]
def skorla(oz):
    out={}
    for mdl,g in oz.groupby("model"):
        s,ok=0.,True
        for t,k in (("yearend","yearend"),("c6","c6"),("c12","c12")):
            rr=g[g["hedef"]==t]
            if rr.empty or not np.isfinite(rr["MAE"].iloc[0]): ok=False;break
            s+=w[k]*float(rr["MAE"].iloc[0])
        if ok: out[mdl]=s
    return out
sd, st = skorla(ozet_dev), skorla(ozet_test)
ortak = sorted(set(sd)&set(st))
fig, ax = plt.subplots(figsize=(8,7))
ax.scatter([sd[k] for k in ortak], [st[k] for k in ortak], s=55, color="#1b3a6b")
for k in ortak:
    ax.annotate(k, (sd[k], st[k]), fontsize=6.5, xytext=(4,3), textcoords="offset points")
lim=[0, max(max(sd.values()), max(st.values()))*1.1]
ax.plot(lim,lim,ls=":",color="0.5"); ax.set_xlim(lim); ax.set_ylim(lim)
ax.set_xlabel("Geliştirme S"); ax.set_ylabel("Nihai test S")
ax.set_title("Geliştirme ve nihai test skorları (düşük daha iyi)\n"
             "S = 0,60·MAE_yılsonu + 0,30·MAE_6ay + 0,10·MAE_12ay · yüzde puan")
ax.grid(alpha=.3); plt.tight_layout(); plt.show()

sr = pd.Series(sd).rank().to_frame("gelistirme_sira").join(
     pd.Series(st).rank().to_frame("test_sira")).dropna()
print("Sıralama korelasyonu (Spearman):", round(sr.corr(method='spearman').iloc[0,1], 3))
print("Düşük korelasyon, tek bir 24 aylık pencerede sıralamanın ne kadar "
      "oynak olabildiğini gösterir — seçim yine de değiştirilmez.")
""")

code(r"""
#@title Model farkları: blok bootstrap (yıl blokları) + Diebold–Mariano
from src import metrics as MX
kaz = frozen["winner"]; alts = frozen["frozen_extra"]["alternatifler"]
dm_rows=[]
for hedef in ("yearend","c6","c12"):
    A = test_scored[(test_scored["model"]==kaz)&(test_scored["target"]==hedef)]
    for other in ["naive_mevsimsel_12"]+list(alts):
        if other==kaz: continue
        B = test_scored[(test_scored["model"]==other)&(test_scored["target"]==hedef)]
        mg = A.merge(B, on="origin", suffixes=("_a","_b"))
        if mg.empty: continue
        blok = pd.PeriodIndex(mg["target_end_a"], freq="M").year
        bs = MX.block_bootstrap_diff(mg["err_a"].to_numpy(), mg["err_b"].to_numpy(),
                                     np.asarray(blok), cfg["bootstrap"]["n_boot"], SEED)
        dm = MX.diebold_mariano(mg["err_a"].to_numpy(), mg["err_b"].to_numpy(),
                                h=6 if hedef=="c6" else 12)
        dm_rows.append({"hedef":hedef,"A":kaz,"B":other,"MAE farkı (A−B)":bs["diff"],
                        "boot %95 alt":bs["lo95"],"boot %95 üst":bs["hi95"],
                        "n":bs["n"],"blok(yıl)":bs.get("n_blocks",0),
                        "DM":dm["dm"],"DM p":dm["p"],"not":dm["note"]})
display(pd.DataFrame(dm_rows))
print("Negatif fark = A daha iyi. Aralık 0'ı içeriyorsa fark ayırt edilememiştir.\n"
      "Diebold–Mariano DESTEKLEYİCİDİR: anlamsız sonuç eşdeğerlik kanıtı değildir; "
      "az örnek ve çoklu karşılaştırma sınırları geçerlidir.")
""")

# ---------------------------------------------------------------- 9. aralık
md(r"""
---
## 9. Belirsizlik aralıkları

Aralıklar **doğrudan ilgili dönem hedefinin** geçmiş hatalarından üretilir
(conformal, mutlak hata kuantili); aylık alt/üst sınırlar çarpılarak kümülatif
aralık **oluşturulmaz** — böylece zamansal bağımlılık korunur.

Zaman kuralı: `t` başlangıcında yalnızca hedefi `t`'ye kadar **açıklanmış** eski
hatalar kalibrasyona girer.
""")

code(r"""
#@title Kapsama, genişlik ve skorlar
from src import calibration as CAL
cal_all = CAL.calibrate(birlesik, kaz, cfg)
raporlar=[]
for etiket, df in (("geliştirme", dev_scored), ("nihai test", test_scored)):
    alt = cal_all[cal_all["origin"].isin(df["origin"].unique())]
    if alt.empty: continue
    rp = CAL.coverage_report(alt, cfg); rp.insert(0,"aşama",etiket); raporlar.append(rp)
cov = pd.concat(raporlar, ignore_index=True)
display(cov[cov["hedef"].isin(["yearend","c6","c12","m1","m6","m12"])])
print("Yüksek kapsama + çok geniş aralık = iyi kalibrasyon DEĞİL, aşırı genişlik "
      "işaretidir. Gözlem sayıları her satırda verilmiştir; keyfî tek bir "
      "geçer/kalır bandı kullanılmamıştır.\n"
      "Conformal yaklaşım rejim değişiminde otomatik geçerli kapsama GARANTİ ETMEZ.")
""")

# ---------------------------------------------------------------- 10. tahmin
md(r"""
---
## 10. Nihai tahmin: Eylül 2026 – Ağustos 2027

Geliştirmede seçilmiş yapılandırma, veri kesimine kadar yeniden eğitilir.
**Seçilmiş eğitim penceresi korunur** (son 60 ay kazandıysa tüm geçmişe geçilmez).
""")

code(r"""
#@title Yeniden eğit ve 12 aylık yolu üret
from src import forecast as FC
cutoff = pd.Period(cfg["data"]["cutoff"], freq="M")

def yol_uret(anahtar):
    if anahtar.startswith("BIRLESIM"):
        yont = anahtar.split("_")[1]
        mats = [FC.fit_final(spec_map[u], z, H)[0]
                for u in frozen["frozen_extra"]["birlesim"]["uyeler"]]
        arr = np.vstack(mats)
        return arr.mean(axis=0) if yont=="mean" else np.median(arr, axis=0)
    return FC.fit_final(spec_map[anahtar], z, H)[0]

z_path = yol_uret(kaz)
tablo  = FC.build_forecast_table(z, z_path, cutoff, bundle.monthly, kaz)
ozetler= FC.period_summaries(z, z_path, cutoff, bundle.monthly)

preds = {rw["target"]: rw["pred"] for _, rw in BT.predicted_frame(
    z, pd.DataFrame({"origin":[cutoff]*H,"model":[kaz]*H,
                     "h":range(1,H+1),"z_pred":z_path}), H, (cutoff.month,)).iterrows()}
preds["yearend"] = float(ozetler[ozetler["olcu"].str.contains("yılsonu")]["deger_pct"].iloc[0])
iv = CAL.forward_intervals(birlesik, kaz, cfg, preds, cutoff)

ivm = iv.set_index("target")
for i in range(H):
    k=f"m{i+1}"
    for lv in (80,95):
        tablo.loc[i,f"aylik_lo{lv}"] = ivm.at[k,f"lo{lv}"] if k in ivm.index else np.nan
        tablo.loc[i,f"aylik_hi{lv}"] = ivm.at[k,f"hi{lv}"] if k in ivm.index else np.nan

print(f"Model: {kaz} · veri kesimi {cutoff} · tahmin {cutoff+1} – {cutoff+H}\n")
display(tablo[["tarih","aylik_pct","yillik_pct","ytd_pct","ytd_kaynak",
               f"kumulatif_{cutoff}_sonrasi_pct","aylik_lo80","aylik_hi80",
               "aylik_lo95","aylik_hi95"]])
print("Aralıklar AYLIK yüzde değişim ölçüsündedir; dönem (bileşik) aralıkları aşağıdadır.")
""")

code(r"""
#@title Dönem özetleri — ölçüler birbirinden AYRI
display(ozetler[["olcu","donem","deger_pct","tanim"]])
print()
display(iv[iv["target"].isin(["yearend","c6","c12"])]
        [["target","pred","n_cal","lo80","hi80","lo95","hi95","yontem95"]])
print("\n'Gelecek 6 ayın bileşik enflasyonu', '6 ay sonra yıllık enflasyon' ve "
      "'takvim yarıyılı enflasyonu' FARKLI büyüklüklerdir.\n"
      f"{cutoff} sonrasından bakıldığında yılsonu hedefi 4 ay sonrasıdır.")
""")

code(r"""
#@title Ana model ve iki alternatifin karşılaştırması
tablolar = {kaz: tablo}
karsi = [ozetler.assign(rol="ana", model=kaz)]
for i,a in enumerate(alts[:2]):
    try:
        zp = yol_uret(a)
    except Exception as e:
        print(f"{a}: üretilemedi ({e})"); continue
    at = FC.build_forecast_table(z, zp, cutoff, bundle.monthly, a)
    tablolar[a] = at
    slug = "".join(ch if ch.isalnum() else "_" for ch in a).strip("_")[:60]
    at.to_csv(out_dir(cfg,"tables")/f"06_aylik_tahminler_{slug}.csv",
              index=False, encoding="utf-8-sig")
    karsi.append(FC.period_summaries(z, zp, cutoff, bundle.monthly)
                 .assign(rol=f"alternatif{i+1}", model=a))
kt = pd.concat(karsi, ignore_index=True)
display(kt.pivot_table(index=["olcu","donem"], columns="model",
                       values="deger_pct", sort=False))
""")

# ---------------------------------------------------------------- 11. grafik
md(r"""
---
## 11. Grafikler ve Türkçe rapor
""")

code(r"""
#@title Tahmin grafikleri
from src.transforms import to_pct
fx = pd.PeriodIndex(tablo["tarih"], freq="M")
kcol = [c for c in tablo.columns if c.startswith("kumulatif_")][0]

fig, ax = plt.subplots(3,1, figsize=(13,13))

h5 = m["aylikYuzde"][m["aylikYuzde"].index >= cutoff-59]
ax[0].plot(h5.index.to_timestamp(), h5.values, color="#1b3a6b", lw=1.7, label="Gerçekleşme")
ax[0].plot([cutoff.to_timestamp()]+list(fx.to_timestamp()),
           [float(m.loc[cutoff,"aylikYuzde"])]+list(tablo["aylik_pct"]),
           color="#c1440e", lw=2, ls="--", marker="o", ms=4, label="Tahmin")
if tablo["aylik_lo80"].notna().any():
    ax[0].fill_between(fx.to_timestamp(), tablo["aylik_lo80"], tablo["aylik_hi80"],
                       color="#c1440e", alpha=.18, label="%80 (aylık ölçü)")
    ax[0].fill_between(fx.to_timestamp(), tablo["aylik_lo95"], tablo["aylik_hi95"],
                       color="#c1440e", alpha=.09, label="%95 (aylık ölçü)")
ax[0].set_title(f"Son 5 yıl aylık enflasyon ve 12 aylık tahmin\nveri kesimi: {cutoff} · ölçü: aylık % (yüzde puan)")
ax[0].set_ylabel("Aylık %"); ax[0].legend(fontsize=8, ncol=2)

yy = m["yillikYuzde"].dropna(); yy = yy[yy.index >= cutoff-71]
ax[1].plot(yy.index.to_timestamp(), yy.values, color="#1b3a6b", lw=1.7, label="Gerçekleşme")
ax[1].plot([cutoff.to_timestamp()]+list(fx.to_timestamp()),
           [float(yy.loc[cutoff])]+list(tablo["yillik_pct"]),
           color="#c1440e", lw=2, ls="--", marker="o", ms=4, label="Tahmin")
ax[1].set_title(f"Yıllık enflasyon ve tahmin\nveri kesimi: {cutoff} · ölçü: 12 aylık % (yüzde puan)")
ax[1].set_ylabel("Yıllık %"); ax[1].legend(fontsize=8)

for (nm,t),c in zip(tablolar.items(), ["#c1440e","#2e7d32","#6a1b9a"]):
    kc=[k for k in t.columns if k.startswith("kumulatif_")][0]
    ax[2].plot(pd.PeriodIndex(t["tarih"],freq="M").to_timestamp(), t[kc],
               lw=1.9, marker="o", ms=3.5, label=nm, color=c)
ax[2].set_title(f"{cutoff} sonrası KÜMÜLATİF (bileşik) tahmin yolu — ana model ve alternatifler\n"
                f"ölçü: bileşik % değişim (yüzde puan)")
ax[2].set_ylabel(f"{cutoff}'a göre bileşik %"); ax[2].set_xlabel("Ay"); ax[2].legend(fontsize=8)

for a in ax:
    a.axvline(cutoff.to_timestamp(), color="0.35", ls=":", lw=1.4); a.grid(alpha=.3)
plt.tight_layout(); plt.show()
""")

code(r"""
#@title Model × hedef hata ısı haritası (geliştirme ve nihai test)
for etiket, sc in (("geliştirme", dev_scored), ("nihai test", test_scored)):
    tut = ["yearend","c6","c12","m1","m3","m6","m12"]
    piv = (sc[sc["target"].isin(tut)].groupby(["model","target"])["err"]
           .apply(lambda s: s.abs().mean()).unstack())
    piv = piv.reindex(columns=[c for c in tut if c in piv.columns])
    piv = piv.loc[piv.mean(axis=1).sort_values().index]
    fig, ax = plt.subplots(figsize=(1.1*len(piv.columns)+4, .36*len(piv)+2.4))
    im = ax.imshow(piv.values, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(piv.columns)), piv.columns)
    ax.set_yticks(range(len(piv.index)), piv.index, fontsize=7)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            v=piv.values[i,j]
            if np.isfinite(v):
                ax.text(j,i,f"{v:.1f}",ha="center",va="center",fontsize=6.5,
                        color="black" if v<np.nanmax(piv.values)*.6 else "white")
    fig.colorbar(im, ax=ax, label="MAE (yüzde puan)")
    ax.set_title(f"Model × hedef MAE — {etiket} · veri kesimi {cutoff}"); ax.grid(False)
    plt.tight_layout(); plt.show()
""")

code(r"""
#@title Tabloları, grafikleri ve Türkçe raporu üret
from src import plots, report

tdir = out_dir(cfg, "tables")
audit.to_csv(tdir/"01_veri_denetimi.csv", index=False, encoding="utf-8-sig")
pd.DataFrame([{"alan":"Ana seri",
               "kapsam":f"{bundle.monthly.index.min()} – {bundle.monthly.index.max()}",
               "kayit":len(bundle.monthly),"kaynak":bundle.provenance},
              {"alan":"Sepet madde fiyatları",
               "kapsam":(f"{bundle.items.index.min()} – {bundle.items.index.max()}"
                         if bundle.items is not None else "yok"),
               "kayit":(f"{bundle.items.shape[1]} kalem × {bundle.items.shape[0]} ay"
                        if bundle.items is not None else 0),
               "kaynak":bundle.provenance}]).to_csv(
    tdir/"01_veri_kapsami.csv", index=False, encoding="utf-8-sig")
tbl.rename(columns={"aday":"aday","aile":"aile","pencere":"pencere",
                    "dönüşüm":"donusum","basitlik":"basitlik_sirasi"}).to_csv(
    tdir/"02_aday_yapilandirmalar.csv", index=False, encoding="utf-8-sig")
ozet_dev.to_csv(tdir/"03a_gelistirme_ozet.csv", index=False, encoding="utf-8-sig")
scores.to_csv(tdir/"03b_gelistirme_siralamasi.csv", index=False, encoding="utf-8-sig")
ozet_test.to_csv(tdir/"03d_nihai_test_ozet.csv", index=False, encoding="utf-8-sig")
tablo.to_csv(tdir/"06_aylik_tahminler.csv", index=False, encoding="utf-8-sig")
ozetler.to_csv(tdir/"07_donem_ozetleri.csv", index=False, encoding="utf-8-sig")
iv.to_csv(tdir/"07b_nihai_tahmin_araliklari.csv", index=False, encoding="utf-8-sig")
kt.to_csv(tdir/"08_model_karsilastirmasi.csv", index=False, encoding="utf-8-sig")
cov.rename(columns={"aşama":"asama"}).to_csv(
    tdir/"09_aralik_kapsamasi.csv", index=False, encoding="utf-8-sig")
for nm, df in (("dev", dev_fail), ("test", test_fail)):
    d = df if (df is not None and len(df)) else pd.DataFrame(
        columns=["origin","model","sebep","ayrinti"])
    d.to_csv(tdir/f"10_basarisiz_denemeler_{nm}.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(dm_rows).to_csv(tdir/"11_bootstrap_karsilastirma.csv",
                             index=False, encoding="utf-8-sig")
rt_tbl = (dev_paths.groupby("model")["runtime_sec"]
          .agg(["count","mean","median","max","sum"]).reset_index())
rt_tbl.columns = ["model","n_baslangic","ort_sn_baslangic","medyan_sn","en_uzun_sn","toplam_sn"]
rt_tbl["asama"]="geliştirme (Colab)"
rt_tbl.to_csv(tdir/"12_calisma_suresi_bellek.csv", index=False, encoding="utf-8-sig")

dev_scored.to_parquet(out_dir(cfg)/"dev_scored.parquet")
test_scored.to_parquet(out_dir(cfg)/"test_scored.parquet")
dev_paths.to_parquet(out_dir(cfg)/"dev_paths.parquet")
test_paths.to_parquet(out_dir(cfg)/"test_paths.parquet")

def _paket_surumleri():
    import importlib.metadata as _md
    out = {}
    for _p in ("numpy","pandas","scipy","scikit-learn","statsmodels","lightgbm",
               "matplotlib","pyarrow","torch","timesfm"):
        try: out[_p] = _md.version(_p)
        except Exception: out[_p] = None
    return out

payload = {"veri_kesimi":str(cutoff),"model":kaz,
           "tahmin_donemi":f"{cutoff+1} – {cutoff+H}",
           "ortam":"Google Colab", "donanim":info,
           "aylik_tahminler":json.loads(tablo.to_json(orient="records")),
           "donem_ozetleri":json.loads(ozetler.to_json(orient="records")),
           "araliklar":json.loads(iv.to_json(orient="records")),
           "timesfm_durumu":tfm_status.dict(),
           "secim":{k:frozen[k] for k in ("winner","score","rule","weights","frozen_at")}}
(out_dir(cfg,"forecast")/"nihai_tahmin.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
FC.archive(payload, out_dir(cfg,"forecast","arsiv"))

man = {"asama":"colab","zaman_utc":pd.Timestamp.utcnow().isoformat(),"seed":SEED,
       "model":kaz,"veri_kesimi":str(cutoff),
       "tahmin_donemi":f"{cutoff+1} – {cutoff+H}",
       "paket_surumleri":_paket_surumleri(),
       "determinizm_notu":("Sabit seed kullanılmıştır. GPU/BLAS iş parçacığı "
                           "farklılıkları nedeniyle son basamak düzeyinde tam "
                           "determinizm garanti edilmez."),
       "donanim":info,"timesfm_durumu":tfm_status.dict(),
       "hizli_mod":HIZLI_MOD,"n_dev_baslangic":len(origins),
       "n_test_baslangic":len(t_orgs),"dev_sure_sn":round(dev_sure,1),
       "config":{k:v for k,v in cfg.items() if not k.startswith("_")}}
(out_dir(cfg)/"manifest_forecast.json").write_text(
    json.dumps(man, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
(out_dir(cfg)/"manifest_data.json").write_text(
    json.dumps({**man, "timesfm_durumu":tfm_status.dict(),
                "veri_kaynaklari":[s.dict() for s in bundle.sources]},
               ensure_ascii=False, indent=2, default=str), encoding="utf-8")

plots.make_all(cfg)
yollar = report.build(cfg)
print("Üretilen:", *[str(p) for p in yollar], sep="\n  ")
""")

code(r"""
#@title Raporu defterin içinde göster
from IPython.display import HTML, display
display(HTML((out_dir(cfg)/"rapor.html").read_text(encoding="utf-8")))
""")

# ---------------------------------------------------------------- 12. sonuç
md(r"""
---
## 12. Araştırma vs. üretim: lisans ayrımı
""")

code(r"""
#@title Araştırmada ve üretimde en başarılı modeller
ARASTIRMA_DISI_URETIM = {"foundation", "foundation_aux"}   # TimesFM 3.0 ağırlık lisansı
uygun = scores[scores["uygun"]].copy()
uygun["aile"] = uygun["model"].map(lambda k: meta.get(k,{}).get("family","?"))

ar = uygun.sort_values("S").iloc[0]
ur = uygun[~uygun["aile"].isin(ARASTIRMA_DISI_URETIM)].sort_values("S").iloc[0]

print("ARAŞTIRMADA en başarılı (tüm adaylar, geliştirme skoru):")
print(f"   {ar['model']}  ·  S = {ar['S']:.4f} yüzde puan  ·  aile: {ar['aile']}")
print("\nÜRETİMDE kullanılabilecek en başarılı (izin verici lisanslı adaylar):")
print(f"   {ur['model']}  ·  S = {ur['S']:.4f} yüzde puan  ·  aile: {ur['aile']}")
if ar["model"] != ur["model"]:
    print(f"\n   Fark: {ar['S']-ur['S']:+.4f} puan "
          f"(%{100*(ur['S']-ar['S'])/ar['S']:+.1f} göreli)")
else:
    print("\n   Aynı model — lisans kısıtı seçimi değiştirmiyor.")

print()
print("Gerekçe")
print("-------")
print("TimesFM kaynak kodu Apache-2.0'dir ve 2.5'e kadarki agirliklar da Apache-2.0'dir.")
print("Ancak TimesFM 3.0 ON EGITIMLI AGIRLIKLARI ayri bir")
print("'timesfm-non-commercial-license-v1.0' lisansi altindadir ve ticari/uretim")
print("kullanimina KAPALIDIR (resmi depo README'si). Diger tum adaylar (statsmodels,")
print("scikit-learn, LightGBM) izin verici lisanslidir.")
print()
print("TimesFM 3.0 bu calistirmada:",
      "CALISTIRILDI" if TIMESFM_CALISTIR else "CALISTIRILAMADI")
print("Uretime dagitim bu gorevin kapsami disindadir.")
""")

code(r"""
#@title Testleri çalıştır (sızıntı, formüller, seçim kuralı)
import subprocess, sys
r = subprocess.run(f"{sys.executable} -m pytest tests -q", shell=True,
                   capture_output=True, text=True)
print(r.stdout[-3000:] or r.stderr[-3000:])
""")

code(r"""
#@title Bütün çıktıları ZIP olarak indir
import shutil
zip_path = shutil.make_archive("/content/kktc_tufe_ciktilar", "zip",
                               root_dir=str(out_dir(cfg)))
print("ZIP:", zip_path, f"({os.path.getsize(zip_path)/1e6:.1f} MB)")
try:
    from google.colab import files
    files.download(zip_path)
except Exception as e:
    print("Colab dışı ortam; dosyayı elle indirin.", e)
""")

md(r"""
---
## Sonuç ve sınırlar

**Ne yapıldı.** Aday modeller (5 zorunlu referans, ETS, sınırlı ızgaralı SARIMA,
AutoTheta, UCM, Ridge/ElasticNet/LightGBM, sepet destekli varyantlar ve
TimesFM 3.0) kayan başlangıçlı, sızıntısız bir protokolde karşılaştırıldı;
kazanan önceden sabitlenmiş bir skorla **yalnızca geliştirme verisinden**
seçildi, seçim donduruldu ve ancak ondan sonra nihai holdout açıldı.

**Bilinmesi gerekenler.**

* Geçmiş veri sürümleri (vintage) bulunmadığından bu, *son veri sürümüyle geriye
  dönük test*tir; o tarihte yapılmış canlı tahmin değildir. TimesFM'in ön
  eğitiminde bu değerlendirme dönemlerinin bulunup bulunmadığı doğrulanamamaktadır.
* 24 aylık nihai testte yalnızca **iki tamamlanmış yılsonu** vardır; yılsonu
  üstünlüğü yüksek kesinlikle kanıtlanamaz.
* Birleşim üyeleri geliştirme skorlarına bakılarak seçildiği için birleşimin
  *geliştirme* skoru bu açıdan iyimserdir; üyeler nihai testten önce dondurulmuştur.
* Conformal aralıklar simetriktir ve rejim değişiminde geçerli kapsama garanti
  etmez; yüksek kapsama, aralığın aşırı geniş olduğunun işareti olabilir.
* Bu defterden sonra yapılacak geliştirmeler aynı dönemi yeniden bağımsız test
  hâline **getirmez**; yeni denemeler keşifsel olarak etiketlenmelidir.
* **"En iyi model"**, bu veri ve önceden tanımlanan değerlendirmede en başarılı
  aday anlamındadır; gelecekte en az hatayı yapacağına dair garanti değildir.

**Tekrarlanabilirlik.** Sabit seed kullanılır; GPU/BLAS iş parçacığı farklılıkları
nedeniyle son basamak düzeyinde tam determinizm garanti edilmez. Çalıştırmanın
ayarları, veri özeti, paket sürümleri, donanımı ve süresi
`artifacts/manifest_*.json` içinde kayıtlıdır.
""")

nb = {
    "cells": cells,
    "metadata": {
        "colab": {"provenance": [], "toc_visible": True,
                  "name": "KKTC_TUFE_Tahmin_Colab.ipynb"},
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python"},
        "accelerator": "GPU",
    },
    "nbformat": 4, "nbformat_minor": 0,
}
out = pathlib.Path("notebooks/KKTC_TUFE_Tahmin_Colab.ipynb")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("yazıldı:", out, f"{out.stat().st_size/1024:.0f} KB, {len(cells)} hücre")
