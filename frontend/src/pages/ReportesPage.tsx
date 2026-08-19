import { useEffect, useState } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement } from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { reportesApi } from '../api';
import type { ReporteInventario, ReporteMasVendidos, ReporteVentas } from '../types/api';
import { useTheme } from '../contexts';
import { Button } from '../components/ui/Button';
import { Card, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Select } from '../components/ui/Input';
import { PageSpinner } from '../components/ui/Spinner';
import { EmptyState } from '../components/ui/EmptyState';
import { formatCurrency, formatDate, downloadBlob } from '../utils/helpers';
import { FileSpreadsheet, FileText, TrendingUp, Package, DollarSign } from 'lucide-react';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement);

type ReportTab = 'inventario' | 'mas-vendidos' | 'ventas';

const TOP_OPTIONS = [
  { value: '5', label: 'Top 5' },
  { value: '10', label: 'Top 10' },
  { value: '20', label: 'Top 20' },
];

const TABS: { key: ReportTab; label: string; icon: React.ReactNode }[] = [
  { key: 'inventario', label: 'Inventario', icon: <Package className="w-4 h-4" /> },
  { key: 'mas-vendidos', label: 'Más Vendidos', icon: <TrendingUp className="w-4 h-4" /> },
  { key: 'ventas', label: 'Ventas', icon: <DollarSign className="w-4 h-4" /> },
];

function chartColors(theme: string) {
  const isDark = theme === 'dark';
  return {
    gridColor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
    textColor: isDark ? '#9ca3af' : '#6b7280',
    barBg: isDark ? 'rgba(251,191,36,0.7)' : 'rgba(245,158,11,0.7)',
    barBorder: isDark ? 'rgb(251,191,36)' : 'rgb(217,119,6)',
  };
}

export function ReportesPage() {
  const { theme } = useTheme();
  const colors = chartColors(theme);

  const [activeTab, setActiveTab] = useState<ReportTab>('inventario');

  const [inventario, setInventario] = useState<ReporteInventario | null>(null);
  const [masVendidos, setMasVendidos] = useState<ReporteMasVendidos | null>(null);
  const [ventas, setVentas] = useState<ReporteVentas | null>(null);

  const [loadingInv, setLoadingInv] = useState(false);
  const [loadingTop, setLoadingTop] = useState(false);
  const [loadingVentas, setLoadingVentas] = useState(false);

  const [errorInv, setErrorInv] = useState('');
  const [errorTop, setErrorTop] = useState('');
  const [errorVentas, setErrorVentas] = useState('');

  const [topN, setTopN] = useState(10);
  const [exporting, setExporting] = useState<string | null>(null);

  const fetchInventario = async () => {
    setLoadingInv(true);
    setErrorInv('');
    try {
      const res = await reportesApi.inventario();
      setInventario(res.data.data || res.data);
    } catch {
      setErrorInv('Error al cargar el reporte de inventario');
    } finally {
      setLoadingInv(false);
    }
  };

  const fetchMasVendidos = async () => {
    setLoadingTop(true);
    setErrorTop('');
    try {
      const res = await reportesApi.masVendidos({ top: topN });
      setMasVendidos(res.data.data || res.data);
    } catch {
      setErrorTop('Error al cargar el reporte de más vendidos');
    } finally {
      setLoadingTop(false);
    }
  };

  const fetchVentas = async () => {
    setLoadingVentas(true);
    setErrorVentas('');
    try {
      const res = await reportesApi.ventas();
      setVentas(res.data.data || res.data);
    } catch {
      setErrorVentas('Error al cargar el reporte de ventas');
    } finally {
      setLoadingVentas(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'inventario' && !inventario && !loadingInv) fetchInventario();
    if (activeTab === 'mas-vendidos' && !masVendidos && !loadingTop) fetchMasVendidos();
    if (activeTab === 'ventas' && !ventas && !loadingVentas) fetchVentas();
  }, [activeTab]);

  useEffect(() => {
    if (masVendidos) fetchMasVendidos();
  }, [topN]);

  const handleExport = async (tipo: 'inventario' | 'ventas', format: 'excel' | 'pdf') => {
    const key = `${tipo}-${format}`;
    setExporting(key);
    try {
      const fn = format === 'excel' ? reportesApi.exportExcel : reportesApi.exportPdf;
      const res = await fn(tipo);
      const ext = format === 'excel' ? 'xlsx' : 'pdf';
      downloadBlob(res.data, `reporte-${tipo}.${ext}`);
    } catch {
      // silent
    } finally {
      setExporting(null);
    }
  };

  const inventarioChartData = inventario ? {
    labels: inventario.categorias.map((c) => c.nombre),
    datasets: [
      {
        label: 'Cantidad',
        data: inventario.categorias.map((c) => c.cantidad),
        backgroundColor: colors.barBg,
        borderColor: colors.barBorder,
        borderWidth: 2,
        borderRadius: 4,
      },
    ],
  } : null;

  const masVendidosChartData = masVendidos ? {
    labels: masVendidos.ranking.map((p) => p.nombre.length > 20 ? p.nombre.substring(0, 20) + '...' : p.nombre),
    datasets: [
      {
        label: 'Total Vendido',
        data: masVendidos.ranking.map((p) => p.total_vendido),
        backgroundColor: colors.barBg,
        borderColor: colors.barBorder,
        borderWidth: 2,
        borderRadius: 4,
      },
    ],
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: theme === 'dark' ? '#1f2937' : '#ffffff',
        titleColor: theme === 'dark' ? '#f9fafb' : '#111827',
        bodyColor: theme === 'dark' ? '#d1d5db' : '#4b5563',
        borderColor: theme === 'dark' ? '#374151' : '#e5e7eb',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        ticks: { color: colors.textColor, maxRotation: 45 },
        grid: { color: colors.gridColor },
      },
      y: {
        beginAtZero: true,
        ticks: { color: colors.textColor },
        grid: { color: colors.gridColor },
      },
    },
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Reportes</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Visualiza y exporta reportes del sistema</p>
      </div>

      <div className="flex gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-xl w-fit">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab.key
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'inventario' && (
        <div className="space-y-6">
          <Card>
            <CardHeader
              title="Resumen de Inventario"
              subtitle="Estado actual del inventario"
              action={
                <div className="flex gap-2">
                  <Button variant="secondary" size="sm" loading={exporting === 'inventario-excel'} onClick={() => handleExport('inventario', 'excel')}>
                    <FileSpreadsheet className="w-4 h-4" /> Excel
                  </Button>
                  <Button variant="secondary" size="sm" loading={exporting === 'inventario-pdf'} onClick={() => handleExport('inventario', 'pdf')}>
                    <FileText className="w-4 h-4" /> PDF
                  </Button>
                </div>
              }
            />
            {loadingInv ? (
              <PageSpinner />
            ) : errorInv ? (
              <div className="text-center py-8">
                <p className="text-red-500 text-sm mb-3">{errorInv}</p>
                <Button variant="secondary" size="sm" onClick={fetchInventario}>Reintentar</Button>
              </div>
            ) : inventario ? (
              <div className="space-y-6">
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                  <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700">
                    <p className="text-xs font-mono uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-1">Total Productos</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{inventario.resumen.total_productos}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700">
                    <p className="text-xs font-mono uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-1">Valor Total</p>
                    <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{formatCurrency(inventario.resumen.valor_total)}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700">
                    <p className="text-xs font-mono uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-1">Stock Normal</p>
                    <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{inventario.resumen.stock_normal}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700">
                    <p className="text-xs font-mono uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-1">Stock Bajo</p>
                    <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">{inventario.resumen.stock_bajo}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700">
                    <p className="text-xs font-mono uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-1">Sin Stock</p>
                    <p className="text-2xl font-bold text-red-600 dark:text-red-400">{inventario.resumen.sin_stock}</p>
                  </div>
                </div>

                {inventario.categorias.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Productos por Categoría</h4>
                    <div className="h-72">
                      {inventarioChartData && <Bar data={inventarioChartData} options={chartOptions} />}
                    </div>
                  </div>
                )}

                {inventario.productos_bajo_stock.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Productos con Stock Bajo</h4>
                    <div className="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded-lg">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
                            <th className="text-left px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Producto</th>
                            <th className="text-left px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Categoría</th>
                            <th className="text-right px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Stock</th>
                            <th className="text-right px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Stock Mín</th>
                            <th className="text-center px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Estado</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                          {inventario.productos_bajo_stock.map((p) => (
                            <tr key={p.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                              <td className="px-4 py-2 font-medium text-gray-900 dark:text-white">{p.nombre}</td>
                              <td className="px-4 py-2 text-gray-500 dark:text-gray-400">{p.categoria}</td>
                              <td className="px-4 py-2 text-right text-amber-600 dark:text-amber-400 font-semibold">{p.cantidad}</td>
                              <td className="px-4 py-2 text-right text-gray-500 dark:text-gray-400">{p.stock_min}</td>
                              <td className="px-4 py-2 text-center"><Badge variant="warning">Stock Bajo</Badge></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {inventario.categorias.length === 0 && inventario.productos_bajo_stock.length === 0 && (
                  <EmptyState title="Sin datos" message="No hay información disponible para este reporte" />
                )}
              </div>
            ) : null}
          </Card>
        </div>
      )}

      {activeTab === 'mas-vendidos' && (
        <div className="space-y-6">
          <Card>
            <CardHeader
              title="Productos Más Vendidos"
              subtitle="Ranking de productos con mayores ventas"
              action={
                <div className="flex items-center gap-3">
                  <Select
                    options={TOP_OPTIONS}
                    value={String(topN)}
                    onChange={(e) => setTopN(Number(e.target.value))}
                    className="w-28"
                  />
                  <Button variant="secondary" size="sm" loading={exporting === 'ventas-excel'} onClick={() => handleExport('ventas', 'excel')}>
                    <FileSpreadsheet className="w-4 h-4" /> Excel
                  </Button>
                  <Button variant="secondary" size="sm" loading={exporting === 'ventas-pdf'} onClick={() => handleExport('ventas', 'pdf')}>
                    <FileText className="w-4 h-4" /> PDF
                  </Button>
                </div>
              }
            />
            {loadingTop ? (
              <PageSpinner />
            ) : errorTop ? (
              <div className="text-center py-8">
                <p className="text-red-500 text-sm mb-3">{errorTop}</p>
                <Button variant="secondary" size="sm" onClick={fetchMasVendidos}>Reintentar</Button>
              </div>
            ) : masVendidos && masVendidos.ranking.length > 0 ? (
              <div className="space-y-6">
                <div className="h-72">
                  {masVendidosChartData && <Bar data={masVendidosChartData} options={chartOptions} />}
                </div>

                <div className="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded-lg">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
                        <th className="text-left px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">#</th>
                        <th className="text-left px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Producto</th>
                        <th className="text-left px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Categoría</th>
                        <th className="text-right px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Total Vendido</th>
                        <th className="text-right px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Ingresos</th>
                        <th className="text-right px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Veces Vendido</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                      {masVendidos.ranking.map((p, idx) => (
                        <tr key={p.producto_id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                          <td className="px-4 py-2 text-gray-400 font-mono text-xs">{idx + 1}</td>
                          <td className="px-4 py-2 font-medium text-gray-900 dark:text-white">{p.nombre}</td>
                          <td className="px-4 py-2 text-gray-500 dark:text-gray-400">{p.categoria}</td>
                          <td className="px-4 py-2 text-right font-semibold text-gray-900 dark:text-white">{p.total_vendido}</td>
                          <td className="px-4 py-2 text-right font-semibold text-emerald-600 dark:text-emerald-400">{formatCurrency(p.total_ingresos)}</td>
                          <td className="px-4 py-2 text-right text-gray-500 dark:text-gray-400">{p.veces_vendido}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <EmptyState title="Sin datos" message="No hay productos vendidos para mostrar" icon={<TrendingUp className="w-8 h-8" />} />
            )}
          </Card>
        </div>
      )}

      {activeTab === 'ventas' && (
        <div className="space-y-6">
          <Card>
            <CardHeader
              title="Reporte de Ventas"
              subtitle="Resumen de actividad de ventas"
              action={
                <div className="flex gap-2">
                  <Button variant="secondary" size="sm" loading={exporting === 'ventas-excel'} onClick={() => handleExport('ventas', 'excel')}>
                    <FileSpreadsheet className="w-4 h-4" /> Excel
                  </Button>
                  <Button variant="secondary" size="sm" loading={exporting === 'ventas-pdf'} onClick={() => handleExport('ventas', 'pdf')}>
                    <FileText className="w-4 h-4" /> PDF
                  </Button>
                </div>
              }
            />
            {loadingVentas ? (
              <PageSpinner />
            ) : errorVentas ? (
              <div className="text-center py-8">
                <p className="text-red-500 text-sm mb-3">{errorVentas}</p>
                <Button variant="secondary" size="sm" onClick={fetchVentas}>Reintentar</Button>
              </div>
            ) : ventas ? (
              <div className="space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700">
                    <p className="text-xs font-mono uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-1">Total Ventas</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{ventas.resumen.total_ventas}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700">
                    <p className="text-xs font-mono uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-1">Ingresos Totales</p>
                    <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{formatCurrency(ventas.resumen.total_ingresos)}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700">
                    <p className="text-xs font-mono uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-1">Promedio por Venta</p>
                    <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">{formatCurrency(ventas.resumen.promedio_venta)}</p>
                  </div>
                </div>

                {ventas.ventas_recientes.length > 0 ? (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Ventas Recientes</h4>
                    <div className="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded-lg">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
                            <th className="text-left px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Factura</th>
                            <th className="text-left px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Cliente</th>
                            <th className="text-left px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Fecha</th>
                            <th className="text-right px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Total</th>
                            <th className="text-center px-4 py-2 font-mono text-xs uppercase text-gray-500 dark:text-gray-400">Estado</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                          {ventas.ventas_recientes.map((v) => (
                            <tr key={v.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                              <td className="px-4 py-2 font-medium text-gray-900 dark:text-white">{v.numero_factura}</td>
                              <td className="px-4 py-2 text-gray-500 dark:text-gray-400">{v.cliente || '—'}</td>
                              <td className="px-4 py-2 text-gray-500 dark:text-gray-400">{formatDate(v.fecha_venta)}</td>
                              <td className="px-4 py-2 text-right font-semibold text-gray-900 dark:text-white">{formatCurrency(v.total)}</td>
                              <td className="px-4 py-2 text-center">
                                <Badge variant={v.estado === 'completada' ? 'success' : v.estado === 'cancelada' ? 'danger' : 'warning'}>
                                  {v.estado}
                                </Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : (
                  <EmptyState title="Sin ventas recientes" message="Aún no hay ventas registradas" icon={<DollarSign className="w-8 h-8" />} />
                )}
              </div>
            ) : null}
          </Card>
        </div>
      )}
    </div>
  );
}
