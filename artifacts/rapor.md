# KKTC TÜFE Tahmin Raporu (veri kesimi: 2026-10)

**Seçilen model:** `BIRLESIM_mean_3` · aile: ensemble · eğitim penceresi: üye modellerin kendi pencereleri · dönüşüm: log
**Geliştirme seçim skoru S = 7.8509 yüzde puan** (S = 0.6·MAE_yılsonu + 0.3·MAE_6ay + 0.1·MAE_12ay)
**Seçim kuralı:** En iyi skora göre göreli farkı %2'den küçük adaylar berabere sayıldı; ardından basitlik, sonra hesaplama maliyeti.
**Donduruldu:** 2026-11-06T07:03:35.527795+00:00 (nihai holdout açılmadan önce)

## ⚠ Eksik zorunlu bileşen

TimesFM 3 çalıştırılamadı: TimesFM 3 kodu içe aktarılamadı: ModuleNotFoundError: No module named 'timesfm3'. Kurulum: pip install 'timesfm[torch]' veya pip install 'git+https://github.com/google-research/timesfm.git'
Bu nedenle karşılaştırma **tamamlanmış sayılmaz**.

## Dönem tahminleri

| olcu                                           | tanim                                                         |   deger_pct | donem             |
|:-----------------------------------------------|:--------------------------------------------------------------|------------:|:------------------|
| 2026 yılsonu enflasyonu (Ara 2026/Ara 2025)    | Gerçekleşmiş YTD (%29.5198, 2026-10) + 2 aylık tahmin         |     35.9154 | 2026-01 → 2026-12 |
| Gelecek 6 ayın BİLEŞİK enflasyonu              | Başlangıç sonrası 6 ayın bileşiği (yıllık enflasyon DEĞİLDİR) |     18.1826 | 2026-11 → 2027-04 |
| Gelecek 12 ayın BİLEŞİK enflasyonu             | Başlangıç sonrası 12 ayın bileşiği                            |     41.2062 | 2026-11 → 2027-10 |
| Temmuz–Aralık 2026 bileşik değişimi (2. dönem) | 4 ay gerçekleşme + 2 ay tahmin                                |     16.2138 | 2026-07 → 2026-12 |
| Ocak–Haziran 2027 bileşik değişimi (1. dönem)  | Tamamı tahmin (takvim yarıyılı)                               |     19.3592 | 2027-01 → 2027-06 |
| 2027-02 YILLIK enflasyonu                      | 12 aylık geriye dönük değişim (6 aylık bileşik DEĞİLDİR)      |     37.6218 | 2026-03 → 2027-02 |

## Aylık tahminler

| tarih   |   aylik_pct |   yillik_pct |   ytd_pct | ytd_kaynak         |   kumulatif_2026-10_sonrasi_pct | model           | veri_kesimi   |   aylik_lo80 |   aylik_hi80 |   aylik_lo95 |   aylik_hi95 | aralik_olcusu                                        |
|:--------|------------:|-------------:|----------:|:-------------------|--------------------------------:|:----------------|:--------------|-------------:|-------------:|-------------:|-------------:|:-----------------------------------------------------|
| 2026-11 |     2.21792 |      36.8709 |  32.3924  | resmî YTD + tahmin |                         2.21792 | BIRLESIM_mean_3 | 2026-10       |  -0.286058   |      4.7219  |     -5.5131  |      9.94893 | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2026-12 |     2.661   |      35.9114 |  35.9154  | resmî YTD + tahmin |                         4.93793 | BIRLESIM_mean_3 | 2026-10       |   0.00223276 |      5.31976 |     -5.19948 |     10.5215  | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-01 |     2.95632 |      37.2196 |   2.95632 | tahmin             |                         8.04023 | BIRLESIM_mean_3 | 2026-10       |   0.23606    |      5.67657 |     -5.10375 |     11.0164  | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-02 |     3.05917 |      37.6218 |   6.10592 | tahmin             |                        11.3454  | BIRLESIM_mean_3 | 2026-10       |   0.553008   |      5.56533 |     -5.07671 |     11.195   | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-03 |     3.09627 |      38.8564 |   9.39125 | tahmin             |                        14.7929  | BIRLESIM_mean_3 | 2026-10       |   0.523987   |      5.66856 |     -5.30824 |     11.5008  | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-04 |     2.95289 |      36.6381 |  12.6215  | tahmin             |                        18.1826  | BIRLESIM_mean_3 | 2026-10       |   0.2516     |      5.65418 |     -5.04819 |     10.954   | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-05 |     3.07549 |      37.9919 |  16.0851  | tahmin             |                        21.8173  | BIRLESIM_mean_3 | 2026-10       |   0.475163   |      5.67582 |     -5.07273 |     11.2237  | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-06 |     2.82045 |      38.7119 |  19.3592  | tahmin             |                        25.2531  | BIRLESIM_mean_3 | 2026-10       |  -0.540201   |      6.18111 |     -5.27772 |     10.9186  | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-07 |     2.89826 |      38.7096 |  22.8186  | tahmin             |                        28.8833  | BIRLESIM_mean_3 | 2026-10       |  -0.572896   |      6.36942 |     -5.24448 |     11.041   | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-08 |     3.27464 |      39.0197 |  26.8405  | tahmin             |                        33.1038  | BIRLESIM_mean_3 | 2026-10       |  -0.23872    |      6.788   |     -4.7952  |     11.3445  | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-09 |     3.08726 |      38.6842 |  30.7564  | tahmin             |                        37.213   | BIRLESIM_mean_3 | 2026-10       |  -0.505058   |      6.67958 |     -5.10377 |     11.2783  | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |
| 2027-10 |     2.91018 |      41.2062 |  34.5616  | tahmin             |                        41.2062  | BIRLESIM_mean_3 | 2026-10       |  -0.779253   |      6.59961 |     -5.29991 |     11.1203  | AYLIK yüzde değişim (bileşik dönem aralığı değildir) |

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
| LightGBM_sepet_wtum      | c12     |  15 |  2.00064 |  2.36037 | -1.53755   |  5.21449 |        4.58944 | 2026-02         | 0.0969423 |            104 |
| SARIMA_w120              | c12     |  15 |  3.53314 |  4.6968  | -1.61634   |  9.33449 |        9.43641 | 2026-09         | 0.171141  |            104 |
| LightGBM_w120            | c12     |  15 |  5.92789 |  6.36246 |  5.92789   | 16.0431  |       10.4763  | 2026-09         | 0.286897  |            104 |
| SARIMA_wtum              | c12     |  15 |  6.59232 |  8.64345 |  5.12992   | 17.9181  |       21.3155  | 2025-08         | 0.319279  |            104 |
| Ridge_w120               | c12     |  15 |  6.76823 |  8.12477 |  6.76823   | 18.4424  |       16.8069  | 2025-08         | 0.327734  |            104 |
| Ridge_sepet_wtum         | c12     |  15 |  6.85819 |  9.22079 |  5.29155   | 18.5544  |       20.5772  | 2025-10         | 0.332284  |            104 |
| ElasticNet_wtum          | c12     |  15 |  7.65969 |  9.76287 |  7.65121   | 20.7814  |       21.2788  | 2025-08         | 0.371171  |            104 |
| AutoTheta_wtum           | c12     |  15 |  8.24254 | 11.5217  |  6.94691   | 22.3738  |       29.4909  | 2025-08         | 0.399374  |            104 |
| UCM_llt_seasonal_wtum    | c12     |  15 |  8.7166  | 12.6545  |  8.11161   | 23.7753  |       31.9624  | 2025-08         | 0.422308  |            104 |
| ortalama_6ay             | c12     |  15 |  9.78577 | 12.9935  |  4.05027   | 26.3232  |       35.9428  | 2025-08         | 0.474103  |            104 |
| ETS_damped_seasonal_wtum | c12     |  15 | 10.2548  | 13.7213  |  9.96964   | 27.8172  |       33.1641  | 2025-08         | 0.496896  |            104 |
| Ridge_wtum               | c12     |  15 | 10.7489  | 13.0045  | 10.7194    | 29.1252  |       26.5945  | 2025-08         | 0.520849  |            104 |
| ETS_damped_seasonal_w120 | c12     |  15 | 10.823   | 12.6646  |  2.47055   | 29.0788  |       27.2002  | 2026-09         | 0.524073  |            104 |
| naive_mevsimsel_12       | c12     |  15 | 10.8802  | 14.883   |  9.85121   | 29.176   |       29.3362  | 2025-08         | 0.527532  |            104 |
| ortalama_12ay            | c12     |  15 | 10.8802  | 14.883   |  9.85121   | 29.176   |       29.3362  | 2025-08         | 0.527532  |            104 |
| AutoTheta_w120           | c12     |  15 | 11.0975  | 13.166   |  4.13012   | 29.8244  |       30.4617  | 2026-09         | 0.53741   |            104 |
| ortalama_3ay             | c12     |  15 | 11.3253  | 13.7587  |  2.00579   | 30.3238  |       24.3939  | 2026-09         | 0.548439  |            104 |
| AutoTheta_w60            | c12     |  15 | 11.415   | 13.6521  |  4.69282   | 30.6591  |       27.1167  | 2026-09         | 0.55297   |            104 |
| UCM_llt_seasonal_w120    | c12     |  15 | 11.6511  | 13.4073  |  3.93083   | 31.4006  |       28.7396  | 2026-09         | 0.564143  |            104 |
| LightGBM_wtum            | c12     |  15 | 13.6956  | 15.8518  | 13.3717    | 37.16    |       28.5006  | 2025-08         | 0.663311  |            104 |
| BIRLESIM_median_3        | c12     |  15 | 13.8531  | 15.2215  | 13.8531    | 37.5105  |       22.2158  | 2025-08         | 0.670864  |            104 |
| BIRLESIM_mean_3          | c12     |  15 | 14.405   | 15.5596  | 14.405     | 38.9217  |       24.6415  | 2025-08         | 0.697666  |            104 |
| ETS_damped_seasonal_w60  | c12     |  15 | 15.0333  | 18.524   |  4.09395   | 40.4582  |       38.938   | 2026-09         | 0.727784  |            104 |
| naive_son_ay             | c12     |  15 | 17.6586  | 21.583   |  1.54407   | 47.6816  |       52.6834  | 2026-09         | 0.854667  |            104 |
| SARIMA_w60               | c12     |  15 | 19.4114  | 20.0227  | 19.4114    | 52.125   |       30.9082  | 2026-09         | 0.939893  |            104 |
| LightGBM_sepet_wtum      | c6      |  21 |  2.00305 |  2.47618 | -0.860282  | 11.7322  |        5.53682 | 2025-09         | 0.18276   |            115 |
| Ridge_w120               | c6      |  21 |  2.54902 |  3.46911 |  2.22374   | 16.9089  |        8.58534 | 2025-02         | 0.232581  |            115 |
| Ridge_sepet_wtum         | c6      |  21 |  2.59548 |  3.32156 |  0.943538  | 16.607   |        6.97656 | 2025-02         | 0.236635  |            115 |
| LightGBM_w120            | c6      |  21 |  2.88079 |  3.40314 |  2.46962   | 18.4371  |        7.52638 | 2026-03         | 0.262258  |            115 |
| SARIMA_w120              | c6      |  21 |  3.20458 |  3.87599 | -0.277493  | 19.6876  |        9.84407 | 2026-03         | 0.29222   |            115 |
| ElasticNet_wtum          | c6      |  21 |  3.2058  |  4.54644 |  2.66806   | 21.3956  |       12.1211  | 2025-02         | 0.29221   |            115 |
| SARIMA_wtum              | c6      |  21 |  3.60289 |  4.92575 |  1.64572   | 23.5415  |       13.6152  | 2025-02         | 0.328546  |            115 |
| UCM_llt_seasonal_wtum    | c6      |  21 |  3.78088 |  5.71366 |  2.46756   | 25.1785  |       16.3277  | 2025-02         | 0.344815  |            115 |
| ortalama_12ay            | c6      |  21 |  3.8981  |  6.19572 |  3.09299   | 25.7436  |       15.9864  | 2025-02         | 0.355966  |            115 |
| Ridge_wtum               | c6      |  21 |  4.16112 |  5.53257 |  3.67879   | 27.3376  |       13.5443  | 2025-02         | 0.378952  |            115 |
| ETS_damped_seasonal_w120 | c6      |  21 |  4.21343 |  5.05773 |  0.850693  | 26.2446  |       11.8102  | 2026-03         | 0.383054  |            115 |
| AutoTheta_wtum           | c6      |  21 |  4.33547 |  5.77434 |  2.03802   | 28.0614  |       16.1484  | 2025-02         | 0.395564  |            115 |
| UCM_llt_seasonal_w120    | c6      |  21 |  4.44784 |  5.25633 |  1.23819   | 27.7031  |       12.2357  | 2026-03         | 0.404489  |            115 |
| ETS_damped_seasonal_wtum | c6      |  21 |  4.49802 |  6.29052 |  3.07896   | 29.5994  |       17.4862  | 2025-02         | 0.41025   |            115 |
| ortalama_6ay             | c6      |  21 |  4.69282 |  6.3952  |  0.951575  | 29.8017  |       18.5346  | 2025-02         | 0.427932  |            115 |
| AutoTheta_w120           | c6      |  21 |  4.8189  |  5.86446 |  0.426436  | 29.7712  |       15.4071  | 2026-03         | 0.439064  |            115 |
| LightGBM_wtum            | c6      |  21 |  4.93089 |  6.54448 |  4.47151   | 32.344   |       15.5608  | 2025-02         | 0.449075  |            115 |
| BIRLESIM_median_3        | c6      |  21 |  4.97847 |  6.13062 |  4.87264   | 32.1448  |       12.4497  | 2025-02         | 0.453067  |            115 |
| BIRLESIM_mean_3          | c6      |  21 |  5.31993 |  6.48141 |  5.27996   | 34.4361  |       13.5289  | 2025-02         | 0.484335  |            115 |
| AutoTheta_w60            | c6      |  21 |  5.35321 |  6.46184 |  0.569483  | 33.7146  |       14.4882  | 2026-03         | 0.488118  |            115 |
| ortalama_3ay             | c6      |  21 |  5.52615 |  6.57606 |  0.0576638 | 34.1627  |       13.4435  | 2026-03         | 0.503863  |            115 |
| ETS_damped_seasonal_w60  | c6      |  21 |  6.40185 |  8.02083 |  1.6158    | 39.7777  |       18.0559  | 2026-03         | 0.58129   |            115 |
| naive_mevsimsel_12       | c6      |  21 |  6.64308 |  9.12062 |  5.42064   | 40.5439  |       20.187   | 2025-04         | 0.606183  |            115 |
| SARIMA_w60               | c6      |  21 |  7.76873 |  8.5368  |  7.76873   | 48.3063  |       16.7315  | 2026-03         | 0.707818  |            115 |
| naive_son_ay             | c6      |  21 |  8.04585 |  9.60506 |  0.256408  | 49.1647  |       24.1893  | 2026-03         | 0.732978  |            115 |
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
| nihai test | c12     | %80      |  1        |  15 |            89.962   |         89.962   |       8.38573  | BIRLESIM_mean_3 |
| nihai test | c12     | %95      |  1        |  15 |           190.625   |        190.625   |       8.38573  | BIRLESIM_mean_3 |
| nihai test | c6      | %80      |  1        |  21 |            42.2161  |         42.2161  |       3.74824  | BIRLESIM_mean_3 |
| nihai test | c6      | %95      |  1        |  21 |            99.5613  |         99.5613  |       3.74824  | BIRLESIM_mean_3 |
| nihai test | m1      | %80      |  0.923077 |  26 |             4.83735 |          5.20234 |       0.587902 | BIRLESIM_mean_3 |
| nihai test | m1      | %95      |  1        |  26 |            15.462   |         15.462   |       0.587902 | BIRLESIM_mean_3 |
| nihai test | m10     | %80      |  1        |  17 |             7.02672 |          7.02672 |       0.695967 | BIRLESIM_mean_3 |
| nihai test | m10     | %95      |  1        |  17 |            16.1397  |         16.1397  |       0.695967 | BIRLESIM_mean_3 |
| nihai test | m11     | %80      |  1        |  16 |             7.18463 |          7.18463 |       0.695309 | BIRLESIM_mean_3 |
| nihai test | m11     | %95      |  1        |  16 |            16.3821  |         16.3821  |       0.695309 | BIRLESIM_mean_3 |
| nihai test | m12     | %80      |  1        |  15 |             7.37886 |          7.37886 |       0.722909 | BIRLESIM_mean_3 |
| nihai test | m12     | %95      |  1        |  15 |            16.4202  |         16.4202  |       0.722909 | BIRLESIM_mean_3 |
| nihai test | m2      | %80      |  0.88     |  25 |             5.02338 |          5.64852 |       0.621659 | BIRLESIM_mean_3 |
| nihai test | m2      | %95      |  1        |  25 |            15.721   |         15.721   |       0.621659 | BIRLESIM_mean_3 |
| nihai test | m3      | %80      |  0.916667 |  24 |             5.38128 |          5.70307 |       0.656174 | BIRLESIM_mean_3 |
| nihai test | m3      | %95      |  1        |  24 |            16.1201  |         16.1201  |       0.656174 | BIRLESIM_mean_3 |
| nihai test | m4      | %80      |  0.956522 |  23 |             4.93576 |          5.15914 |       0.621479 | BIRLESIM_mean_3 |
| nihai test | m4      | %95      |  1        |  23 |            16.2718  |         16.2718  |       0.621479 | BIRLESIM_mean_3 |
| nihai test | m5      | %80      |  0.909091 |  22 |             4.72222 |          4.90416 |       0.596616 | BIRLESIM_mean_3 |
| nihai test | m5      | %95      |  1        |  22 |            16.809   |         16.809   |       0.596616 | BIRLESIM_mean_3 |
| nihai test | m6      | %80      |  1        |  21 |             5.24144 |          5.24144 |       0.596644 | BIRLESIM_mean_3 |
| nihai test | m6      | %95      |  1        |  21 |            16.0022  |         16.0022  |       0.596644 | BIRLESIM_mean_3 |
| nihai test | m7      | %80      |  0.95     |  20 |             4.97753 |          4.97761 |       0.588838 | BIRLESIM_mean_3 |
| nihai test | m7      | %95      |  1        |  20 |            16.2964  |         16.2964  |       0.588838 | BIRLESIM_mean_3 |
| nihai test | m8      | %80      |  1        |  19 |             6.72131 |          6.72131 |       0.68659  | BIRLESIM_mean_3 |
| nihai test | m8      | %95      |  1        |  19 |            16.1963  |         16.1963  |       0.68659  | BIRLESIM_mean_3 |
| nihai test | m9      | %80      |  1        |  18 |             6.94232 |          6.94232 |       0.707031 | BIRLESIM_mean_3 |
| nihai test | m9      | %95      |  1        |  18 |            16.2855  |         16.2855  |       0.707031 | BIRLESIM_mean_3 |
| nihai test | yearend | %80      |  1        |   5 |            25.3739  |         25.3739  |       2.63687  | BIRLESIM_mean_3 |
| nihai test | yearend | %95      |  1        |   5 |            50.5254  |         50.5254  |       2.63687  | BIRLESIM_mean_3 |
| nihai test | yoy1    | %80      |  0.961538 |  26 |             8.1779  |          8.29675 |       0.875817 | BIRLESIM_mean_3 |
| nihai test | yoy1    | %95      |  1        |  26 |            23.0303  |         23.0303  |       0.875817 | BIRLESIM_mean_3 |
| nihai test | yoy10   | %80      |  1        |  17 |            72.9604  |         72.9604  |       6.90878  | BIRLESIM_mean_3 |
| nihai test | yoy10   | %95      |  1        |  17 |           172.12    |        172.12    |       6.90878  | BIRLESIM_mean_3 |
| nihai test | yoy11   | %80      |  1        |  16 |            78.22    |         78.22    |       7.51397  | BIRLESIM_mean_3 |
| nihai test | yoy11   | %95      |  1        |  16 |           185.576   |        185.576   |       7.51397  | BIRLESIM_mean_3 |
| nihai test | yoy12   | %80      |  1        |  15 |            89.962   |         89.962   |       8.38573  | BIRLESIM_mean_3 |
| nihai test | yoy12   | %95      |  1        |  15 |           190.625   |        190.625   |       8.38573  | BIRLESIM_mean_3 |
| nihai test | yoy2    | %80      |  0.92     |  25 |            14.9092  |         15.4027  |       1.5144   | BIRLESIM_mean_3 |
| nihai test | yoy2    | %95      |  1        |  25 |            41.6271  |         41.6271  |       1.5144   | BIRLESIM_mean_3 |
| nihai test | yoy3    | %80      |  0.958333 |  24 |            21.7608  |         22.1799  |       2.16273  | BIRLESIM_mean_3 |
| nihai test | yoy3    | %95      |  1        |  24 |            53.0551  |         53.0551  |       2.16273  | BIRLESIM_mean_3 |
| nihai test | yoy4    | %80      |  0.956522 |  23 |            26.807   |         27.1452  |       2.65688  | BIRLESIM_mean_3 |
| nihai test | yoy4    | %95      |  1        |  23 |            68.4137  |         68.4137  |       2.65688  | BIRLESIM_mean_3 |
| nihai test | yoy5    | %80      |  1        |  22 |            35.1611  |         35.1611  |       3.36861  | BIRLESIM_mean_3 |
| nihai test | yoy5    | %95      |  1        |  22 |            88.0134  |         88.0134  |       3.36861  | BIRLESIM_mean_3 |
| nihai test | yoy6    | %80      |  1        |  21 |            51.4034  |         51.4034  |       4.48685  | BIRLESIM_mean_3 |
| nihai test | yoy6    | %95      |  1        |  21 |           114.669   |        114.669   |       4.48685  | BIRLESIM_mean_3 |
| nihai test | yoy7    | %80      |  1        |  20 |            59.9461  |         59.9461  |       5.19297  | BIRLESIM_mean_3 |
| nihai test | yoy7    | %95      |  1        |  20 |           126.929   |        126.929   |       5.19297  | BIRLESIM_mean_3 |
| nihai test | yoy8    | %80      |  1        |  19 |            61.4074  |         61.4074  |       5.70496  | BIRLESIM_mean_3 |
| nihai test | yoy8    | %95      |  1        |  19 |           145.91    |        145.91    |       5.70496  | BIRLESIM_mean_3 |
| nihai test | yoy9    | %80      |  1        |  18 |            64.3724  |         64.3724  |       6.21846  | BIRLESIM_mean_3 |
| nihai test | yoy9    | %95      |  1        |  18 |           164.179   |        164.179   |       6.21846  | BIRLESIM_mean_3 |

## Sınırlar

- Geçmiş veri sürümleri yoktur; değerlendirme *son veri sürümüyle geriye dönük test*tir.
- 24 aylık nihai testte yalnızca iki tamamlanmış yılsonu vardır.
- "En iyi model", bu veri ve bu protokolde en başarılı adaydır; gelecek performans garantisi değildir.
- TimesFM 3.0 ağırlıkları ticari/üretim kullanımına kapalıdır (`timesfm-non-commercial-license-v1.0`).
