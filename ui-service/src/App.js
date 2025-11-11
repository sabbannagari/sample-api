import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import Login from './components/Login';
import Products from './components/Products';
import Orders from './components/Orders';
import { authAPI, getToken } from './services/api';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = getToken();
    if (token) {
      try {
        const userData = await authAPI.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        setIsAuthenticated(false);
        setUser(null);
      }
    }
    setLoading(false);
  };

  const handleLogout = async () => {
    await authAPI.logout();
    setIsAuthenticated(false);
    setUser(null);
  };

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <Router>
      <div className="app">
        {isAuthenticated && (
          <nav className="navbar">
            <div className="nav-container">
              <div className="nav-logo">
                <h2>Sample API UI</h2>
              </div>
              <div className="nav-links">
                <Link to="/products" className="nav-link">Products</Link>
                <Link to="/orders" className="nav-link">Orders</Link>
              </div>
              <div className="nav-user">
                <span className="user-info">
                  Welcome, <strong>{user?.username}</strong> ({user?.role})
                </span>
                <button onClick={handleLogout} className="logout-btn">
                  Logout
                </button>
              </div>
            </div>
          </nav>
        )}

        <div className="main-content">
          <Routes>
            <Route
              path="/login"
              element={
                isAuthenticated ? (
                  <Navigate to="/products" />
                ) : (
                  <Login setIsAuthenticated={setIsAuthenticated} setUser={setUser} />
                )
              }
            />
            <Route
              path="/products"
              element={
                isAuthenticated ? (
                  <Products user={user} />
                ) : (
                  <Navigate to="/login" />
                )
              }
            />
            <Route
              path="/orders"
              element={
                isAuthenticated ? (
                  <Orders user={user} />
                ) : (
                  <Navigate to="/login" />
                )
              }
            />
            <Route
              path="/"
              element={
                <Navigate to={isAuthenticated ? "/products" : "/login"} />
              }
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
