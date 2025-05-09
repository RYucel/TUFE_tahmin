// frontend/src/components/PredictionDisplay.tsx
import React from 'react';
import './PredictionDisplay.css'; // Your CSS file for this component

interface PredictionDisplayProps {
  predictionsPct: { [key: string]: number };
  predictionsAbs: { [key: string]: number };
}

const PredictionDisplay: React.FC<PredictionDisplayProps> = ({ predictionsPct, predictionsAbs }) => {
  if (!predictionsPct || Object.keys(predictionsPct).length === 0) {
    return <p>Tahmin verisi bulunamadı.</p>;
  }

  // Sort horizons numerically if they are string keys like "3", "6", "12"
  const horizons = Object.keys(predictionsPct).sort((a, b) => parseInt(a, 10) - parseInt(b, 10));

  return (
    <div className="prediction-container">
      <h2>Gelecek Dönem Tahminleri (Yüzdesel Değişim)</h2>
      <div className="prediction-grid">
        {horizons.map(horizon => (
          <div key={horizon} className="prediction-card">
            <h3>{horizon} Ay Sonrası</h3>
            <p className={`percentage ${predictionsPct[horizon] >= 0 ? 'positive' : 'negative'}`}>
              {predictionsPct[horizon] >= 0 ? '+' : ''}
              {predictionsPct[horizon].toFixed(2)}%
            </p>
            <p className="absolute-value">
              (Mutlak Değer: {predictionsAbs[horizon].toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })})
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PredictionDisplay;