import React, { createContext, useContext, useState, useEffect } from 'react';
import { getCurrentUser } from '@/api/auth';

/**
 * Interface representing User Information
 */
export interface User {
  user_id: number;
  email: string;
  username: string;
}

/**
 * Interface for the Auth Context state
 */
export interface AuthContextType {
  user: User | null;
  loading: boolean;
  loginState: (token: string, userData: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  loginState: () => {},
  logout: () => {},
});

/**
 * Custom hook to use the AuthContext
 * @returns AuthContextType
 */
export const useAuth = () => useContext(AuthContext);

/**
 * AuthProvider component to wrap app and maintain user state
 * @param props Props containing the children to render
 * @returns AuthProvider Component
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const res = await getCurrentUser();
          if (res.status === 'success') {
            setUser(res.data);
          } else {
            localStorage.removeItem('auth_token');
          }
        } catch (error) {
          localStorage.removeItem('auth_token');
        }
      }
      setLoading(false);
    };
    fetchUser();
  }, []);

  /**
   * Updates state upon successful login
   * @param token Authentication token string
   * @param userData User details object
   */
  const loginState = (token: string, userData: User) => {
    localStorage.setItem('auth_token', token);
    setUser(userData);
  };

  /**
   * Logs out the user and clears context
   */
  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, loginState, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
