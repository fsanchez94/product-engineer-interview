import React from 'react';
import { useSeller } from '../contexts/SellerContext';
import './SellerSelector.css';

const SellerSelector = () => {
  const { selectedSeller, sellers, loading, error, changeSeller } = useSeller();

  const handleSellerChange = (event) => {
    changeSeller(event.target.value);
  };

  if (loading) {
    return (
      <div className="seller-selector">
        <label>Loading sellers...</label>
      </div>
    );
  }

  if (error) {
    return (
      <div className="seller-selector">
        <label>Error loading sellers: {error}</label>
      </div>
    );
  }

  return (
    <div className="seller-selector">
      <label htmlFor="seller-select">Select Seller:</label>
      <select
        id="seller-select"
        value={selectedSeller.seller_id}
        onChange={handleSellerChange}
        className="seller-dropdown"
      >
        {sellers.map((seller) => (
          <option key={seller.seller_id} value={seller.seller_id}>
            {seller.name} {seller.rating ? `(★${seller.rating.toFixed(1)})` : ''}
          </option>
        ))}
      </select>
      <div className="selected-seller-info">
        <span className="seller-name">{selectedSeller.name}</span>
        {selectedSeller.rating > 0 && (
          <span className="seller-rating">★ {selectedSeller.rating.toFixed(1)}</span>
        )}
      </div>
    </div>
  );
};

export default SellerSelector;