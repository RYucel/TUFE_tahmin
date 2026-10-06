# KKTC TÜFE Tahmin Raporu (veri kesimi: 2026-09)

**Seçilen model:** `BIRLESIM_mean_3` · aile: ensemble · eğitim penceresi: üye modellerin kendi pencereleri · dönüşüm: log
**Geliştirme seçim skoru S = 7.8509 yüzde puan** (S = 0.6·MAE_yılsonu + 0.3·MAE_6ay + 0.1·MAE_12ay)
**Seçim kuralı:** En iyi skora göre göreli farkı %2'den küçük adaylar berabere sayıldı; ardından basitlik, sonra hesaplama maliyeti.
**Donduruldu:** 2026-10-06T08:56:10.167749+00:00 (nihai holdout açılmadan önce)

## ⚠ Eksik zorunlu bileşen

TimesFM 3 çalıştırılamadı: TimesFM 3 kodu yüklendi (import başarılı) ancak ön eğitimli ağırlıklar indirilemedi (google/timesfm-3.0-pytorch): ProxyError: 403 Forbidden. Bu ortamda huggingface.co erişimi engellenmiş görünüyor; TimesFM 3 ÇALIŞTIRILAMAMIŞTIR.
Bu nedenle karşılaştırma **tamamlanmış sayılmaz**.

> Veri kaynağı notu: API'ye ulaşılamadı; API'nin beslendiği yukarı akış deposu kullanıldı (`https://kktc-tufe-api.stevevaius.workers.dev` egress politikasınca engelli). Kullanılan kaynak API'nin beslendiği `https://github.com/RYucel/kktc_tufe` deposudur.

## Dönem tahminleri

| olcu                                           | tanim                                                         |   deger_pct | donem             |
|:-----------------------------------------------|:--------------------------------------------------------------|------------:|:------------------|
| 2026 yılsonu enflasyonu (Ara 2026/Ara 2025)    | Gerçekleşmiş YTD (%28.1458, 2026-09) + 3 aylık tahmin         |     39.9335 | 2026-01 → 2026-12 |
| Gelecek 6 ayın BİLEŞİK enflasyonu              | Başlangıç sonrası 6 ayın bileşiği (yıllık enflasyon DEĞİLDİR) |     19.7243 | 2026-10 → 2027-03 |
| Gelecek 12 ayın BİLEŞİK enflasyonu             | Başlangıç sonrası 12 ayın bileşiği                            |     44.4867 | 2026-10 → 2027-09 |
| Temmuz–Aralık 2026 bileşik değişimi (2. dönem) | 3 ay gerçekleşme + 3 ay tahmin                                |     19.6495 | 2026-07 → 2026-12 |
| Ocak–Haziran 2027 bileşik değişimi (1. dönem)  | Tamamı tahmin (takvim yarıyılı)                               |     19.7585 | 2027-01 → 2027-06 |
| 2027-02 YILLIK enflasyonu                      | 12 aylık geriye dönük değişim (6 aylık bileşik DEĞİLDİR)      |     42.0014 | 2026-03 → 2027-02 |

## Aylık tahminler

| tarih   |   aylik_pct |   yillik_pct |   ytd_pct | ytd_kaynak         |   kumulatif_2026-09_sonrasi_pct | model           | veri_kesimi   |   aylik_lo80 |   aylik_hi80 |   aylik_lo95 |   aylik_hi95 | aralik_olcusu                                        |
|:--------|------------:|-------------:|----------:|:-------------------|--------------------------------:|:----------------|:--------------|-------------:|-------------:|-------------:|-------------:|:-----------------------------------------------------|
| 2026-10 |     3.06124 |      37.6458 |  32.0686  | resmî YTD + tahmin |                         3.06124 | BIRLESIM_mean_3 | 2026-09       |     0.557259 |      5.56521 |     -4.66978 |      10.7923 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2026-11 |     2.89199 |      40.4848 |  35.8881  | resmî YTD + tahmin |                         6.04176 | BIRLESIM_mean_3 | 2026-09       |     0.23323  |      5.55076 |     -4.96849 |      10.7525 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2026-12 |     2.97703 |      39.9294 |  39.9335  | resmî YTD + tahmin |                         9.19866 | BIRLESIM_mean_3 | 2026-09       |     0.256775 |      5.69729 |     -5.08304 |      11.0371 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-01 |     3.25018 |      41.6795 |   3.25018 | tahmin             |                        12.7478  | BIRLESIM_mean_3 | 2026-09       |     0.744098 |      5.75625 |     -4.88571 |      11.3861 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-02 |     2.99143 |      42.0014 |   6.33884 | tahmin             |                        16.1206  | BIRLESIM_mean_3 | 2026-09       |     0.419148 |      5.56372 |     -5.41308 |      11.3959 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-03 |     3.10341 |      43.2852 |   9.63897 | tahmin             |                        19.7243  | BIRLESIM_mean_3 | 2026-09       |     0.40212  |      5.8047  |     -4.89767 |      11.1045 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-04 |     3.07194 |      41.1592 |  13.007   | tahmin             |                        23.4021  | BIRLESIM_mean_3 | 2026-09       |     0.471612 |      5.67227 |     -5.07628 |      11.2202 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-05 |     2.96097 |      42.3993 |  16.3531  | tahmin             |                        27.056   | BIRLESIM_mean_3 | 2026-09       |    -0.399684 |      6.32163 |     -5.1372  |      11.0591 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-06 |     2.9268  |      43.2905 |  19.7585  | tahmin             |                        30.7747  | BIRLESIM_mean_3 | 2026-09       |    -0.544358 |      6.39796 |     -5.21594 |      11.0695 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-07 |     3.06921 |      43.5261 |  23.4342  | tahmin             |                        34.7885  | BIRLESIM_mean_3 | 2026-09       |    -0.444151 |      6.58257 |     -5.00063 |      11.1391 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-08 |     3.7525  |      44.5125 |  28.066   | tahmin             |                        39.8464  | BIRLESIM_mean_3 | 2026-09       |     0.16018  |      7.34481 |     -4.43853 |      11.9435 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-09 |     3.31813 |      44.4867 |  32.3154  | tahmin             |                        44.4867  | BIRLESIM_mean_3 | 2026-09       |    -0.371303 |      7.00756 |     -4.89196 |      11.5282 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |

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

| model                    | hedef   |   n |      MAE |     RMSE |         ME |     MAPE |   en_kotu_hata | en_kotu_donem   |      MASE |   MASE_payda_n |
|:-------------------------|:--------|----:|---------:|---------:|-----------:|---------:|---------------:|:----------------|----------:|---------------:|
| LightGBM_sepet_wtum      | c12     |  14 |  2.05278 |  2.4195  | -1.73814   |  5.32756 |        4.58944 | 2026-02         | 0.0995067 |            104 |
| SARIMA_w120              | c12     |  14 |  3.70877 |  4.85317 | -1.65505   |  9.78192 |        9.43641 | 2026-09         | 0.179679  |            104 |
| LightGBM_w120            | c12     |  14 |  5.62356 |  5.99646 |  5.62356   | 15.1091  |       10.4763  | 2026-09         | 0.27243   |            104 |
| SARIMA_wtum              | c12     |  14 |  6.63584 |  8.80276 |  5.06898   | 17.9766  |       21.3155  | 2025-08         | 0.321555  |            104 |
| Ridge_w120               | c12     |  14 |  6.68489 |  8.13815 |  6.68489   | 18.1398  |       16.8069  | 2025-08         | 0.323916  |            104 |
| Ridge_sepet_wtum         | c12     |  14 |  7.09036 |  9.49559 |  5.41181   | 19.1432  |       20.5772  | 2025-10         | 0.34364   |            104 |
| ElasticNet_wtum          | c12     |  14 |  7.89444 | 10.0377  |  7.88536   | 21.3731  |       21.2788  | 2025-08         | 0.382678  |            104 |
| AutoTheta_wtum           | c12     |  14 |  8.51398 | 11.8668  |  7.12581   | 23.0651  |       29.4909  | 2025-08         | 0.412657  |            104 |
| UCM_llt_seasonal_wtum    | c12     |  14 |  8.90678 | 12.9984  |  8.25858   | 24.2376  |       31.9624  | 2025-08         | 0.431699  |            104 |
| ortalama_6ay             | c12     |  14 | 10.1272  | 13.3828  |  3.98205   | 27.1816  |       35.9428  | 2025-08         | 0.490793  |            104 |
| ETS_damped_seasonal_wtum | c12     |  14 | 10.5588  | 14.1121  | 10.2533    | 28.5797  |       33.1641  | 2025-08         | 0.511807  |            104 |
| ETS_damped_seasonal_w120 | c12     |  14 | 10.9352  | 12.8737  |  1.98612   | 29.267   |       27.2002  | 2026-09         | 0.529759  |            104 |
| Ridge_wtum               | c12     |  14 | 11.0742  | 13.3587  | 11.0426    | 29.941   |       26.5945  | 2025-08         | 0.536798  |            104 |
| ortalama_3ay             | c12     |  14 | 11.2799  | 13.8782  |  1.29469   | 30.0479  |       24.3939  | 2026-09         | 0.546571  |            104 |
| AutoTheta_w120           | c12     |  14 | 11.5447  | 13.5667  |  4.07971   | 30.9675  |       30.4617  | 2026-09         | 0.559203  |            104 |
| naive_mevsimsel_12       | c12     |  14 | 11.5617  | 15.4012  | 10.4592    | 30.9865  |       29.3362  | 2025-08         | 0.560617  |            104 |
| ortalama_12ay            | c12     |  14 | 11.5617  | 15.4012  | 10.4592    | 30.9865  |       29.3362  | 2025-08         | 0.560617  |            104 |
| UCM_llt_seasonal_w120    | c12     |  14 | 11.6661  | 13.5369  |  3.39441   | 31.3079  |       28.7396  | 2026-09         | 0.565183  |            104 |
| AutoTheta_w60            | c12     |  14 | 12.0488  | 14.1149  |  4.84645   | 32.3301  |       27.1167  | 2026-09         | 0.583746  |            104 |
| LightGBM_wtum            | c12     |  14 | 13.8089  | 16.0858  | 13.4619    | 37.3422  |       28.5006  | 2025-08         | 0.669139  |            104 |
| BIRLESIM_median_3        | c12     |  14 | 13.8208  | 15.2848  | 13.8208    | 37.2693  |       22.2158  | 2025-08         | 0.669695  |            104 |
| BIRLESIM_mean_3          | c12     |  14 | 14.4842  | 15.7088  | 14.4842    | 38.9875  |       24.6415  | 2025-08         | 0.701878  |            104 |
| ETS_damped_seasonal_w60  | c12     |  14 | 14.7531  | 18.4927  |  3.03236   | 39.4783  |       38.938   | 2026-09         | 0.714725  |            104 |
| naive_son_ay             | c12     |  14 | 17.4141  | 21.6184  |  3.16015   | 46.7838  |       52.6834  | 2026-09         | 0.84338   |            104 |
| SARIMA_w60               | c12     |  14 | 19.2258  | 19.8732  | 19.2258    | 51.3549  |       30.9082  | 2026-09         | 0.931504  |            104 |
| LightGBM_sepet_wtum      | c6      |  20 |  2.0613  |  2.5304  | -0.945199  | 12.0505  |        5.53682 | 2025-09         | 0.187968  |            114 |
| Ridge_w120               | c6      |  20 |  2.43849 |  3.39172 |  2.09694   | 16.2303  |        8.58534 | 2025-02         | 0.22189   |            114 |
| Ridge_sepet_wtum         | c6      |  20 |  2.54829 |  3.3103  |  0.813755  | 16.3041  |        6.97656 | 2025-02         | 0.23187   |            114 |
| LightGBM_w120            | c6      |  20 |  2.78652 |  3.32033 |  2.35479   | 17.8329  |        7.52638 | 2026-03         | 0.25302   |            114 |
| SARIMA_w120              | c6      |  20 |  3.07517 |  3.75454 | -0.581008  | 18.8172  |        9.84407 | 2026-03         | 0.279666  |            114 |
| ElasticNet_wtum          | c6      |  20 |  3.1686  |  4.57423 |  2.60398   | 21.2007  |       12.1211  | 2025-02         | 0.288298  |            114 |
| SARIMA_wtum              | c6      |  20 |  3.61636 |  4.99206 |  1.56134   | 23.6513  |       13.6152  | 2025-02         | 0.329342  |            114 |
| UCM_llt_seasonal_wtum    | c6      |  20 |  3.86585 |  5.83623 |  2.48686   | 25.7709  |       16.3277  | 2025-02         | 0.352295  |            114 |
| ortalama_12ay            | c6      |  20 |  3.99705 |  6.3342  |  3.15168   | 26.4162  |       15.9864  | 2025-02         | 0.364764  |            114 |
| ETS_damped_seasonal_w120 | c6      |  20 |  4.14017 |  5.02467 |  0.609294  | 25.7386  |       11.8102  | 2026-03         | 0.375576  |            114 |
| Ridge_wtum               | c6      |  20 |  4.14101 |  5.57661 |  3.63456   | 27.2433  |       13.5443  | 2025-02         | 0.3765    |            114 |
| UCM_llt_seasonal_w120    | c6      |  20 |  4.35384 |  5.19696 |  0.98371   | 27.0622  |       12.2357  | 2026-03         | 0.395039  |            114 |
| AutoTheta_wtum           | c6      |  20 |  4.39875 |  5.87698 |  1.98643   | 28.4816  |       16.1484  | 2025-02         | 0.400946  |            114 |
| ETS_damped_seasonal_wtum | c6      |  20 |  4.57195 |  6.41041 |  3.08194   | 30.1126  |       17.4862  | 2025-02         | 0.416602  |            114 |
| AutoTheta_w120           | c6      |  20 |  4.70999 |  5.80202 |  0.0978994 | 29.0194  |       15.4071  | 2026-03         | 0.428204  |            114 |
| ortalama_6ay             | c6      |  20 |  4.87044 |  6.54817 |  0.942134  | 30.9266  |       18.5346  | 2025-02         | 0.443981  |            114 |
| LightGBM_wtum            | c6      |  20 |  4.90154 |  6.59161 |  4.41919   | 32.1945  |       15.5608  | 2025-02         | 0.445652  |            114 |
| BIRLESIM_median_3        | c6      |  20 |  4.93042 |  6.14002 |  4.8193    | 31.8504  |       12.4497  | 2025-02         | 0.447868  |            114 |
| BIRLESIM_mean_3          | c6      |  20 |  5.19511 |  6.40737 |  5.15314   | 33.6553  |       13.5289  | 2025-02         | 0.471897  |            114 |
| AutoTheta_w60            | c6      |  20 |  5.36093 |  6.51857 |  0.338015  | 33.7357  |       14.4882  | 2026-03         | 0.488144  |            114 |
| ortalama_3ay             | c6      |  20 |  5.54941 |  6.64275 | -0.192503  | 34.2504  |       13.4435  | 2026-03         | 0.505323  |            114 |
| ETS_damped_seasonal_w60  | c6      |  20 |  6.64392 |  8.21149 |  1.61857   | 41.267   |       18.0559  | 2026-03         | 0.603037  |            114 |
| naive_mevsimsel_12       | c6      |  20 |  6.84007 |  9.32629 |  5.5565    | 41.7056  |       20.187   | 2025-04         | 0.623816  |            114 |
| SARIMA_w60               | c6      |  20 |  7.47905 |  8.20512 |  7.47905   | 46.3792  |       16.7315  | 2026-03         | 0.679609  |            114 |
| naive_son_ay             | c6      |  20 |  7.67104 |  9.20827 | -0.507876  | 46.6466  |       24.1893  | 2026-03         | 0.696743  |            114 |
| LightGBM_sepet_wtum      | yearend |   5 |  2.62041 |  3.06834 |  1.39019   |  5.48672 |        4.8902  | 2024-12         | 0.294321  |             29 |
| Ridge_w120               | yearend |   5 |  3.39574 |  4.62619 |  3.05641   |  6.72873 |        7.95322 | 2024-12         | 0.382942  |             29 |
| SARIMA_w120              | yearend |   5 |  3.55875 |  4.17263 |  1.51451   |  7.52326 |        6.00236 | 2024-12         | 0.399425  |             29 |
| LightGBM_w120            | yearend |   5 |  3.72279 |  4.2036  |  3.72279   |  7.83936 |        6.07346 | 2024-12         | 0.41796   |             29 |
| Ridge_sepet_wtum         | yearend |   5 |  3.72311 |  4.50868 |  2.60569   |  7.66229 |        6.74514 | 2024-12         | 0.418712  |             29 |
| ElasticNet_wtum          | yearend |   5 |  4.07641 |  5.93654 |  4.07641   |  7.91099 |       10.8806  | 2024-12         | 0.460373  |             29 |
| Ridge_wtum               | yearend |   5 |  4.17837 |  5.87635 |  4.01804   |  8.2666  |       11.0565  | 2024-12         | 0.471253  |             29 |
| AutoTheta_wtum           | yearend |   5 |  4.33913 |  6.59516 |  3.6033    |  8.40535 |       13.1326  | 2024-12         | 0.490106  |             29 |
| ortalama_3ay             | yearend |   5 |  4.43024 |  6.0508  |  3.97573   |  8.88501 |       11.4627  | 2024-12         | 0.499176  |             29 |
| ETS_damped_seasonal_wtum | yearend |   5 |  4.46025 |  7.16646 |  4.31266   |  8.46805 |       14.2665  | 2024-12         | 0.504479  |             29 |
| AutoTheta_w120           | yearend |   5 |  4.51099 |  5.10769 |  3.01579   |  9.50663 |        7.78028 | 2024-12         | 0.506422  |             29 |
| SARIMA_wtum              | yearend |   5 |  5.1257  |  6.88534 |  4.63723   | 10.2454  |       12.802   | 2024-12         | 0.577675  |             29 |
| BIRLESIM_median_3        | yearend |   5 |  5.32211 |  6.47081 |  5.32211   | 10.9447  |       11.1569  | 2024-12         | 0.598574  |             29 |
| UCM_llt_seasonal_wtum    | yearend |   5 |  5.4444  |  7.92917 |  5.11618   | 10.6267  |       15.2095  | 2024-12         | 0.614623  |             29 |
| AutoTheta_w60            | yearend |   5 |  5.45211 |  6.76879 |  3.8854    | 11.2294  |       12.4331  | 2024-12         | 0.613125  |             29 |
| BIRLESIM_mean_3          | yearend |   5 |  5.58328 |  6.85919 |  5.58328   | 11.4831  |       12.2359  | 2024-12         | 0.627943  |             29 |
| UCM_llt_seasonal_w120    | yearend |   5 |  5.74686 |  6.30405 |  1.09027   | 12.6097  |        8.57482 | 2025-12         | 0.643156  |             29 |
| ETS_damped_seasonal_w120 | yearend |   5 |  5.80468 |  6.40347 |  0.92359   | 12.7786  |        9.09541 | 2025-12         | 0.649457  |             29 |
| ortalama_12ay            | yearend |   5 |  5.82413 |  8.10108 |  4.74169   | 11.4737  |       14.6175  | 2024-12         | 0.657064  |             29 |
| ortalama_6ay             | yearend |   5 |  5.99673 |  8.41092 |  5.71429   | 11.981   |       16.8325  | 2024-12         | 0.675863  |             29 |
| LightGBM_wtum            | yearend |   5 |  6.1038  |  8.16965 |  6.1038    | 12.2324  |       15.2558  | 2024-12         | 0.687779  |             29 |
| naive_son_ay             | yearend |   5 |  6.65547 |  7.34825 |  1.05211   | 14.8332  |       11.2899  | 2025-12         | 0.743917  |             29 |
| SARIMA_w60               | yearend |   5 |  6.66655 |  7.19402 |  6.66655   | 14.4472  |       10.4366  | 2024-12         | 0.74681   |             29 |
| naive_mevsimsel_12       | yearend |   5 |  6.9301  |  8.04444 |  2.59653   | 14.4297  |       12.358   | 2024-12         | 0.778706  |             29 |
| ETS_damped_seasonal_w60  | yearend |   5 |  8.4496  |  9.75677 |  0.567235  | 19.1339  |       15.8684  | 2025-12         | 0.943239  |             29 |

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
| nihai test | c12     | %80      |  1        |  14 |            89.962   |         89.962   |       8.40157  | BIRLESIM_mean_3 |
| nihai test | c12     | %95      |  1        |  14 |           190.625   |        190.625   |       8.40157  | BIRLESIM_mean_3 |
| nihai test | c6      | %80      |  1        |  20 |            42.2161  |         42.2161  |       3.72328  | BIRLESIM_mean_3 |
| nihai test | c6      | %95      |  1        |  20 |            99.5613  |         99.5613  |       3.72328  | BIRLESIM_mean_3 |
| nihai test | m1      | %80      |  0.92     |  25 |             4.83053 |          5.21011 |       0.581308 | BIRLESIM_mean_3 |
| nihai test | m1      | %95      |  1        |  25 |            15.462   |         15.462   |       0.581308 | BIRLESIM_mean_3 |
| nihai test | m10     | %80      |  1        |  16 |             7.02672 |          7.02672 |       0.683291 | BIRLESIM_mean_3 |
| nihai test | m10     | %95      |  1        |  16 |            16.1397  |         16.1397  |       0.683291 | BIRLESIM_mean_3 |
| nihai test | m11     | %80      |  1        |  15 |             7.18463 |          7.18463 |       0.685333 | BIRLESIM_mean_3 |
| nihai test | m11     | %95      |  1        |  15 |            16.3821  |         16.3821  |       0.685333 | BIRLESIM_mean_3 |
| nihai test | m12     | %80      |  1        |  14 |             7.37886 |          7.37886 |       0.708407 | BIRLESIM_mean_3 |
| nihai test | m12     | %95      |  1        |  14 |            16.4202  |         16.4202  |       0.708407 | BIRLESIM_mean_3 |
| nihai test | m2      | %80      |  0.875    |  24 |             5.01113 |          5.66231 |       0.614422 | BIRLESIM_mean_3 |
| nihai test | m2      | %95      |  1        |  24 |            15.721   |         15.721   |       0.614422 | BIRLESIM_mean_3 |
| nihai test | m3      | %80      |  0.913043 |  23 |             5.3787  |          5.71449 |       0.649556 | BIRLESIM_mean_3 |
| nihai test | m3      | %95      |  1        |  23 |            16.1201  |         16.1201  |       0.649556 | BIRLESIM_mean_3 |
| nihai test | m4      | %80      |  0.954545 |  22 |             4.93229 |          5.16582 |       0.611036 | BIRLESIM_mean_3 |
| nihai test | m4      | %95      |  1        |  22 |            16.2718  |         16.2718  |       0.611036 | BIRLESIM_mean_3 |
| nihai test | m5      | %80      |  0.904762 |  21 |             4.7021  |          4.89272 |       0.584788 | BIRLESIM_mean_3 |
| nihai test | m5      | %95      |  1        |  21 |            16.809   |         16.809   |       0.584788 | BIRLESIM_mean_3 |
| nihai test | m6      | %80      |  1        |  20 |             5.23339 |          5.23339 |       0.583428 | BIRLESIM_mean_3 |
| nihai test | m6      | %95      |  1        |  20 |            16.0022  |         16.0022  |       0.583428 | BIRLESIM_mean_3 |
| nihai test | m7      | %80      |  0.947368 |  19 |             4.96579 |          4.96587 |       0.578899 | BIRLESIM_mean_3 |
| nihai test | m7      | %95      |  1        |  19 |            16.2964  |         16.2964  |       0.578899 | BIRLESIM_mean_3 |
| nihai test | m8      | %80      |  1        |  18 |             6.72131 |          6.72131 |       0.670461 | BIRLESIM_mean_3 |
| nihai test | m8      | %95      |  1        |  18 |            16.1963  |         16.1963  |       0.670461 | BIRLESIM_mean_3 |
| nihai test | m9      | %80      |  1        |  17 |             6.94232 |          6.94232 |       0.693779 | BIRLESIM_mean_3 |
| nihai test | m9      | %95      |  1        |  17 |            16.2855  |         16.2855  |       0.693779 | BIRLESIM_mean_3 |
| nihai test | yearend | %80      |  1        |   5 |            25.3739  |         25.3739  |       2.63687  | BIRLESIM_mean_3 |
| nihai test | yearend | %95      |  1        |   5 |            50.5254  |         50.5254  |       2.63687  | BIRLESIM_mean_3 |
| nihai test | yoy1    | %80      |  0.96     |  25 |             8.17642 |          8.30002 |       0.867241 | BIRLESIM_mean_3 |
| nihai test | yoy1    | %95      |  1        |  25 |            23.0303  |         23.0303  |       0.867241 | BIRLESIM_mean_3 |
| nihai test | yoy10   | %80      |  1        |  16 |            72.9604  |         72.9604  |       6.91838  | BIRLESIM_mean_3 |
| nihai test | yoy10   | %95      |  1        |  16 |           172.12    |        172.12    |       6.91838  | BIRLESIM_mean_3 |
| nihai test | yoy11   | %80      |  1        |  15 |            78.22    |         78.22    |       7.58524  | BIRLESIM_mean_3 |
| nihai test | yoy11   | %95      |  1        |  15 |           185.576   |        185.576   |       7.58524  | BIRLESIM_mean_3 |
| nihai test | yoy12   | %80      |  1        |  14 |            89.962   |         89.962   |       8.40157  | BIRLESIM_mean_3 |
| nihai test | yoy12   | %95      |  1        |  14 |           190.625   |        190.625   |       8.40157  | BIRLESIM_mean_3 |
| nihai test | yoy2    | %80      |  0.916667 |  24 |            14.8867  |         15.4008  |       1.51264  | BIRLESIM_mean_3 |
| nihai test | yoy2    | %95      |  1        |  24 |            41.6271  |         41.6271  |       1.51264  | BIRLESIM_mean_3 |
| nihai test | yoy3    | %80      |  0.956522 |  23 |            21.7405  |         22.1779  |       2.16779  | BIRLESIM_mean_3 |
| nihai test | yoy3    | %95      |  1        |  23 |            53.0551  |         53.0551  |       2.16779  | BIRLESIM_mean_3 |
| nihai test | yoy4    | %80      |  0.954545 |  22 |            26.7907  |         27.1443  |       2.66204  | BIRLESIM_mean_3 |
| nihai test | yoy4    | %95      |  1        |  22 |            68.4137  |         68.4137  |       2.66204  | BIRLESIM_mean_3 |
| nihai test | yoy5    | %80      |  1        |  21 |            35.1611  |         35.1611  |       3.36952  | BIRLESIM_mean_3 |
| nihai test | yoy5    | %95      |  1        |  21 |            88.0134  |         88.0134  |       3.36952  | BIRLESIM_mean_3 |
| nihai test | yoy6    | %80      |  1        |  20 |            51.4034  |         51.4034  |       4.45979  | BIRLESIM_mean_3 |
| nihai test | yoy6    | %95      |  1        |  20 |           114.669   |        114.669   |       4.45979  | BIRLESIM_mean_3 |
| nihai test | yoy7    | %80      |  1        |  19 |            59.9461  |         59.9461  |       5.23258  | BIRLESIM_mean_3 |
| nihai test | yoy7    | %95      |  1        |  19 |           126.929   |        126.929   |       5.23258  | BIRLESIM_mean_3 |
| nihai test | yoy8    | %80      |  1        |  18 |            61.4074  |         61.4074  |       5.68935  | BIRLESIM_mean_3 |
| nihai test | yoy8    | %95      |  1        |  18 |           145.91    |        145.91    |       5.68935  | BIRLESIM_mean_3 |
| nihai test | yoy9    | %80      |  1        |  17 |            64.3724  |         64.3724  |       6.24561  | BIRLESIM_mean_3 |
| nihai test | yoy9    | %95      |  1        |  17 |           164.179   |        164.179   |       6.24561  | BIRLESIM_mean_3 |

## Sınırlar

- Geçmiş veri sürümleri yoktur; değerlendirme *son veri sürümüyle geriye dönük test*tir.
- 24 aylık nihai testte yalnızca iki tamamlanmış yılsonu vardır.
- "En iyi model", bu veri ve bu protokolde en başarılı adaydır; gelecek performans garantisi değildir.
- TimesFM 3.0 ağırlıkları ticari/üretim kullanımına kapalıdır (`timesfm-non-commercial-license-v1.0`).
