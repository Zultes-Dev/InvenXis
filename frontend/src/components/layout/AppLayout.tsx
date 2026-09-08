import { Outlet } from 'react-router-dom';
import { useState } from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { useLocation } from 'react-router-dom';

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  '/': { title: 'Dashboard', subtitle: 'Inicio' },
  '/productos': { title: 'Productos', subtitle: 'Inventario' },
  '/proveedores': { title: 'Proveedores', subtitle: 'Directorio' },
  '/ventas': { title: 'Ventas', subtitle: 'Punto de Venta' },
  '/facturacion': { title: 'Facturación', subtitle: 'Electrónica DIAN' },
  '/reportes': { title: 'Reportes', subtitle: 'Analítica' },
};

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const pageInfo = pageTitles[location.pathname] || { title: 'InvenXis', subtitle: 'Gestión' };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className="lg:pl-64">
        <Topbar
          title={pageInfo.title}
          subtitle={pageInfo.subtitle}
          onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
        />
        <main className="p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
