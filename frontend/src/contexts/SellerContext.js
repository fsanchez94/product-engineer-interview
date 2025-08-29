import React, { createContext, useState, useContext, useEffect } from 'react';

// Create the context
const SellerContext = createContext();

// Default seller (TechGear Pro)
const DEFAULT_SELLER = {
  seller_id: 'df5141f4-c445-42da-bbd6-8d7ec647bedf',
  name: 'TechGear Pro',
  rating: 0
};

// Custom hook to use the seller context
export const useSeller = () => {
  const context = useContext(SellerContext);
  if (context === undefined) {
    throw new Error('useSeller must be used within a SellerProvider');
  }
  return context;
};

// Provider component
export const SellerProvider = ({ children }) => {
  const [selectedSeller, setSelectedSeller] = useState(DEFAULT_SELLER);
  const [sellers, setSellers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch sellers list on mount
  useEffect(() => {
    const fetchSellers = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/sellers/list_sellers/');
        
        if (!response.ok) {
          throw new Error('Failed to fetch sellers');
        }
        
        const data = await response.json();
        setSellers(data.sellers || []);
        
        // Set default seller if available in the list
        const defaultSeller = data.sellers?.find(s => s.seller_id === DEFAULT_SELLER.seller_id);
        if (defaultSeller) {
          setSelectedSeller(defaultSeller);
        }
        
        setError(null);
      } catch (err) {
        console.error('Error fetching sellers:', err);
        setError(err.message);
        // Fallback to default seller
        setSellers([DEFAULT_SELLER]);
        setSelectedSeller(DEFAULT_SELLER);
      } finally {
        setLoading(false);
      }
    };

    fetchSellers();
  }, []);

  // Function to change selected seller
  const changeSeller = (sellerId) => {
    const seller = sellers.find(s => s.seller_id === sellerId);
    if (seller) {
      setSelectedSeller(seller);
    }
  };

  const value = {
    selectedSeller,
    sellers,
    loading,
    error,
    changeSeller,
    setSelectedSeller
  };

  return (
    <SellerContext.Provider value={value}>
      {children}
    </SellerContext.Provider>
  );
};

export default SellerContext;