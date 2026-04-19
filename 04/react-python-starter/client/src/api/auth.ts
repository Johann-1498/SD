import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/register'; 

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000', // VPS or Local dev server
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Perform login request
 * @param payload - Username or email and password
 * @returns Promise with auth response data
 */
export const login = async (payload: any) => {
  const response = await apiClient.post('/login', payload);
  return response.data;
};

/**
 * Perform register request
 * @param payload - Username, email and password
 * @returns Promise with auth response data
 */
export const register = async (payload: any) => {
  const response = await apiClient.post('/register', payload);
  return response.data;
};

/**
 * Perform forgot password request
 * @param payload - User Email
 * @returns Promise with message
 */
export const forgotPassword = async (payload: any) => {
  const response = await apiClient.post('/forgot-password', payload);
  return response.data;
};

/**
 * Perform reset password request
 * @param payload - Reset token and new password
 * @returns Promise with message
 */
export const resetPassword = async (payload: any) => {
  const response = await apiClient.post('/reset-password', payload);
  return response.data;
};

/**
 * Get current user information
 * @returns Promise with user data
 */
export const getCurrentUser = async () => {
  const response = await apiClient.get('/me');
  return response.data;
};
