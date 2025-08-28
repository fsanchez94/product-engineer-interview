import React from 'react';
import RevenueChart from '../charts/RevenueChart';
import CategoryChart from '../charts/CategoryChart';
import MarketShareChart from '../charts/MarketShareChart';
import TopProductsChart from '../charts/TopProductsChart';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Seller Analytics Dashboard</h1>
        <p>Performance insights and market intelligence</p>
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

export default Dashboard;