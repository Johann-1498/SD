import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';

import Login from '@/pages/Login';
import Register from '@/pages/Register';
import ForgotPassword from '@/pages/ForgotPassword';
import ResetPassword from '@/pages/ResetPassword';
import Landing from '@/pages/Landing';

/**
 * Protected Route Wrapper Component
 * @returns React Element conditionally rendering Outlet or redirecting
 */
const PrivateRoute = () => {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex h-screen items-center justify-center">Cargando...</div>;
  return user ? <Outlet /> : <Navigate to="/login" replace />;
};

/**
 * Public Route Wrapper Component
 * @returns React Element conditionally rendering Outlet or redirecting to home
 */
const PublicRoute = () => {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex h-screen items-center justify-center">Cargando...</div>;
  return !user ? <Outlet /> : <Navigate to="/" replace />;
};

/**
 * App Main Component
 * @returns React element initializing the application routes and context
 */
export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
          </Route>
          
          <Route element={<PrivateRoute />}>
            <Route path="/" element={<Landing />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
