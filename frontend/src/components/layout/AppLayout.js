import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import { SellerProvider } from '../../contexts/SellerContext';

const AppLayout = () => {
  return (
    <SellerProvider>
      <div>
        <Navbar />
        <main>
          <Outlet />
        </main>
      </div>
    </SellerProvider>
  );
};

export default AppLayout;