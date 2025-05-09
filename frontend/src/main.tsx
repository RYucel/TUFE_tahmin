// frontend/src/main.tsx (or index.tsx)
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx' // Ensure App.tsx is imported
import './index.css' // Your global CSS

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)