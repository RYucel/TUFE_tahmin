from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from pmdarima import auto_arima
from prophet import Prophet
from sklearn.metrics import mean_absolute_error
import warnings

warnings.filterwarnings("ignore") # Özellikle Prophet ve auto_arima uyarılarını bastırmak için

app = Flask(__name__)
CORS(app)  # Geliştirme sırasında frontend'den erişim için

DATA_FILE = 'data.csv'
VALIDATION_MONTHS = 3
PREDICTION_HORIZONS = [3, 6, 12] # Gelecek 3, 6, 12 ay

def load_and_preprocess_data():
    try:
        # BOM karakterini temizlemek için utf-8-sig kullanıyoruz
        df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        df = df.sort_values('Date')
        df.set_index('Date', inplace=True)
        df['CPI'] = pd.to_numeric(df['CPI'], errors='coerce')
        df.dropna(subset=['CPI'], inplace=True)
        return df['CPI']
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def train_and_evaluate_model(series, model_name, train_set, val_set):
    model = None
    predictions = None
    mae = float('inf')

    try:
        if model_name == "SARIMA":
            # pmdarima's auto_arima, mevsimselliği (m=12) ve durağanlaştırmayı kendi bulur
            model = auto_arima(train_set, seasonal=True, m=12,
                               suppress_warnings=True, stepwise=True,
                               error_action='ignore')
            predictions = model.predict(n_periods=len(val_set))
        
        elif model_name == "Prophet":
            prophet_train_df = train_set.reset_index()
            prophet_train_df.columns = ['ds', 'y']
            model = Prophet()
            model.fit(prophet_train_df)
            future_dates = model.make_future_dataframe(periods=len(val_set), freq='MS') # Aylık frekans
            prophet_preds_df = model.predict(future_dates)
            predictions = prophet_preds_df['yhat'].iloc[-len(val_set):].values

        elif model_name == "ETS":
            # Trend ve mevsimsellik için farklı kombinasyonlar denenebilir
            # Additive trend, Additive seasonality, Damped trend
            model = ExponentialSmoothing(train_set, seasonal_periods=12,
                                         trend='add', seasonal='add', damped_trend=True)
            fitted_model = model.fit()
            predictions = fitted_model.predict(start=val_set.index[0], end=val_set.index[-1])

        if predictions is not None:
            mae = mean_absolute_error(val_set.values, predictions)
            # print(f"Model: {model_name}, Validation MAE: {mae}")

    except Exception as e:
        print(f"Error training/evaluating {model_name}: {e}")
    
    return model, mae

@app.route('/api/predict', methods=['GET'])
def get_predictions():
    series = load_and_preprocess_data()
    if series is None or len(series) < (VALIDATION_MONTHS + 12): # En az 1 yıl veri + validasyon
        return jsonify({"error": "Not enough data to make predictions"}), 500

    # Veriyi eğitim ve validasyon setlerine ayır
    train_set = series[:-VALIDATION_MONTHS]
    val_set = series[-VALIDATION_MONTHS:]

    models_to_try = {
        "SARIMA": None,
        "Prophet": None,
        "ETS": None
    }
    
    best_mae = float('inf')
    best_model_name = None
    
    for name in models_to_try:
        _, mae = train_and_evaluate_model(series, name, train_set, val_set)
        if mae < best_mae:
            best_mae = mae
            best_model_name = name
    
    if best_model_name is None:
        return jsonify({"error": "Could not train any model successfully"}), 500

    # En iyi modeli tüm veriyle yeniden eğit (validasyon seti dahil)
    # ve gelecek tahminleri yap
    final_model = None
    future_predictions_abs = {}

    last_actual_date = series.index[-1]
    last_actual_cpi = series.iloc[-1]

    try:
        if best_model_name == "SARIMA":
            final_model = auto_arima(series, seasonal=True, m=12,
                                     suppress_warnings=True, stepwise=True,
                                     error_action='ignore')
            preds = final_model.predict(n_periods=max(PREDICTION_HORIZONS))
            for h in PREDICTION_HORIZONS:
                future_predictions_abs[h] = preds[h-1]
        
        elif best_model_name == "Prophet":
            prophet_full_df = series.reset_index()
            prophet_full_df.columns = ['ds', 'y']
            final_model = Prophet()
            final_model.fit(prophet_full_df)
            future_dates = final_model.make_future_dataframe(periods=max(PREDICTION_HORIZONS), freq='MS')
            prophet_preds_df = final_model.predict(future_dates)
            for h in PREDICTION_HORIZONS:
                future_predictions_abs[h] = prophet_preds_df['yhat'].iloc[-(max(PREDICTION_HORIZONS) - h + 1)]
        
        elif best_model_name == "ETS":
            final_model = ExponentialSmoothing(series, seasonal_periods=12,
                                               trend='add', seasonal='add', damped_trend=True)
            fitted_final_model = final_model.fit()
            preds = fitted_final_model.predict(start=series.index[-1] + pd.DateOffset(months=1), 
                                               end=series.index[-1] + pd.DateOffset(months=max(PREDICTION_HORIZONS)))
            for h in PREDICTION_HORIZONS:
                future_predictions_abs[h] = preds.iloc[h-1]

    except Exception as e:
        return jsonify({"error": f"Error making final predictions with {best_model_name}: {e}"}), 500


    predictions_pct_change = {}
    for h, abs_val in future_predictions_abs.items():
        pct_change = ((abs_val - last_actual_cpi) / last_actual_cpi) * 100
        predictions_pct_change[h] = round(pct_change, 2)
        future_predictions_abs[h] = round(abs_val, 2)


    # Geçmiş verileri de gönder (son 24 ay)
    historical_data_points = 24 
    historical_series = series.iloc[-historical_data_points:]
    
    historical_for_chart = {
        "labels": [d.strftime('%Y-%m') for d in historical_series.index],
        "values": [round(v, 2) for v in historical_series.values]
    }
    
    # Tahmin edilen gelecek ayları da grafiğe ekle
    predicted_labels = []
    predicted_values = []
    current_pred_date = last_actual_date
    
    # Sadece 3, 6, 12. ayları değil, tüm aradaki ayları tahmin etmeye çalışalım (gösterim için)
    # Bu kısım final_model'in tüm periyotlar için tahmin yapabilmesine bağlı
    all_future_preds_for_chart = []
    if best_model_name == "SARIMA":
        all_future_preds_for_chart = final_model.predict(n_periods=12)
    elif best_model_name == "Prophet":
        future_df_chart = final_model.make_future_dataframe(periods=12, freq='MS')
        prophet_preds_df_chart = final_model.predict(future_df_chart)
        all_future_preds_for_chart = prophet_preds_df_chart['yhat'].iloc[-12:].values
    elif best_model_name == "ETS":
        # ETS'de fitted_final_model.predict() ile 12 periyotluk tahmin alınıyor
        all_future_preds_for_chart = fitted_final_model.predict(
            start=series.index[-1] + pd.DateOffset(months=1),
            end=series.index[-1] + pd.DateOffset(months=12)
        ).values


    for i in range(12): # Gelecek 12 ay için
        current_pred_date += pd.DateOffset(months=1)
        predicted_labels.append(current_pred_date.strftime('%Y-%m'))
        if i < len(all_future_preds_for_chart):
             predicted_values.append(round(all_future_preds_for_chart[i], 2))
        else: # Eğer model 12 ayın hepsini döndürmediyse (olmamalı ama tedbir)
             predicted_values.append(None)


    return jsonify({
        "last_actual_cpi": round(last_actual_cpi, 2),
        "last_actual_date": last_actual_date.strftime('%d/%m/%Y'),
        "predictions_pct_change": predictions_pct_change,
        "predictions_absolute": future_predictions_abs,
        "best_model_name": best_model_name,
        "best_model_mae_validation": round(best_mae, 2),
        "historical_data_for_chart": historical_for_chart,
        "predicted_data_for_chart": {
            "labels": predicted_labels,
            "values": predicted_values
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001) # Portu frontend ile çakışmayacak şekilde ayarlayın