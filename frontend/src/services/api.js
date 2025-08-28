import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Hardcoded seller ID for development - TechGear Pro
const DEFAULT_SELLER_ID = 'df5141f4-c445-42da-bbd6-8d7ec647bedf';

export const getSellerAnalytics = async (sellerId = DEFAULT_SELLER_ID) => {
  try {
    const response = await api.get(`/api/sellers/${sellerId}/analytics/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching seller analytics:', error);
    throw error;
  }
};

export const getSalesPerformance = async (sellerId = DEFAULT_SELLER_ID) => {
  try {
    const response = await api.get(`/api/sellers/${sellerId}/sales-performance/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching sales performance:', error);
    throw error;
  }
};

export const getMarketShare = async (sellerId = DEFAULT_SELLER_ID) => {
  try {
    const response = await api.get(`/api/sellers/${sellerId}/market-share/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching market share:', error);
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