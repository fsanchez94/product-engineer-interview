import React, { useState, useEffect } from 'react';
import CategoryMarketShareChart from '../charts/CategoryMarketShareChart';
import PlatformTopProductsChart from '../charts/PlatformTopProductsChart';
import SearchAnalyticsChart from '../charts/SearchAnalyticsChart';
import RevenueByStateChart from '../charts/RevenueByStateChart';
import { 
  getPlatformCategoryMarketShare, 
  getPlatformTopProducts, 
  getPlatformSearchAnalytics,
  getPlatformRevenueByState
} from '../../services/api';
import '../layout/Dashboard.css';

const MarketplaceAnalytics = () => {
  const [categoryData, setCategoryData] = useState(null);
  const [topProductsData, setTopProductsData] = useState(null);
  const [searchData, setSearchData] = useState(null);
  const [stateData, setStateData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAllData = async () => {
      try {
        setLoading(true);
        
        // Fetch all platform analytics data in parallel
        const [categoryRes, productsRes, searchRes, stateRes] = await Promise.all([
          getPlatformCategoryMarketShare(),
          getPlatformTopProducts(),
          getPlatformSearchAnalytics(),
          getPlatformRevenueByState()
        ]);

        setCategoryData(categoryRes);
        setTopProductsData(productsRes);
        setSearchData(searchRes);
        setStateData(stateRes);
      } catch (error) {
        console.error('Failed to fetch platform analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, []);

  if (loading) {
    return (
      <div className="dashboard">
        <header className="dashboard-header">
          <h1>Marketplace Analytics Dashboard</h1>
          <p>Platform-wide trends and insights</p>
        </header>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '400px',
          fontSize: '18px'
        }}>
          Loading marketplace analytics...
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Marketplace Analytics Dashboard</h1>
        <p>Platform-wide trends and insights</p>
      </header>
      
      <div className="charts-grid">
        <CategoryMarketShareChart data={categoryData} />
        <PlatformTopProductsChart data={topProductsData} />
        <SearchAnalyticsChart data={searchData} />
        <RevenueByStateChart data={stateData} />
      </div>
    </div>
  );
};

export default MarketplaceAnalytics;