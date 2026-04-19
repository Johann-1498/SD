import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

/**
 * Landing Page Component (Protected)
 * @returns React element representing the protected dashboard/landing area
 */
export default function Landing() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen w-full bg-gray-50 dark:bg-gray-900 p-8">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-primary">UNSA Portal</h1>
        <Button variant="outline" onClick={handleLogout}>Cerrar Sesión</Button>
      </header>
      
      <main className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Bienvenido</CardTitle>
            <CardDescription>Resumen de tu cuenta</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm"><strong>Usuario:</strong> {user?.username}</p>
            <p className="text-sm"><strong>Correo:</strong> {user?.email}</p>
            <p className="text-sm text-muted-foreground mt-4">
              Te has autenticado correctamente en nuestra plataforma segura.
            </p>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
