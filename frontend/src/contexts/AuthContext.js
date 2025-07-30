import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  // Set axios defaults
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Check if user is logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      console.log('🔍 AuthContext: Checking authentication, token:', token ? 'present' : 'absent');
      if (token) {
        try {
          console.log('🔍 AuthContext: Making request to /api/auth/me');
          const response = await axios.get(`${backendUrl}/api/auth/me`);
          console.log('✅ AuthContext: User data received:', response.data);
          setUser(response.data);
        } catch (error) {
          console.error('❌ AuthContext: Token validation failed:', error);
          // Token is invalid - try to refresh first
          console.log('🔄 AuthContext: Attempting token refresh...');
          const refreshResult = await refreshToken();
          if (!refreshResult.success) {
            console.log('❌ AuthContext: Token refresh failed, clearing auth');
            localStorage.removeItem('token');
            setToken(null);
            setUser(null);
          }
        }
      } else {
        console.log('🔍 AuthContext: No token present');
      }
      console.log('✅ AuthContext: Authentication check complete, setting loading to false');
      setLoading(false);
    };

    checkAuth();
  }, [token, backendUrl]);

  const login = async (username, password) => {
    try {
      console.log('🔐 AuthContext: Starting login process for username:', username);
      const response = await axios.post(`${backendUrl}/api/auth/login`, {
        username,
        password
      });
      
      console.log('✅ AuthContext: Login response received:', response.data);
      const { access_token } = response.data;
      
      // Store token
      console.log('💾 AuthContext: Storing token in localStorage');
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Get user info
      console.log('👤 AuthContext: Fetching user info');
      const userResponse = await axios.get(`${backendUrl}/api/auth/me`, {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      
      console.log('✅ AuthContext: User info received:', userResponse.data);
      setUser(userResponse.data);
      
      console.log('🎉 AuthContext: Login successful');
      return { success: true };
    } catch (error) {
      console.error('❌ AuthContext: Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const register = async (username, email, password, fullName) => {
    try {
      const response = await axios.post(`${backendUrl}/api/auth/register`, {
        username,
        email,
        password,
        full_name: fullName
      });
      
      const { access_token } = response.data;
      
      // Store token
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Get user info
      const userResponse = await axios.get(`${backendUrl}/api/auth/me`, {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      
      setUser(userResponse.data);
      
      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await axios.post(`${backendUrl}/api/auth/logout`);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
    }
  };

  const refreshToken = async () => {
    try {
      const response = await axios.post(`${backendUrl}/api/auth/refresh`);
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      return { success: true };
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
      return { success: false };
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    refreshToken,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};