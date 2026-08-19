import { useEffect, useState } from 'react';
import { dashboardApi } from '../api';
import type { DashboardData } from '../types/api';
import { PageSpinner } from '../components/ui/Spinner';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { formatCurrency, formatDate, getStockStatus } from '../utils/helpers';
import { Package, Truck, ShoppingCart, AlertTriangle, TrendingUp, DollarSign, Box, ClipboardList } from 'lucide-react';

const kpiCards = [
  { key: 'total_productos', label: 'Total Productos', icon: Package, color: 'blue' },
  { key: 'stock_bajo', label: 'Stock Bajo', icon: AlertTriangle, color: 'amber' },
  { key: 'sin_stock', label: 'Sin Stock', icon: Box, color: 'red' },
  { key: 'total_proveedores', label: 'Proveedores', icon: Truck, color: 'emerald' },
  { key: 'total_pedidos', label: 'Pedidos', icon: ClipboardList, color: 'indigo' },
  { key: 'pedidos_pendientes', label: 'Pendientes', icon: ShoppingCart, color: 'amber' },
  { key: 'total_ventas', label: 'Ventas', icon: TrendingUp, color: 'green' },
  { key: 'valor_total', label: 'Valor Inventario', icon: DollarSign, color: 'amber', isCurrency: true },
  { key: 'ingresos_totales', label: 'Ingresos', icon: TrendingUp, color: 'emerald', isCurrency: true },
];

const colorClasses: Record<string, { bg: string; text: string; bar: string }> = {
  amber: { bg: 'bg-amber-50 dark:bg-amber-500/10', text: 'text-amber-600 dark:text-amber-400', bar: 'bg-amber-500' },
  red: { bg: 'bg-red-50 dark:bg-red-500/10', text: 'text-red-600 dark:text-red-400', bar: 'bg-red-500' },
  blue: { bg: 'bg-blue-50 dark:bg-blue-500/10', text: 'text-blue-600 dark:text-blue-400', bar: 'bg-blue-500' },
  emerald: { bg: 'bg-emerald-50 dark:bg-emerald-500/10', text: 'text-emerald-600 dark:text-emerald-400', bar: 'bg-emerald-500' },
  indigo: { bg: 'bg-indigo-50 dark:bg-indigo-500/10', text: 'text-indigo-600 dark:text-indigo-400', bar: 'bg-indigo-500' },
  green: { bg: 'bg-green-50 dark:bg-green-500/10', text: 'text-green-600 dark:text-green-400', bar: 'bg-green-500' },
};

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await dashboardApi.get();
      setData(response.data.data || response.data);
    } catch {
      setError('Error al cargar el dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <PageSpinner />;

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <p className="text-red-500 font-mono text-sm mb-4">{error}</p>
        <button onClick={fetchData} className="px-4 py-2 bg-amber-500 text-gray-900 rounded-lg text-sm font-semibold hover:bg-amber-400 transition-colors">
          Reintentar
        </button>
      </div>
    );
  }

  if (!data) return null;

  const { kpi, productos_recientes, pedidos_recientes } = data;

  const kpiValue = (key: string) => {
    const value = kpi[key as keyof typeof kpi];
    if (key === 'valor_total' || key === 'ingresos_totales') return formatCurrency(value as number);
    return value?.toLocaleString() || '0';
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Panel de Control</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 font-mono">Resumen ejecutivo del inventario</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {kpiCards.map((kpiItem) => {
          const colors = colorClasses[kpiItem.color];
          const Icon = kpiItem.icon;
          return (
            <Card key={kpiItem.key} className="relative overflow-hidden">
              <div className={`absolute top-0 left-0 right-0 h-0.5 ${colors.bar}`} />
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-mono text-gray-500 dark:text-gray-400 mb-1">{kpiItem.label}</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white font-mono">
                    {kpiValue(kpiItem.key)}
                  </p>
                </div>
                <div className={`w-10 h-10 rounded-lg ${colors.bg} ${colors.text} flex items-center justify-center`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Productos Recientes" subtitle="Últimos 5 registrados">
          {productos_recientes.length === 0 ? (
            <p className="text-sm text-gray-400 font-mono text-center py-8">Sin productos recientes</p>
          ) : (
            <div className="space-y-3">
              {productos_recientes.map((p) => {
                const stock = getStockStatus(p.cantidad, p.stock_min);
                return (
                  <div key={p.id} className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{p.nombre}</p>
                      <p className="text-xs font-mono text-gray-500 dark:text-gray-400">{p.categoria} · {formatDate(p.fecha_creacion)}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-mono text-gray-700 dark:text-gray-300">{p.cantidad} uds</span>
                      <Badge variant={stock.color}>{stock.label}</Badge>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </Card>

        <Card title="Pedidos Recientes" subtitle="Últimos 5 registrados">
          {pedidos_recientes.length === 0 ? (
            <p className="text-sm text-gray-400 font-mono text-center py-8">Sin pedidos recientes</p>
          ) : (
            <div className="space-y-3">
              {pedidos_recientes.map((p) => (
                <div key={p.id} className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">{p.numero_orden}</p>
                    <p className="text-xs font-mono text-gray-500 dark:text-gray-400">{p.proveedor?.razon_social || 'N/A'} · {formatDate(p.fecha_pedido)}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-mono text-amber-600 dark:text-amber-400">{formatCurrency(p.total)}</span>
                    <Badge variant={p.estado === 'recibido' ? 'success' : p.estado === 'pendiente' ? 'warning' : 'info'}>{p.estado}</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
