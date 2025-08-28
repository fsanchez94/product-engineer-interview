import React from 'react';
import { NavLink } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <h2>Analytics Platform</h2>
        </div>
        
        <ul className="navbar-menu">
          <li className="navbar-item">
            <NavLink 
              to="/seller" 
              className={({ isActive }) => isActive ? 'navbar-link active' : 'navbar-link'}
            >
              Seller Analytics
            </NavLink>
          </li>
          <li className="navbar-item">
            <NavLink 
              to="/marketplace" 
              className={({ isActive }) => isActive ? 'navbar-link active' : 'navbar-link'}
            >
              Marketplace Analytics
            </NavLink>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;