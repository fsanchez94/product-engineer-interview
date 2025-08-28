import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import SellerAnalytics from './components/pages/SellerAnalytics';
import MarketplaceAnalytics from './components/pages/MarketplaceAnalytics';
import './App.css';

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Navigate to="/seller" replace />} />
            <Route path="seller" element={<SellerAnalytics />} />
            <Route path="marketplace" element={<MarketplaceAnalytics />} />
          </Route>
        </Routes>
      </Router>
    </div>
  );
}

export default App;
