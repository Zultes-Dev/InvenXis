import { Suspense, lazy } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { queryClient } from './lib/queryClient';
import { AuthProvider, ThemeProvider, useAuth } from './contexts';
import { AppLayout } from './components/layout/AppLayout';
import { LoginPage } from './pages/LoginPage';
import { Toaster } from 'react-hot-toast';
import type { ReactNode } from 'react';

const DashboardPage = lazy(() =>
  import('./pages/DashboardPage').then((m) => ({ default: m.DashboardPage })));
const ProductosPage = lazy(() => import('./pages/ProductosPage'));
const ProveedoresPage = lazy(() => import('./pages/ProveedoresPage'));
const VentasPage = lazy(() =>
  import('./pages/VentasPage').then((m) => ({ default: m.VentasPage })));
const ReportesPage = lazy(() =>
  import('./pages/ReportesPage').then((m) => ({ default: m.ReportesPage })));

function PageFallback() {
  return (
    <div className="min-h-[40vh] flex items-center justify-center">
      <div className="animate-spin h-10 w-10 border-2 border-amber-500 border-t-transparent rounded-full mx-auto" />
    </div>
  );
}

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="text-center">
          <div className="animate-spin h-10 w-10 border-2 border-amber-500 border-t-transparent rounded-full mx-auto" />
          <p className="mt-4 text-sm text-gray-500 dark:text-gray-400 font-mono">Cargando...</p>
        </div>
      </div>
    );
  }
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function PublicRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
        <div className="animate-spin h-10 w-10 border-2 border-amber-500 border-t-transparent rounded-full mx-auto" />
      </div>
    );
  }
  if (isAuthenticated) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Suspense fallback={<PageFallback />}>
      <Routes>
        <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
        <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/productos" element={<ProductosPage />} />
          <Route path="/proveedores" element={<ProveedoresPage />} />
          <Route path="/ventas" element={<VentasPage />} />
          <Route path="/reportes" element={<ReportesPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <AppRoutes />
          <Toaster
            position="bottom-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: 'var(--toast-bg, #fff)',
                color: 'var(--toast-color, #1a1c1e)',
                border: '1px solid var(--toast-border, #e5e4e7)',
                borderRadius: '11px',
                fontSize: '13px',
                fontFamily: 'Syne, sans-serif',
              },
            }}
          />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
    </QueryClientProvider>
  );
}
