// frontend/src/types/api.ts

export interface PredictionData {
    last_actual_cpi: number;
    last_actual_date: string; // Format "DD/MM/YYYY"
    predictions_pct_change: { [key: string]: number }; // e.g., {"3": 1.23, "6": 2.34, "12": 4.56}
    predictions_absolute: { [key: string]: number };
    best_model_name: string;
    best_model_mae_validation: number;
    historical_data_for_chart: {
      labels: string[]; // Format "YYYY-MM"
      values: number[];
    };
    predicted_data_for_chart: {
      labels: string[]; // Format "YYYY-MM"
      values: (number | null)[]; // Predictions might have gaps or be incomplete
    };
  }
  
  export interface ApiErrorResponse {
    error: string;
  }