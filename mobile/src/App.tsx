import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';
import { theme } from './theme';
import { AppProvider } from './context/AppContext';
import { NetworkStatus } from './components/NetworkStatus';
import { BottomNavigation } from './components/BottomNavigation';
import { UpdatePrompt } from './components/UpdatePrompt';
import Dashboard from './pages/Dashboard';
import Weather from './pages/Weather';
import Farm from './pages/Farm';
import Loans from './pages/Loans';
import CreditScore from './pages/CreditScore';
import Login from './pages/Login';
import Register from './pages/Register';
import Offline from './pages/Offline';
import Profile from './pages/Profile';
import MarketPrices from './pages/MarketPrices';
import './App.css';

function App() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [waitingWorker, setWaitingWorker] = useState<ServiceWorker | null>(null);
  const [showUpdatePrompt, setShowUpdatePrompt] = useState(false);

  // Check authentication status
  useEffect(() => {
    const token = localStorage.getItem('agrifinance_token');
    if (token) {
      // In a real app, we would validate the token here
      setIsLoggedIn(true);
    }
  }, []);

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Service worker update handling
  useEffect(() => {
    // Listen for new service worker updates
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then(registration => {
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                setWaitingWorker(newWorker);
                setShowUpdatePrompt(true);
              }
            });
          }
        });
      });
    }
  }, []);

  const handleUpdate = () => {
    if (waitingWorker) {
      waitingWorker.postMessage({ type: 'SKIP_WAITING' });
      setShowUpdatePrompt(false);
      window.location.reload();
    }
  };

  return (
    <I18nextProvider i18n={i18n}>
      <ThemeProvider theme={theme}>
        <AppProvider>
          <Router>
            <div className="app">
              <NetworkStatus isOnline={isOnline} />
              {showUpdatePrompt && <UpdatePrompt onUpdate={handleUpdate} />}
              
              <main className="main-content">
                {!isOnline && <Navigate to="/offline" />}
                
                <Routes>
                  <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
                  <Route path="/register" element={<Register setIsLoggedIn={setIsLoggedIn} />} />
                  <Route path="/offline" element={<Offline />} />
                  
                  {/* Protected routes */}
                  <Route 
                    path="/" 
                    element={isLoggedIn ? <Dashboard /> : <Navigate to="/login" />} 
                  />
                  <Route 
                    path="/weather" 
                    element={isLoggedIn ? <Weather /> : <Navigate to="/login" />} 
                  />
                  <Route 
                    path="/farm" 
                    element={isLoggedIn ? <Farm /> : <Navigate to="/login" />} 
                  />
                  <Route 
                    path="/loans" 
                    element={isLoggedIn ? <Loans /> : <Navigate to="/login" />} 
                  />
                  <Route 
                    path="/credit" 
                    element={isLoggedIn ? <CreditScore /> : <Navigate to="/login" />} 
                  />
                  <Route 
                    path="/profile" 
                    element={isLoggedIn ? <Profile /> : <Navigate to="/login" />} 
                  />
                  <Route 
                    path="/market" 
                    element={isLoggedIn ? <MarketPrices /> : <Navigate to="/login" />} 
                  />
                </Routes>
              </main>
              
              {isLoggedIn && <BottomNavigation />}
            </div>
          </Router>
        </AppProvider>
      </ThemeProvider>
    </I18nextProvider>
  );
}

export default App;
