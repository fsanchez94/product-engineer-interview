import React from 'react';
import RevenueChart from '../charts/RevenueChart';
import CategoryChart from '../charts/CategoryChart';
import MarketShareChart from '../charts/MarketShareChart';
import TopProductsChart from '../charts/TopProductsChart';
import SellerSelector from '../SellerSelector';
import '../layout/Dashboard.css';

const SellerAnalytics = () => {
  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Seller Analytics Dashboard</h1>
        <p>Performance insights and market intelligence</p>
        <SellerSelector />
      </header>
      
      <div className="charts-grid">
        <div className="chart-container">
          <RevenueChart />
        </div>
        
        <div className="chart-container">
          <CategoryChart />
        </div>
        
        <div className="chart-container">
          <MarketShareChart />
        </div>
        
        <div className="chart-container">
          <TopProductsChart />
        </div>
      </div>
    </div>
  );
};

export default SellerAnalytics;