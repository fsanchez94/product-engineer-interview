import React from 'react';
import '../layout/Dashboard.css';

const MarketplaceAnalytics = () => {
  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Marketplace Analytics Dashboard</h1>
        <p>Platform-wide trends and insights</p>
      </header>
      
      <div className="charts-grid">
        <div className="chart-container">
          <div style={{ 
            height: '400px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            background: '#f8f9fa',
            border: '2px dashed #dee2e6',
            borderRadius: '8px'
          }}>
            <div style={{ textAlign: 'center', color: '#6c757d' }}>
              <h3>Platform Revenue Trends</h3>
              <p>Coming soon - Total platform revenue over time</p>
            </div>
          </div>
        </div>
        
        <div className="chart-container">
          <div style={{ 
            height: '400px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            background: '#f8f9fa',
            border: '2px dashed #dee2e6',
            borderRadius: '8px'
          }}>
            <div style={{ textAlign: 'center', color: '#6c757d' }}>
              <h3>Top Performing Categories</h3>
              <p>Coming soon - Platform-wide category performance</p>
            </div>
          </div>
        </div>
        
        <div className="chart-container">
          <div style={{ 
            height: '400px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            background: '#f8f9fa',
            border: '2px dashed #dee2e6',
            borderRadius: '8px'
          }}>
            <div style={{ textAlign: 'center', color: '#6c757d' }}>
              <h3>Seller Growth Metrics</h3>
              <p>Coming soon - New sellers and growth trends</p>
            </div>
          </div>
        </div>
        
        <div className="chart-container">
          <div style={{ 
            height: '400px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            background: '#f8f9fa',
            border: '2px dashed #dee2e6',
            borderRadius: '8px'
          }}>
            <div style={{ textAlign: 'center', color: '#6c757d' }}>
              <h3>Order Volume Analysis</h3>
              <p>Coming soon - Platform-wide order patterns</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketplaceAnalytics;