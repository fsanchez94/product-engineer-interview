import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Seller analytics APIs - sellerId is now required
export const getSellerAnalytics = async (sellerId) => {
  if (!sellerId) {
    throw new Error('sellerId is required');
  }
  
  try {
    const response = await api.get(`/api/sellers/${sellerId}/analytics/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching seller analytics:', error);
    throw error;
  }
};

export const getSalesPerformance = async (sellerId) => {
  if (!sellerId) {
    throw new Error('sellerId is required');
  }
  
  try {
    const response = await api.get(`/api/sellers/${sellerId}/sales-performance/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching sales performance:', error);
    throw error;
  }
};

export const getMarketShare = async (sellerId) => {
  if (!sellerId) {
    throw new Error('sellerId is required');
  }
  
  try {
    const response = await api.get(`/api/sellers/${sellerId}/market-share/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching market share:', error);
    throw error;
  }
};

// New API to fetch list of sellers
export const getSellers = async () => {
  try {
    const response = await api.get('/api/sellers/list_sellers/');
    return response.data;
  } catch (error) {
    console.error('Error fetching sellers list:', error);
    throw error;
  }
};

// Platform-wide analytics APIs
export const getPlatformCategoryMarketShare = async () => {
  try {
    const response = await api.get('/api/platform/category-market-share/');
    return response.data;
  } catch (error) {
    console.error('Error fetching platform category market share:', error);
    throw error;
  }
};

export const getPlatformTopProducts = async () => {
  try {
    const response = await api.get('/api/platform/top-products/');
    return response.data;
  } catch (error) {
    console.error('Error fetching platform top products:', error);
    throw error;
  }
};

export const getPlatformSearchAnalytics = async () => {
  try {
    const response = await api.get('/api/platform/search-analytics/');
    return response.data;
  } catch (error) {
    console.error('Error fetching platform search analytics:', error);
    throw error;
  }
};

export const getPlatformRevenueByState = async () => {
  try {
    const response = await api.get('/api/platform/revenue-by-state/');
    return response.data;
  } catch (error) {
    console.error('Error fetching platform revenue by state:', error);
    throw error;
  }
};