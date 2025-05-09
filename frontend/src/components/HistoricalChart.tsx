// frontend/src/components/HistoricalChart.tsx
import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
  ChartOptions,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface HistoricalChartProps {
  historicalData?: { // Make them optional to handle loading state gracefully
    labels: string[];
    values: number[];
  };
  predictedData?: { // Make them optional
    labels: string[];
    values: (number | null)[];
  };
}

const HistoricalChart: React.FC<HistoricalChartProps> = ({ historicalData, predictedData }) => {
  if (!historicalData || !predictedData) {
    return <p>Grafik verisi yükleniyor...</p>;
  }

  const allLabels = [...historicalData.labels, ...predictedData.labels];
  const historicalValuesForChart = [...historicalData.values, ...Array(predictedData.values.length).fill(null)];
  const predictedValuesForChart = [...Array(historicalData.values.length).fill(null), ...predictedData.values];

  const chartData: ChartData<'line'> = { // Explicitly type chartData
    labels: allLabels,
    datasets: [
      {
        label: 'Geçmiş TÜFE Değerleri',
        data: historicalValuesForChart,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
        fill: false,
      },
      {
        label: 'Tahmini TÜFE Değerleri',
        data: predictedValuesForChart,
        borderColor: 'rgb(255, 99, 132)',
        borderDash: [5, 5],
        tension: 0.1,
        fill: false,
      }
    ],
  };

  const options: ChartOptions<'line'> = { // Explicitly type options
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'top' as const, // Use 'as const' for literal types
      },
      title: {
        display: true,
        text: 'TÜFE Geçmiş ve Tahmini Değerler',
      },
      tooltip: {
        callbacks: {
            label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                    label += ': ';
                }
                if (context.parsed.y !== null) {
                    label += context.parsed.y.toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                }
                return label;
            }
        }
      }
    },
    scales: {
      y: {
        ticks: {
          callback: function(value) { // value is number | string
            const numericValue = typeof value === 'string' ? parseFloat(value) : value;
            if (numericValue >= 1000000) return (numericValue / 1000000).toLocaleString('tr-TR') + 'M';
            if (numericValue >= 1000) return (numericValue / 1000).toLocaleString('tr-TR') + 'K';
            return numericValue.toLocaleString('tr-TR');
          }
        }
      }
    }
  };

  return (
    <div style={{ marginTop: '30px', marginBottom: '30px', position: 'relative', minHeight: '300px' }}> {/* Added minHeight for responsiveness */}
      <Line options={options} data={chartData} />
    </div>
  );
};

export default HistoricalChart;