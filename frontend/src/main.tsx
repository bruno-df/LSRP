import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// O Vite fornece a div #root em index.html. createRoot entrega esse elemento ao
// React; StrictMode ativa verificações adicionais durante o desenvolvimento.
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
