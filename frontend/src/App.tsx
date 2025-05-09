// frontend/src/App.tsx
import React, { useState, useEffect } from 'react';
import './App.css'; // Your main App CSS
import PredictionDisplay from './components/PredictionDisplay';
import HistoricalChart from './components/HistoricalChart';
import { PredictionData, ApiErrorResponse } from './types/api'; // Import defined types

function App() {
  const [predictionData, setPredictionData] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch('/api/predict'); 
        
        if (!response.ok) {
          let errorData: ApiErrorResponse | { message?: string } | string = `HTTP error! status: ${response.status}`;
          try {
            // Try to parse as JSON, could be our ApiErrorResponse or other structure
            const parsedError = await response.json();
            if (typeof parsedError === 'object' && parsedError !== null && 'error' in parsedError) {
                 errorData = (parsedError as ApiErrorResponse).error;
            } else if (typeof parsedError === 'object' && parsedError !== null && 'message' in parsedError) {
                 errorData = (parsedError as { message: string }).message;
            } else {
                errorData = JSON.stringify(parsedError); // Fallback for unknown error structure
            }
          } catch (e) {
            // If parsing fails, use the status text or a generic message
            errorData = response.statusText || `HTTP error! status: ${response.status}`;
          }
          throw new Error(typeof errorData === 'string' ? errorData : 'Bilinmeyen bir sunucu hatası oluştu.');
        }
        
        const data: PredictionData = await response.json();
        setPredictionData(data);
      } catch (e: any) { // Catch 'any' or 'unknown' and assert type
        console.error("Tahminler alınırken hata oluştu:", e);
        setError(e.message || 'Veri alınırken bir sorun oluştu.');
      } finally {
        setLoading(false);
      }
    };

    fetchPredictions();
  }, []);

  if (loading) {
    return <div className="loading">Tahminler yükleniyor, lütfen bekleyin... (Bu işlem birkaç saniye sürebilir)</div>;
  }

  if (error) {
    return <div className="error">Hata: {error}</div>;
  }

  if (!predictionData) {
    return <div className="error">Tahmin verisi bulunamadı. Lütfen daha sonra tekrar deneyin.</div>;
  }
  
  const { 
    last_actual_cpi, 
    last_actual_date, 
    predictions_pct_change,
    predictions_absolute,
    best_model_name,
    best_model_mae_validation,
    historical_data_for_chart,
    predicted_data_for_chart
  } = predictionData;

  return (
    <div className="container">
      <header className="App-header">
        <h1>TÜFE CPI Tahmin Uygulaması</h1>
      </header>
      
      <div className="last-known">
        Son Bilinen TÜFE ({last_actual_date}): <strong>{last_actual_cpi.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong>
      </div>

      <PredictionDisplay 
        predictionsPct={predictions_pct_change} 
        predictionsAbs={predictions_absolute}
      />
      
      <div className="model-info">
        Kullanılan En İyi Model: {best_model_name} (Validasyon MAE: {best_model_mae_validation.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })})
      </div>

      <HistoricalChart 
        historicalData={historical_data_for_chart}
        predictedData={predicted_data_for_chart}
      />
      
      <footer>
        <p style={{textAlign: 'center', fontSize: '0.8em', color: '#777'}}>
          Bu tahminler istatistiksel modellere dayanmaktadır ve yalnızca bilgilendirme amaçlıdır.
        </p>
      </footer>
    </div>
  );
}

export default App;