# KKTC TÜFE Tahmin Raporu (veri kesimi: 2026-08)

**Seçilen model:** `BIRLESIM_mean_3` · aile: ensemble · eğitim penceresi: üye modellerin kendi pencereleri · dönüşüm: log
**Geliştirme seçim skoru S = 7.8509 yüzde puan** (S = 0.6·MAE_yılsonu + 0.3·MAE_6ay + 0.1·MAE_12ay)
**Seçim kuralı:** En iyi skora göre göreli farkı %2'den küçük adaylar berabere sayıldı; ardından basitlik, sonra hesaplama maliyeti.
**Donduruldu:** 2026-09-08T06:29:13.818575+00:00 (nihai holdout açılmadan önce)

## ⚠ Eksik zorunlu bileşen

TimesFM 3 çalıştırılamadı: TimesFM 3 kodu yüklendi (import başarılı) ancak ön eğitimli ağırlıklar indirilemedi (google/timesfm-3.0-pytorch): ProxyError: 403 Forbidden. Bu ortamda huggingface.co erişimi engellenmiş görünüyor; TimesFM 3 ÇALIŞTIRILAMAMIŞTIR.
Bu nedenle karşılaştırma **tamamlanmış sayılmaz**.

> Veri kaynağı notu: API'ye ulaşılamadı; API'nin beslendiği yukarı akış deposu kullanıldı (`https://kktc-tufe-api.stevevaius.workers.dev` egress politikasınca engelli). Kullanılan kaynak API'nin beslendiği `https://github.com/RYucel/kktc_tufe` deposudur.

## Dönem tahminleri

| olcu                                           | tanim                                                         |   deger_pct | donem             |
|:-----------------------------------------------|:--------------------------------------------------------------|------------:|:------------------|
| 2026 yılsonu enflasyonu (Ara 2026/Ara 2025)    | Gerçekleşmiş YTD (%24.0081, 2026-08) + 4 aylık tahmin         |     40.8071 | 2026-01 → 2026-12 |
| Gelecek 6 ayın BİLEŞİK enflasyonu              | Başlangıç sonrası 6 ayın bileşiği (yıllık enflasyon DEĞİLDİR) |     21.6083 | 2026-09 → 2027-02 |
| Gelecek 12 ayın BİLEŞİK enflasyonu             | Başlangıç sonrası 12 ayın bileşiği                            |     49.7812 | 2026-09 → 2027-08 |
| Temmuz–Aralık 2026 bileşik değişimi (2. dönem) | 2 ay gerçekleşme + 4 ay tahmin                                |     20.3965 | 2026-07 → 2026-12 |
| Ocak–Haziran 2027 bileşik değişimi (1. dönem)  | Tamamı tahmin (takvim yarıyılı)                               |     22.9896 | 2027-01 → 2027-06 |
| 2027-02 YILLIK enflasyonu                      | 12 aylık geriye dönük değişim (6 aylık bileşik DEĞİLDİR)      |     43.9104 | 2026-03 → 2027-02 |

## Aylık tahminler

| tarih   |   aylik_pct |   yillik_pct |   ytd_pct | ytd_kaynak         |   kumulatif_2026-08_sonrasi_pct | model           | veri_kesimi   |   aylik_lo80 |   aylik_hi80 |   aylik_lo95 |   aylik_hi95 | aralik_olcusu                                        |
|:--------|------------:|-------------:|----------:|:-------------------|--------------------------------:|:----------------|:--------------|-------------:|-------------:|-------------:|-------------:|:-----------------------------------------------------|
| 2026-09 |     3.16493 |      34.7902 |  27.9329  | resmî YTD + tahmin |                         3.16493 | BIRLESIM_mean_3 | 2026-08       |   0.660958   |      5.66891 |     -4.56608 |      10.896  | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2026-10 |     3.19942 |      37.6014 |  32.026   | resmî YTD + tahmin |                         6.46561 | BIRLESIM_mean_3 | 2026-08       |   0.540654   |      5.85818 |     -4.66106 |      11.0599 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2026-11 |     3.10902 |      40.7356 |  36.1307  | resmî YTD + tahmin |                         9.77565 | BIRLESIM_mean_3 | 2026-08       |   0.388761   |      5.82927 |     -4.95105 |      11.1691 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2026-12 |     3.43524 |      40.8031 |  40.8071  | resmî YTD + tahmin |                        13.5467  | BIRLESIM_mean_3 | 2026-08       |   0.92916    |      5.94131 |     -4.70064 |      11.5711 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-01 |     3.48269 |      42.8851 |   3.48269 | tahmin             |                        17.5012  | BIRLESIM_mean_3 | 2026-08       |   0.910407   |      6.05498 |     -4.92182 |      11.8872 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-02 |     3.49537 |      43.9104 |   7.09979 | tahmin             |                        21.6083  | BIRLESIM_mean_3 | 2026-08       |   0.794076   |      6.19666 |     -4.50571 |      11.4964 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-03 |     3.51432 |      45.7903 |  10.8636  | tahmin             |                        25.882   | BIRLESIM_mean_3 | 2026-08       |   0.913992   |      6.11465 |     -4.6339  |      11.6625 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-04 |     3.52344 |      44.2563 |  14.7698  | tahmin             |                        30.3174  | BIRLESIM_mean_3 | 2026-08       |   0.162786   |      6.8841  |     -4.57473 |      11.6216 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-05 |     3.52225 |      46.3169 |  18.8123  | tahmin             |                        34.9075  | BIRLESIM_mean_3 | 2026-08       |   0.0510911  |      6.99341 |     -4.62049 |      11.665  | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-06 |     3.51583 |      48.0751 |  22.9896  | tahmin             |                        39.6506  | BIRLESIM_mean_3 | 2026-08       |   0.00247173 |      7.02919 |     -4.55401 |      11.5857 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-07 |     3.40622 |      48.8036 |  27.1789  | tahmin             |                        44.4074  | BIRLESIM_mean_3 | 2026-08       |  -0.186093   |      6.99854 |     -4.7848  |      11.5973 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-08 |     3.72127 |      49.7812 |  31.9115  | tahmin             |                        49.7812  | BIRLESIM_mean_3 | 2026-08       |   0.0318371  |      7.4107  |     -4.48882 |      11.9314 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |

## Geliştirme sıralaması

| model                    |   MAE_yearend |   n_yearend |   MAE_c6 |   n_c6 |   MAE_c12 |   n_c12 |        S | uygun   |   sira |
|:-------------------------|--------------:|------------:|---------:|-------:|----------:|--------:|---------:|:--------|-------:|
| BIRLESIM_mean_3          |       6.23393 |          27 |  7.72318 |    110 |   17.9356 |     104 |  7.85087 | True    |      1 |
| BIRLESIM_median_3        |       6.23367 |          27 |  7.85773 |    110 |   18.046  |     104 |  7.90212 | True    |      2 |
| LightGBM_wtum            |       6.07274 |          27 |  8.21614 |    110 |   19.0379 |     104 |  8.01228 | True    |      3 |
| Ridge_wtum               |       6.74733 |          27 |  8.03681 |    110 |   17.3034 |     104 |  8.18978 | True    |      4 |
| ElasticNet_wtum          |       6.87136 |          27 |  8.03718 |    110 |   17.3205 |     104 |  8.26602 | True    |      5 |
| SARIMA_w60               |       6.82137 |          27 |  8.47584 |    110 |   21.1383 |     104 |  8.74941 | True    |      6 |
| Ridge_sepet_wtum         |       6.79461 |          27 |  8.83901 |    110 |   21.4031 |     104 |  8.86877 | True    |      7 |
| SARIMA_wtum              |       7.54749 |          27 |  8.37023 |    110 |   18.6103 |     104 |  8.90059 | True    |      8 |
| Ridge_w120               |       7.34396 |          27 |  9.33359 |    110 |   22.3695 |     104 |  9.44341 | True    |      9 |
| ETS_damped_seasonal_wtum |       8.31622 |          27 |  8.71236 |    110 |   19.9181 |     104 |  9.59525 | True    |     10 |
| AutoTheta_wtum           |       8.55944 |          27 |  8.93819 |    110 |   20.8346 |     104 |  9.90058 | True    |     11 |
| ortalama_12ay            |       8.60654 |          27 |  8.9732  |    110 |   20.619  |     104 |  9.91779 | True    |     12 |
| UCM_llt_seasonal_wtum    |       8.73583 |          27 |  8.92779 |    110 |   20.8834 |     104 | 10.0082  | True    |     13 |
| SARIMA_w120              |       8.10054 |          27 |  9.72765 |    110 |   23.2532 |     104 | 10.1039  | True    |     14 |
| LightGBM_sepet_wtum      |       7.74693 |          27 | 10.8942  |    110 |   24.933  |     104 | 10.4097  | True    |     15 |
| LightGBM_w120            |       8.12867 |          27 | 10.7403  |    110 |   25.2383 |     104 | 10.6231  | True    |     16 |
| naive_mevsimsel_12       |       8.8343  |          27 | 10.9362  |    110 |   20.619  |     104 | 10.6434  | True    |     17 |
| ortalama_6ay             |       9.56069 |          27 | 10.2723  |    110 |   24.1906 |     104 | 11.2372  | True    |     18 |
| AutoTheta_w120           |      10.3295  |          27 |  9.94679 |    110 |   28.1168 |     104 | 11.9934  | True    |     19 |
| ortalama_3ay             |      10.0853  |          27 | 10.6266  |    110 |   29.2403 |     104 | 12.1632  | True    |     20 |
| ETS_damped_seasonal_w120 |      10.3733  |          27 | 10.2389  |    110 |   30.1947 |     104 | 12.3151  | True    |     21 |
| UCM_llt_seasonal_w120    |      10.3583  |          27 | 10.4285  |    110 |   31.2467 |     104 | 12.4682  | True    |     22 |
| AutoTheta_w60            |      10.4139  |          27 | 10.6328  |    110 |   30.4387 |     104 | 12.4821  | True    |     23 |
| ETS_damped_seasonal_w60  |      10.2745  |          27 | 10.9857  |    110 |   32.299  |     104 | 12.6903  | True    |     24 |
| naive_son_ay             |      12.5325  |          27 | 11.888   |    110 |   34.228  |     104 | 14.5087  | True    |     25 |

## Nihai test (yalnızca denetim)

| model                    | hedef   |   n |      MAE |     RMSE |         ME |     MAPE |   en_kotu_hata | en_kotu_donem   |     MASE |   MASE_payda_n |
|:-------------------------|:--------|----:|---------:|---------:|-----------:|---------:|---------------:|:----------------|---------:|---------------:|
| LightGBM_sepet_wtum      | c12     |  13 |  2.09914 |  2.47841 | -1.98339   |  5.41879 |        4.58944 | 2026-02         | 0.101782 |            104 |
| SARIMA_w120              | c12     |  13 |  3.26818 |  4.30294 | -2.50824   |  8.46129 |        8.25288 | 2025-12         | 0.158496 |            104 |
| LightGBM_w120            | c12     |  13 |  5.25027 |  5.50281 |  5.25027   | 13.9698  |        7.21675 | 2026-08         | 0.254524 |            104 |
| SARIMA_wtum              | c12     |  13 |  6.23238 |  8.52005 |  4.54499   | 16.7493  |       21.3155  | 2025-08         | 0.302217 |            104 |
| Ridge_w120               | c12     |  13 |  6.30835 |  7.81084 |  6.30835   | 16.9912  |       16.8069  | 2025-08         | 0.305877 |            104 |
| Ridge_sepet_wtum         | c12     |  13 |  6.98227 |  9.5682  |  5.17461   | 18.7493  |       20.5772  | 2025-10         | 0.338559 |            104 |
| ElasticNet_wtum          | c12     |  13 |  7.86043 | 10.1568  |  7.85066   | 21.1857  |       21.2788  | 2025-08         | 0.38119  |            104 |
| AutoTheta_wtum           | c12     |  13 |  8.23263 | 11.843   |  6.73767   | 22.1653  |       29.4909  | 2025-08         | 0.399249 |            104 |
| UCM_llt_seasonal_wtum    | c12     |  13 |  8.66614 | 13.0695  |  7.96808   | 23.4581  |       31.9624  | 2025-08         | 0.420263 |            104 |
| ETS_damped_seasonal_w120 | c12     |  13 |  9.684   | 11.0259  |  0.0465739 | 25.5427  |       18.9401  | 2025-12         | 0.469609 |            104 |
| ortalama_6ay             | c12     |  13 |  9.88186 | 13.3879  |  3.26398   | 26.3469  |       35.9428  | 2025-08         | 0.479146 |            104 |
| AutoTheta_w120           | c12     |  13 | 10.0896  | 11.2621  |  2.05033   | 26.6575  |       17.8889  | 2025-10         | 0.48922  |            104 |
| ortalama_3ay             | c12     |  13 | 10.2712  | 12.714   | -0.482171  | 27.0002  |       22.6638  | 2026-01         | 0.498125 |            104 |
| UCM_llt_seasonal_w120    | c12     |  13 | 10.3528  | 11.5675  |  1.44478   | 27.4025  |       19.1793  | 2025-10         | 0.502049 |            104 |
| ETS_damped_seasonal_wtum | c12     |  13 | 10.4324  | 14.2484  | 10.1034    | 28.0973  |       33.1641  | 2025-08         | 0.505911 |            104 |
| AutoTheta_w60            | c12     |  13 | 10.8897  | 12.5696  |  3.13336   | 28.8598  |       26.3193  | 2025-08         | 0.52806  |            104 |
| Ridge_wtum               | c12     |  13 | 11.0268  | 13.4785  | 10.9928    | 29.676   |       26.5945  | 2025-08         | 0.534726 |            104 |
| naive_mevsimsel_12       | c12     |  13 | 12.1293  | 15.9404  | 10.9419    | 32.4511  |       29.3362  | 2025-08         | 0.588223 |            104 |
| ortalama_12ay            | c12     |  13 | 12.1293  | 15.9404  | 10.9419    | 32.4511  |       29.3362  | 2025-08         | 0.588223 |            104 |
| ETS_damped_seasonal_w60  | c12     |  13 | 12.8928  | 15.8637  |  0.27039   | 33.9609  |       31.6316  | 2025-10         | 0.625262 |            104 |
| BIRLESIM_median_3        | c12     |  13 | 13.1849  | 14.6312  | 13.1849    | 35.284   |       22.2158  | 2025-08         | 0.63928  |            104 |
| LightGBM_wtum            | c12     |  13 | 13.1897  | 15.5532  | 12.8159    | 35.4124  |       28.5006  | 2025-08         | 0.639524 |            104 |
| BIRLESIM_mean_3          | c12     |  13 | 13.9608  | 15.195   | 13.9608    | 37.3098  |       24.6415  | 2025-08         | 0.676899 |            104 |
| naive_son_ay             | c12     |  13 | 14.7011  | 17.0235  | -0.649324  | 38.8086  |       27.933   | 2026-03         | 0.712825 |            104 |
| SARIMA_w60               | c12     |  13 | 18.3271  | 18.7573  | 18.3271    | 48.5151  |       23.7069  | 2026-03         | 0.888504 |            104 |
| LightGBM_sepet_wtum      | c6      |  19 |  1.99411 |  2.48063 | -0.819271  | 11.792   |        5.53682 | 2025-09         | 0.181498 |            114 |
| Ridge_sepet_wtum         | c6      |  19 |  2.54198 |  3.34068 |  0.997014  | 16.4487  |        6.97656 | 2025-02         | 0.230993 |            114 |
| Ridge_w120               | c6      |  19 |  2.56352 |  3.4798  |  2.21061   | 17.0678  |        8.58534 | 2025-02         | 0.23326  |            114 |
| LightGBM_w120            | c6      |  19 |  2.89715 |  3.40296 |  2.4427    | 18.5884  |        7.52638 | 2026-03         | 0.262981 |            114 |
| SARIMA_w120              | c6      |  19 |  3.0796  |  3.79047 | -0.454166  | 19.0077  |        9.84407 | 2026-03         | 0.279722 |            114 |
| ElasticNet_wtum          | c6      |  19 |  3.27125 |  4.68473 |  2.80515   | 21.9907  |       12.1211  | 2025-02         | 0.297499 |            114 |
| SARIMA_wtum              | c6      |  19 |  3.64003 |  5.06996 |  1.81019   | 24.0492  |       13.6152  | 2025-02         | 0.331151 |            114 |
| UCM_llt_seasonal_wtum    | c6      |  19 |  3.88743 |  5.93513 |  2.79963   | 26.203   |       16.3277  | 2025-02         | 0.353895 |            114 |
| ortalama_12ay            | c6      |  19 |  4.0778  |  6.47415 |  3.44718   | 27.1479  |       15.9864  | 2025-02         | 0.371888 |            114 |
| ETS_damped_seasonal_w120 | c6      |  19 |  4.23281 |  5.1262  |  0.766625  | 26.4568  |       11.8102  | 2026-03         | 0.383676 |            114 |
| Ridge_wtum               | c6      |  19 |  4.29868 |  5.71544 |  3.88612   | 28.3709  |       13.5443  | 2025-02         | 0.390701 |            114 |
| AutoTheta_wtum           | c6      |  19 |  4.38592 |  5.93485 |  2.33532   | 28.739   |       16.1484  | 2025-02         | 0.399288 |            114 |
| UCM_llt_seasonal_w120    | c6      |  19 |  4.47307 |  5.3104  |  1.1454    | 27.9279  |       12.2357  | 2026-03         | 0.405592 |            114 |
| ETS_damped_seasonal_wtum | c6      |  19 |  4.59875 |  6.51056 |  3.45797   | 30.6109  |       17.4862  | 2025-02         | 0.418611 |            114 |
| AutoTheta_w120           | c6      |  19 |  4.73466 |  5.87268 |  0.326276  | 29.4124  |       15.4071  | 2026-03         | 0.429948 |            114 |
| ortalama_6ay             | c6      |  19 |  4.76542 |  6.53103 |  1.35308   | 30.7181  |       18.5346  | 2025-02         | 0.433689 |            114 |
| LightGBM_wtum            | c6      |  19 |  5.0486  |  6.74555 |  4.76269   | 33.3253  |       15.5608  | 2025-02         | 0.458776 |            114 |
| BIRLESIM_median_3        | c6      |  19 |  5.16517 |  6.29861 |  5.0977    | 33.401   |       12.4497  | 2025-02         | 0.469135 |            114 |
| AutoTheta_w60            | c6      |  19 |  5.35555 |  6.56942 |  0.643345  | 34.0502  |       14.4882  | 2026-03         | 0.487052 |            114 |
| BIRLESIM_mean_3          | c6      |  19 |  5.41589 |  6.56982 |  5.37172   | 35.1591  |       13.5289  | 2025-02         | 0.49183  |            114 |
| ortalama_3ay             | c6      |  19 |  5.57638 |  6.71664 |  0.0624644 | 34.7059  |       13.4435  | 2026-03         | 0.507226 |            114 |
| ETS_damped_seasonal_w60  | c6      |  19 |  6.68661 |  8.31787 |  2.01074   | 41.879   |       18.0559  | 2026-03         | 0.60618  |            114 |
| naive_mevsimsel_12       | c6      |  19 |  7.08891 |  9.55629 |  5.73779   | 43.3357  |       20.187   | 2025-04         | 0.646294 |            114 |
| SARIMA_w60               | c6      |  19 |  7.53416 |  8.28794 |  7.53416   | 47.1     |       16.7315  | 2026-03         | 0.683845 |            114 |
| naive_son_ay             | c6      |  19 |  7.76593 |  9.35108 | -0.225761  | 47.5323  |       24.1893  | 2026-03         | 0.704645 |            114 |
| LightGBM_sepet_wtum      | yearend |   5 |  2.62041 |  3.06834 |  1.39019   |  5.48672 |        4.8902  | 2024-12         | 0.294321 |             29 |
| Ridge_w120               | yearend |   5 |  3.39574 |  4.62619 |  3.05641   |  6.72873 |        7.95322 | 2024-12         | 0.382942 |             29 |
| SARIMA_w120              | yearend |   5 |  3.55875 |  4.17263 |  1.51451   |  7.52326 |        6.00236 | 2024-12         | 0.399425 |             29 |
| LightGBM_w120            | yearend |   5 |  3.72279 |  4.2036  |  3.72279   |  7.83936 |        6.07346 | 2024-12         | 0.41796  |             29 |
| Ridge_sepet_wtum         | yearend |   5 |  3.72311 |  4.50868 |  2.60569   |  7.66229 |        6.74514 | 2024-12         | 0.418712 |             29 |
| ElasticNet_wtum          | yearend |   5 |  4.07641 |  5.93654 |  4.07641   |  7.91099 |       10.8806  | 2024-12         | 0.460373 |             29 |
| Ridge_wtum               | yearend |   5 |  4.17837 |  5.87635 |  4.01804   |  8.2666  |       11.0565  | 2024-12         | 0.471253 |             29 |
| AutoTheta_wtum           | yearend |   5 |  4.33913 |  6.59516 |  3.6033    |  8.40535 |       13.1326  | 2024-12         | 0.490106 |             29 |
| ortalama_3ay             | yearend |   5 |  4.43024 |  6.0508  |  3.97573   |  8.88501 |       11.4627  | 2024-12         | 0.499176 |             29 |
| ETS_damped_seasonal_wtum | yearend |   5 |  4.46025 |  7.16646 |  4.31266   |  8.46805 |       14.2665  | 2024-12         | 0.504479 |             29 |
| AutoTheta_w120           | yearend |   5 |  4.51099 |  5.10769 |  3.01579   |  9.50663 |        7.78028 | 2024-12         | 0.506422 |             29 |
| SARIMA_wtum              | yearend |   5 |  5.1257  |  6.88534 |  4.63723   | 10.2454  |       12.802   | 2024-12         | 0.577675 |             29 |
| BIRLESIM_median_3        | yearend |   5 |  5.32211 |  6.47081 |  5.32211   | 10.9447  |       11.1569  | 2024-12         | 0.598574 |             29 |
| UCM_llt_seasonal_wtum    | yearend |   5 |  5.4444  |  7.92917 |  5.11618   | 10.6267  |       15.2095  | 2024-12         | 0.614623 |             29 |
| AutoTheta_w60            | yearend |   5 |  5.45211 |  6.76879 |  3.8854    | 11.2294  |       12.4331  | 2024-12         | 0.613125 |             29 |
| BIRLESIM_mean_3          | yearend |   5 |  5.58328 |  6.85919 |  5.58328   | 11.4831  |       12.2359  | 2024-12         | 0.627943 |             29 |
| UCM_llt_seasonal_w120    | yearend |   5 |  5.74686 |  6.30405 |  1.09027   | 12.6097  |        8.57482 | 2025-12         | 0.643156 |             29 |
| ETS_damped_seasonal_w120 | yearend |   5 |  5.80468 |  6.40347 |  0.92359   | 12.7786  |        9.09541 | 2025-12         | 0.649457 |             29 |
| ortalama_12ay            | yearend |   5 |  5.82413 |  8.10108 |  4.74169   | 11.4737  |       14.6175  | 2024-12         | 0.657064 |             29 |
| ortalama_6ay             | yearend |   5 |  5.99673 |  8.41092 |  5.71429   | 11.981   |       16.8325  | 2024-12         | 0.675863 |             29 |
| LightGBM_wtum            | yearend |   5 |  6.1038  |  8.16965 |  6.1038    | 12.2324  |       15.2558  | 2024-12         | 0.687779 |             29 |
| naive_son_ay             | yearend |   5 |  6.65547 |  7.34825 |  1.05211   | 14.8332  |       11.2899  | 2025-12         | 0.743917 |             29 |
| SARIMA_w60               | yearend |   5 |  6.66655 |  7.19402 |  6.66655   | 14.4472  |       10.4366  | 2024-12         | 0.74681  |             29 |
| naive_mevsimsel_12       | yearend |   5 |  6.9301  |  8.04444 |  2.59653   | 14.4297  |       12.358   | 2024-12         | 0.778706 |             29 |
| ETS_damped_seasonal_w60  | yearend |   5 |  8.4496  |  9.75677 |  0.567235  | 19.1339  |       15.8684  | 2025-12         | 0.943239 |             29 |

## Aralık kapsaması

| asama      | hedef   | seviye   |   kapsama |   n |   ortalama_genislik |   interval_score |   WIS_yaklasik | model           |
|:-----------|:--------|:---------|----------:|----:|--------------------:|-----------------:|---------------:|:----------------|
| geliştirme | c12     | %80      |  0.590361 |  83 |            30.1817  |        146.278   |      16.0097   | BIRLESIM_mean_3 |
| geliştirme | c12     | %95      |  0.643836 |  73 |            74.0292  |        463.339   |      16.0097   | BIRLESIM_mean_3 |
| geliştirme | c6      | %80      |  0.694737 |  95 |            17.4011  |         57.1508  |       5.75216  | BIRLESIM_mean_3 |
| geliştirme | c6      | %95      |  0.811765 |  85 |            49.3342  |        138.365   |       5.75216  | BIRLESIM_mean_3 |
| geliştirme | m1      | %80      |  0.790476 | 105 |             3.83237 |          7.83039 |       0.806579 | BIRLESIM_mean_3 |
| geliştirme | m1      | %95      |  0.915789 |  95 |             8.13613 |         17.0707  |       0.806579 | BIRLESIM_mean_3 |
| geliştirme | m10     | %80      |  0.678161 |  87 |             3.93982 |         11.8752  |       1.25769  | BIRLESIM_mean_3 |
| geliştirme | m10     | %95      |  0.805195 |  77 |             9.82137 |         32.4227  |       1.25769  | BIRLESIM_mean_3 |
| geliştirme | m11     | %80      |  0.682353 |  85 |             3.86011 |         12.2821  |       1.28282  | BIRLESIM_mean_3 |
| geliştirme | m11     | %95      |  0.813333 |  75 |            10.0534  |         33.0544  |       1.28282  | BIRLESIM_mean_3 |
| geliştirme | m12     | %80      |  0.662651 |  83 |             3.91577 |         12.7907  |       1.32027  | BIRLESIM_mean_3 |
| geliştirme | m12     | %95      |  0.808219 |  73 |            10.1195  |         33.9151  |       1.32027  | BIRLESIM_mean_3 |
| geliştirme | m2      | %80      |  0.776699 | 103 |             3.69304 |          8.97128 |       0.901665 | BIRLESIM_mean_3 |
| geliştirme | m2      | %95      |  0.913978 |  93 |             9.39543 |         19.0021  |       0.901665 | BIRLESIM_mean_3 |
| geliştirme | m3      | %80      |  0.772277 | 101 |             3.96556 |          9.47543 |       0.945681 | BIRLESIM_mean_3 |
| geliştirme | m3      | %95      |  0.901099 |  91 |             9.22586 |         19.7554  |       0.945681 | BIRLESIM_mean_3 |
| geliştirme | m4      | %80      |  0.767677 |  99 |             4.16181 |         10.1998  |       1.02251  | BIRLESIM_mean_3 |
| geliştirme | m4      | %95      |  0.853933 |  89 |             9.29776 |         22.9977  |       1.02251  | BIRLESIM_mean_3 |
| geliştirme | m5      | %80      |  0.762887 |  97 |             3.94348 |         10.3167  |       1.05939  | BIRLESIM_mean_3 |
| geliştirme | m5      | %95      |  0.850575 |  87 |             9.25979 |         25.0414  |       1.05939  | BIRLESIM_mean_3 |
| geliştirme | m6      | %80      |  0.736842 |  95 |             4.02527 |         10.6821  |       1.08994  | BIRLESIM_mean_3 |
| geliştirme | m6      | %95      |  0.835294 |  85 |             9.18978 |         25.8826  |       1.08994  | BIRLESIM_mean_3 |
| geliştirme | m7      | %80      |  0.731183 |  93 |             3.91117 |         11.0053  |       1.13837  | BIRLESIM_mean_3 |
| geliştirme | m7      | %95      |  0.831325 |  83 |             9.54996 |         28.7018  |       1.13837  | BIRLESIM_mean_3 |
| geliştirme | m8      | %80      |  0.725275 |  91 |             4.00161 |         11.4307  |       1.19972  | BIRLESIM_mean_3 |
| geliştirme | m8      | %95      |  0.839506 |  81 |             9.76424 |         30.8052  |       1.19972  | BIRLESIM_mean_3 |
| geliştirme | m9      | %80      |  0.696629 |  89 |             3.94319 |         11.5659  |       1.2301   | BIRLESIM_mean_3 |
| geliştirme | m9      | %95      |  0.810127 |  79 |             9.66136 |         32.2389  |       1.2301   | BIRLESIM_mean_3 |
| geliştirme | yearend | %80      |  0.666667 |  15 |            17.7482  |         53.8175  |       3.26477  | BIRLESIM_mean_3 |
| geliştirme | yearend | %95      |  1        |   6 |            50.5254  |         50.5254  |       3.26477  | BIRLESIM_mean_3 |
| geliştirme | yoy1    | %80      |  0.72381  | 105 |             4.73029 |         11.3968  |       1.17042  | BIRLESIM_mean_3 |
| geliştirme | yoy1    | %95      |  0.894737 |  95 |            10.9269  |         24.4404  |       1.17042  | BIRLESIM_mean_3 |
| geliştirme | yoy10   | %80      |  0.655172 |  87 |            27.3526  |        118.053   |      12.7589   | BIRLESIM_mean_3 |
| geliştirme | yoy10   | %95      |  0.701299 |  77 |            69.1227  |        362.048   |      12.7589   | BIRLESIM_mean_3 |
| geliştirme | yoy11   | %80      |  0.6      |  85 |            29.2849  |        130.73    |      14.217    | BIRLESIM_mean_3 |
| geliştirme | yoy11   | %95      |  0.653333 |  75 |            72.2411  |        406.358   |      14.217    | BIRLESIM_mean_3 |
| geliştirme | yoy12   | %80      |  0.590361 |  83 |            30.1817  |        146.278   |      16.0097   | BIRLESIM_mean_3 |
| geliştirme | yoy12   | %95      |  0.643836 |  73 |            74.0292  |        463.339   |      16.0097   | BIRLESIM_mean_3 |
| geliştirme | yoy2    | %80      |  0.728155 | 103 |             7.87507 |         22.7314  |       2.21822  | BIRLESIM_mean_3 |
| geliştirme | yoy2    | %95      |  0.870968 |  93 |            22.3976  |         45.0325  |       2.21822  | BIRLESIM_mean_3 |
| geliştirme | yoy3    | %80      |  0.732673 | 101 |            11.1174  |         33.2427  |       3.2593   | BIRLESIM_mean_3 |
| geliştirme | yoy3    | %95      |  0.868132 |  91 |            29.9275  |         66.7453  |       3.2593   | BIRLESIM_mean_3 |
| geliştirme | yoy4    | %80      |  0.737374 |  99 |            14.3713  |         45.614   |       4.49433  | BIRLESIM_mean_3 |
| geliştirme | yoy4    | %95      |  0.820225 |  89 |            37.9618  |         98.3311  |       4.49433  | BIRLESIM_mean_3 |
| geliştirme | yoy5    | %80      |  0.721649 |  97 |            16.7163  |         57.4088  |       5.7522   | BIRLESIM_mean_3 |
| geliştirme | yoy5    | %95      |  0.816092 |  87 |            46.4748  |        134.215   |       5.7522   | BIRLESIM_mean_3 |
| geliştirme | yoy6    | %80      |  0.663158 |  95 |            19.4434  |         69.2784  |       7.01663  | BIRLESIM_mean_3 |
| geliştirme | yoy6    | %95      |  0.811765 |  85 |            56.0071  |        171.916   |       7.01663  | BIRLESIM_mean_3 |
| geliştirme | yoy7    | %80      |  0.655914 |  93 |            20.736   |         81.7411  |       8.29128  | BIRLESIM_mean_3 |
| geliştirme | yoy7    | %95      |  0.807229 |  83 |            60.2888  |        205.65    |       8.29128  | BIRLESIM_mean_3 |
| geliştirme | yoy8    | %80      |  0.659341 |  91 |            22.5848  |         93.1775  |       9.62928  | BIRLESIM_mean_3 |
| geliştirme | yoy8    | %95      |  0.765432 |  81 |            65.3606  |        250.624   |       9.62928  | BIRLESIM_mean_3 |
| geliştirme | yoy9    | %80      |  0.674157 |  89 |            25.1697  |        104.753   |      11.1638   | BIRLESIM_mean_3 |
| geliştirme | yoy9    | %95      |  0.734177 |  79 |            68.323   |        306.48    |      11.1638   | BIRLESIM_mean_3 |
| nihai test | c12     | %80      |  1        |  13 |            89.962   |         89.962   |       8.29689  | BIRLESIM_mean_3 |
| nihai test | c12     | %95      |  1        |  13 |           190.625   |        190.625   |       8.29689  | BIRLESIM_mean_3 |
| nihai test | c6      | %80      |  1        |  19 |            42.2161  |         42.2161  |       3.76743  | BIRLESIM_mean_3 |
| nihai test | c6      | %95      |  1        |  19 |            99.5613  |         99.5613  |       3.76743  | BIRLESIM_mean_3 |
| nihai test | m1      | %80      |  0.916667 |  24 |             4.82314 |          5.21854 |       0.58931  | BIRLESIM_mean_3 |
| nihai test | m1      | %95      |  1        |  24 |            15.462   |         15.462   |       0.58931  | BIRLESIM_mean_3 |
| nihai test | m10     | %80      |  1        |  15 |             7.02672 |          7.02672 |       0.697845 | BIRLESIM_mean_3 |
| nihai test | m10     | %95      |  1        |  15 |            16.1397  |         16.1397  |       0.697845 | BIRLESIM_mean_3 |
| nihai test | m11     | %80      |  1        |  14 |             7.18463 |          7.18463 |       0.695723 | BIRLESIM_mean_3 |
| nihai test | m11     | %95      |  1        |  14 |            16.3821  |         16.3821  |       0.695723 | BIRLESIM_mean_3 |
| nihai test | m12     | %80      |  1        |  13 |             7.37886 |          7.37886 |       0.719964 | BIRLESIM_mean_3 |
| nihai test | m12     | %95      |  1        |  13 |            16.4202  |         16.4202  |       0.719964 | BIRLESIM_mean_3 |
| nihai test | m2      | %80      |  0.869565 |  23 |             4.9978  |          5.6773  |       0.624106 | BIRLESIM_mean_3 |
| nihai test | m2      | %95      |  1        |  23 |            15.721   |         15.721   |       0.624106 | BIRLESIM_mean_3 |
| nihai test | m3      | %80      |  0.909091 |  22 |             5.37589 |          5.72694 |       0.661067 | BIRLESIM_mean_3 |
| nihai test | m3      | %95      |  1        |  22 |            16.1201  |         16.1201  |       0.661067 | BIRLESIM_mean_3 |
| nihai test | m4      | %80      |  0.952381 |  21 |             4.92849 |          5.17313 |       0.6206   | BIRLESIM_mean_3 |
| nihai test | m4      | %95      |  1        |  21 |            16.2718  |         16.2718  |       0.6206   | BIRLESIM_mean_3 |
| nihai test | m5      | %80      |  0.9      |  20 |             4.67998 |          4.88012 |       0.591545 | BIRLESIM_mean_3 |
| nihai test | m5      | %95      |  1        |  20 |            16.809   |         16.809   |       0.591545 | BIRLESIM_mean_3 |
| nihai test | m6      | %80      |  1        |  19 |             5.22448 |          5.22448 |       0.593808 | BIRLESIM_mean_3 |
| nihai test | m6      | %95      |  1        |  19 |            16.0022  |         16.0022  |       0.593808 | BIRLESIM_mean_3 |
| nihai test | m7      | %80      |  0.944444 |  18 |             4.95274 |          4.95283 |       0.585086 | BIRLESIM_mean_3 |
| nihai test | m7      | %95      |  1        |  18 |            16.2964  |         16.2964  |       0.585086 | BIRLESIM_mean_3 |
| nihai test | m8      | %80      |  1        |  17 |             6.72131 |          6.72131 |       0.681801 | BIRLESIM_mean_3 |
| nihai test | m8      | %95      |  1        |  17 |            16.1963  |         16.1963  |       0.681801 | BIRLESIM_mean_3 |
| nihai test | m9      | %80      |  1        |  16 |             6.94232 |          6.94232 |       0.708156 | BIRLESIM_mean_3 |
| nihai test | m9      | %95      |  1        |  16 |            16.2855  |         16.2855  |       0.708156 | BIRLESIM_mean_3 |
| nihai test | yearend | %80      |  1        |   5 |            25.3739  |         25.3739  |       2.63687  | BIRLESIM_mean_3 |
| nihai test | yearend | %95      |  1        |   5 |            50.5254  |         50.5254  |       2.63687  | BIRLESIM_mean_3 |
| nihai test | yoy1    | %80      |  0.958333 |  24 |             8.17481 |          8.30357 |       0.878219 | BIRLESIM_mean_3 |
| nihai test | yoy1    | %95      |  1        |  24 |            23.0303  |         23.0303  |       0.878219 | BIRLESIM_mean_3 |
| nihai test | yoy10   | %80      |  1        |  15 |            72.9604  |         72.9604  |       7.00917  | BIRLESIM_mean_3 |
| nihai test | yoy10   | %95      |  1        |  15 |           172.12    |        172.12    |       7.00917  | BIRLESIM_mean_3 |
| nihai test | yoy11   | %80      |  1        |  14 |            78.22    |         78.22    |       7.62883  | BIRLESIM_mean_3 |
| nihai test | yoy11   | %95      |  1        |  14 |           185.576   |        185.576   |       7.62883  | BIRLESIM_mean_3 |
| nihai test | yoy12   | %80      |  1        |  13 |            89.962   |         89.962   |       8.29689  | BIRLESIM_mean_3 |
| nihai test | yoy12   | %95      |  1        |  13 |           190.625   |        190.625   |       8.29689  | BIRLESIM_mean_3 |
| nihai test | yoy2    | %80      |  0.913043 |  23 |            14.8623  |         15.3988  |       1.53118  | BIRLESIM_mean_3 |
| nihai test | yoy2    | %95      |  1        |  23 |            41.6271  |         41.6271  |       1.53118  | BIRLESIM_mean_3 |
| nihai test | yoy3    | %80      |  0.954545 |  22 |            21.7185  |         22.1758  |       2.19644  | BIRLESIM_mean_3 |
| nihai test | yoy3    | %95      |  1        |  22 |            53.0551  |         53.0551  |       2.19644  | BIRLESIM_mean_3 |
| nihai test | yoy4    | %80      |  0.952381 |  21 |            26.7729  |         27.1433  |       2.6843   | BIRLESIM_mean_3 |
| nihai test | yoy4    | %95      |  1        |  21 |            68.4137  |         68.4137  |       2.6843   | BIRLESIM_mean_3 |
| nihai test | yoy5    | %80      |  1        |  20 |            35.1611  |         35.1611  |       3.36615  | BIRLESIM_mean_3 |
| nihai test | yoy5    | %95      |  1        |  20 |            88.0134  |         88.0134  |       3.36615  | BIRLESIM_mean_3 |
| nihai test | yoy6    | %80      |  1        |  19 |            51.4034  |         51.4034  |       4.51407  | BIRLESIM_mean_3 |
| nihai test | yoy6    | %95      |  1        |  19 |           114.669   |        114.669   |       4.51407  | BIRLESIM_mean_3 |
| nihai test | yoy7    | %80      |  1        |  18 |            59.9461  |         59.9461  |       5.24698  | BIRLESIM_mean_3 |
| nihai test | yoy7    | %95      |  1        |  18 |           126.929   |        126.929   |       5.24698  | BIRLESIM_mean_3 |
| nihai test | yoy8    | %80      |  1        |  17 |            61.4074  |         61.4074  |       5.74296  | BIRLESIM_mean_3 |
| nihai test | yoy8    | %95      |  1        |  17 |           145.91    |        145.91    |       5.74296  | BIRLESIM_mean_3 |
| nihai test | yoy9    | %80      |  1        |  16 |            64.3724  |         64.3724  |       6.28034  | BIRLESIM_mean_3 |
| nihai test | yoy9    | %95      |  1        |  16 |           164.179   |        164.179   |       6.28034  | BIRLESIM_mean_3 |

## Sınırlar

- Geçmiş veri sürümleri yoktur; değerlendirme *son veri sürümüyle geriye dönük test*tir.
- 24 aylık nihai testte yalnızca iki tamamlanmış yılsonu vardır.
- "En iyi model", bu veri ve bu protokolde en başarılı adaydır; gelecek performans garantisi değildir.
- TimesFM 3.0 ağırlıkları ticari/üretim kullanımına kapalıdır (`timesfm-non-commercial-license-v1.0`).
