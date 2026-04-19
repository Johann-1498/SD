import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { forgotPassword } from '@/api/auth';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

/**
 * ForgotPassword Page Component
 * @returns React element representing the forgot password page
 */
export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');
    try {
      const resp = await forgotPassword({ email });
      setMessage(resp.message || 'Se ha enviado un enlace a tu correo para restablecer tu contraseña. (Revisa la consola del servidor)');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Error occurred. Please try again.');
    }
  };

  return (
    <div className="flex h-screen w-full items-center justify-center bg-gray-50 dark:bg-gray-900">
      <Card className="w-[400px]">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl text-primary font-bold tracking-tight">Recuperar Cuenta</CardTitle>
          <CardDescription>
            Ingresa tu correo para recibir un enlace de recuperación.
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && <div className="text-sm text-destructive font-medium">{error}</div>}
            {message && <div className="text-sm text-green-600 font-medium">{message}</div>}
            <div className="space-y-2">
              <Label htmlFor="email">Correo Electrónico</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="usuario@unsa.edu.pe" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <Button className="w-full" type="submit">Enviar Enlace</Button>
            <div className="text-center text-sm text-muted-foreground w-full">
              <Link to="/login" className="text-primary font-medium hover:underline">
                Volver al inicio de sesión
              </Link>
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
