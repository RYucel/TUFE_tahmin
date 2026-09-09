#!/usr/bin/env python
"""Colab defterini doğrular ve kod hücrelerini gerçekten çalıştırır.

İki aşama:
  1. Biçim  — nbformat şeması + `source` satır sonu sözleşmesi. (.ipynb'de
     liste elemanları AYIRAÇSIZ birleştirilir; son satır dışında her satır
     kendi "\\n" karakterini taşımalıdır, aksi hâlde hücre görüntüleyicide
     tek satıra yapışır.)
  2. Çalıştırma — kurulum ve Colab'e özgü hücreler dışındakiler sırayla
     çalıştırılır. Çıktılar `artifacts_dryrun/` altına yazılır; üretim
     `artifacts/` dizinine dokunulmaz.

Kullanım:
    python notebooks/_defter_dogrula.py            # biçim + çalıştırma
    python notebooks/_defter_dogrula.py --sadece-bicim
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks" / "KKTC_TUFE_Tahmin_Colab.ipynb"

# Kurulum ve Colab'e özgü hücreler: yerel doğrulamada çalıştırılmaz.
# (Başlıklar markdown hücrelerine taşındığı için kod içeriğine göre eşleşilir.)
ATLANACAK = [
    'sh("pip install',                 # paket kurulumu
    "git clone -q --branch",           # depoyu klonlama
    "display(HTML((out_dir(cfg)",      # raporu defterde gösterme
    "shutil.make_archive",             # ZIP indirme
]

AYARLAR_ISARETI = "REPO_URL"           # AYARLAR hücresini tanıyan ifade

# Çalıştırma sırasında defterdeki AYARLAR hücresinin yerine geçer.
AYARLAR_DRYRUN = """
HIZLI_MOD = True
SON_N_BASLANGIC = 40
TIMESFM_CALISTIR = False
TIMESFM_CTX = [512]
TIMESFM_SEPET_VARYANTI = False
VERI_KESIMI = "2026-08"
UFUK = 12
REPO_URL = ""; REPO_BRANCH = ""
print("DRY-RUN ayarları")
"""


def bicim_kontrolu(nb: dict) -> int:
    """Satır sonu sözleşmesi ve kod sözdizimi. Hata sayısını döner."""
    hata = 0
    for i, c in enumerate(nb["cells"]):
        src = c["source"]
        if not isinstance(src, list):
            print(f"HATA hücre {i}: source liste değil")
            hata += 1
            continue
        for j, ln in enumerate(src[:-1]):
            if not ln.endswith("\n"):
                print(f"HATA hücre {i} satır {j}: sonda \\n yok -> {ln[:60]!r}")
                hata += 1
        if src and src[-1].endswith("\n"):
            print(f"HATA hücre {i}: son satır \\n ile bitiyor")
            hata += 1
        birlesik = "".join(src)
        if len(src) > 1 and birlesik.count("\n") != len(src) - 1:
            print(f"HATA hücre {i}: satır sayısı tutmuyor")
            hata += 1
        if c["cell_type"] == "code":
            try:
                ast.parse(birlesik)
            except SyntaxError as exc:
                print(f"HATA hücre {i}: sözdizimi — {exc}")
                hata += 1
    try:
        import nbformat
        nbformat.validate(nbformat.read(NB, as_version=4))
        print("nbformat şema doğrulaması: GEÇTİ")
    except ImportError:
        print("nbformat kurulu değil; şema doğrulaması atlandı")
    except Exception as exc:
        print(f"HATA nbformat şeması: {exc}")
        hata += 1
    return hata


def calistir(nb: dict) -> int:
    """Kod hücrelerini sırayla çalıştırır. Hata olursa 1 döner."""
    import matplotlib
    matplotlib.use("Agg")

    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT))
    g: dict = {"__name__": "__main__",
               "display": lambda *a, **k: None}

    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])          # AYIRAÇSIZ — satır sonları zaten içinde
        baslik = next((ln for ln in src.split("\n") if ln.strip()), "")[:70]
        if any(mk in src for mk in ATLANACAK):
            print(f"--- [{i}] ATLANDI: {baslik}")
            continue
        if AYARLAR_ISARETI in src and "HIZLI_MOD" in src:
            src = AYARLAR_DRYRUN
        print(f"--- [{i}] {baslik}", flush=True)
        try:
            exec(compile(src, f"<hücre {i}>", "exec"), g)
        except Exception:
            print(f"!!! HÜCRE {i} HATA:")
            traceback.print_exc()
            return 1
        cfg = g.get("cfg")
        if isinstance(cfg, dict) and cfg.get("report", {}).get("out_dir") == "artifacts":
            cfg["report"]["out_dir"] = "artifacts_dryrun"
            print("    [dry-run] çıktı dizini -> artifacts_dryrun")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sadece-bicim", action="store_true")
    args = ap.parse_args()

    nb = json.loads(NB.read_text(encoding="utf-8"))
    print(f"Defter: {NB.relative_to(ROOT)} · {len(nb['cells'])} hücre "
          f"({sum(c['cell_type']=='code' for c in nb['cells'])} kod)")

    hata = bicim_kontrolu(nb)
    print(f"Biçim hatası: {hata}")
    if hata:
        return 1
    if args.sadece_bicim:
        return 0
    if calistir(nb):
        return 1
    print("\n=== TÜM HÜCRELER GEÇTİ ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
