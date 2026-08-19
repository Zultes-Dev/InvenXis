import { useEffect, useState, useCallback } from 'react';
import { ventasApi, productosApi } from '../api';
import type { VentaListItem, ProductoListItem } from '../types/api';
import { Button } from '../components/ui/Button';
import { Input, Select } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { Badge } from '../components/ui/Badge';
import { EmptyState } from '../components/ui/EmptyState';
import { PageSpinner } from '../components/ui/Spinner';
import { formatCurrency, formatDate, getEstadoVentaColor, downloadBlob } from '../utils/helpers';
import { Plus, Search, X, ChevronLeft, ChevronRight, FileDown, ShoppingCart } from 'lucide-react';

type VentaFilter = {
  estado: string;
  desde: string;
  hasta: string;
  page: number;
  page_size: number;
};

interface LineItemForm {
  producto_id: number | '';
  cantidad: number;
  precio_unitario: number;
}

interface VentaForm {
  cliente: string;
  metodo_pago: string;
  detalles: LineItemForm[];
}

const ESTADOS_VENTA = [
  { value: '', label: 'Todos' },
  { value: 'completada', label: 'Completada' },
  { value: 'pendiente', label: 'Pendiente' },
  { value: 'cancelada', label: 'Cancelada' },
];

const METODOS_PAGO = [
  { value: 'efectivo', label: 'Efectivo' },
  { value: 'tarjeta', label: 'Tarjeta' },
  { value: 'transferencia', label: 'Transferencia' },
  { value: 'otro', label: 'Otro' },
];

const initialLineItem: LineItemForm = { producto_id: '', cantidad: 1, precio_unitario: 0 };

function emptyForm(): VentaForm {
  return { cliente: '', metodo_pago: 'efectivo', detalles: [{ ...initialLineItem }] };
}

export function VentasPage() {
  const [ventas, setVentas] = useState<VentaListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [productos, setProductos] = useState<ProductoListItem[]>([]);
  const [filter, setFilter] = useState<VentaFilter>({ estado: '', desde: '', hasta: '', page: 1, page_size: 15 });
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<VentaForm>(emptyForm());
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');

  const fetchVentas = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params: Record<string, string | number | boolean> = { page: filter.page, page_size: filter.page_size };
      if (filter.estado) params.estado = filter.estado;
      if (filter.desde) params.desde = filter.desde;
      if (filter.hasta) params.hasta = filter.hasta;
      const res = await ventasApi.list(params);
      setVentas(res.data.results);
      setTotalPages(res.data.total_pages);
      setTotalCount(res.data.count);
    } catch {
      setError('Error al cargar las ventas');
    } finally {
      setLoading(false);
    }
  }, [filter]);

  const fetchProductos = useCallback(async () => {
    try {
      const res = await productosApi.list({ page_size: 200 });
      setProductos(res.data.results);
    } catch {
      // silent
    }
  }, []);

  useEffect(() => { fetchVentas(); }, [fetchVentas]);
  useEffect(() => { if (modalOpen) fetchProductos(); }, [modalOpen, fetchProductos]);

  const handleFilterChange = (key: keyof VentaFilter, value: string | number) => {
    setFilter((prev) => ({ ...prev, [key]: value, page: key === 'page' ? (value as number) : 1 }));
  };

  const openModal = () => {
    setForm(emptyForm());
    setFormError('');
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setFormError('');
  };

  const addLineItem = () => {
    setForm((prev) => ({ ...prev, detalles: [...prev.detalles, { ...initialLineItem }] }));
  };

  const removeLineItem = (idx: number) => {
    setForm((prev) => {
      const detalles = prev.detalles.filter((_, i) => i !== idx);
      return { ...prev, detalles: detalles.length === 0 ? [{ ...initialLineItem }] : detalles };
    });
  };

  const updateLineItem = (idx: number, field: keyof LineItemForm, value: number | '') => {
    setForm((prev) => {
      const detalles = prev.detalles.map((item, i) => {
        if (i !== idx) return item;
        const updated = { ...item, [field]: value };
        if (field === 'producto_id') {
          const prod = productos.find((p) => p.id === value);
          updated.precio_unitario = prod ? prod.precio : 0;
        }
        return updated;
      });
      return { ...prev, detalles };
    });
  };

  const calcSubtotal = (item: LineItemForm) => {
    const qty = Number(item.cantidad) || 0;
    const price = Number(item.precio_unitario) || 0;
    return qty * price;
  };

  const totalVenta = form.detalles.reduce((sum, item) => sum + calcSubtotal(item), 0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');

    const validDetalles = form.detalles.filter((d) => d.producto_id !== '');
    if (validDetalles.length === 0) {
      setFormError('Agrega al menos un producto a la venta');
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        cliente: form.cliente || null,
        metodo_pago: form.metodo_pago,
        detalles: validDetalles.map((d) => ({
          producto_id: d.producto_id,
          cantidad: Number(d.cantidad),
          precio_unitario: Number(d.precio_unitario),
        })),
      };
      await ventasApi.create(payload);
      closeModal();
      fetchVentas();
    } catch {
      setFormError('Error al crear la venta');
    } finally {
      setSubmitting(false);
    }
  };

  const productOptions = productos.map((p) => ({
    value: String(p.id),
    label: `${p.nombre} (${formatCurrency(p.precio)})`,
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Ventas</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {totalCount > 0 ? `${totalCount} venta${totalCount !== 1 ? 's' : ''} registrada${totalCount !== 1 ? 's' : ''}` : 'Gestión de ventas'}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" onClick={() => {
            ventasApi.list(filter).then((res) => {
              const blob = new Blob([JSON.stringify(res.data.results, null, 2)], { type: 'application/json' });
              downloadBlob(blob, 'ventas.json');
            });
          }}>
            <FileDown className="w-4 h-4" /> Exportar
          </Button>
          <Button onClick={openModal}>
            <Plus className="w-4 h-4" /> Nueva Venta
          </Button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4">
        <div className="flex flex-wrap items-end gap-3">
          <Select
            label="Estado"
            options={ESTADOS_VENTA}
            value={filter.estado}
            onChange={(e) => handleFilterChange('estado', e.target.value)}
            className="w-40"
          />
          <Input
            label="Desde"
            type="date"
            value={filter.desde}
            onChange={(e) => handleFilterChange('desde', e.target.value)}
            className="w-44"
          />
          <Input
            label="Hasta"
            type="date"
            value={filter.hasta}
            onChange={(e) => handleFilterChange('hasta', e.target.value)}
            className="w-44"
          />
          <Button variant="ghost" size="sm" onClick={() => setFilter({ estado: '', desde: '', hasta: '', page: 1, page_size: 15 })}>
            Limpiar
          </Button>
        </div>
      </div>

      {loading ? (
        <PageSpinner />
      ) : error ? (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-6 text-center">
          <p className="text-red-500">{error}</p>
          <Button variant="secondary" size="sm" className="mt-4" onClick={fetchVentas}>Reintentar</Button>
        </div>
      ) : ventas.length === 0 ? (
        <EmptyState
          title="No hay ventas"
          message={filter.estado || filter.desde || filter.hasta ? 'No se encontraron ventas con los filtros aplicados' : 'Aún no se han registrado ventas'}
          icon={<ShoppingCart className="w-8 h-8" />}
          action={!filter.estado && !filter.desde && !filter.hasta ? (
            <Button onClick={openModal}><Plus className="w-4 h-4" /> Nueva Venta</Button>
          ) : undefined}
        />
      ) : (
        <>
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                    <th className="text-left px-4 py-3 font-mono text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400">Factura</th>
                    <th className="text-left px-4 py-3 font-mono text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400">Cliente</th>
                    <th className="text-left px-4 py-3 font-mono text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400">Fecha</th>
                    <th className="text-right px-4 py-3 font-mono text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400">Total</th>
                    <th className="text-left px-4 py-3 font-mono text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400">Método Pago</th>
                    <th className="text-center px-4 py-3 font-mono text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400">Estado</th>
                    <th className="text-right px-4 py-3 font-mono text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                  {ventas.map((venta) => (
                    <tr key={venta.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                      <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">{venta.numero_factura}</td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300">{venta.cliente || '—'}</td>
                      <td className="px-4 py-3 text-gray-500 dark:text-gray-400">{formatDate(venta.fecha_venta)}</td>
                      <td className="px-4 py-3 text-right font-semibold text-gray-900 dark:text-white">{formatCurrency(venta.total)}</td>
                      <td className="px-4 py-3 text-gray-600 dark:text-gray-300 capitalize">{venta.metodo_pago || '—'}</td>
                      <td className="px-4 py-3 text-center">
                        <Badge variant={getEstadoVentaColor(venta.estado)}>{venta.estado}</Badge>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Button variant="ghost" size="sm">
                          <Search className="w-4 h-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Página {filter.page} de {totalPages}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={filter.page <= 1}
                  onClick={() => handleFilterChange('page', filter.page - 1)}
                >
                  <ChevronLeft className="w-4 h-4" /> Anterior
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={filter.page >= totalPages}
                  onClick={() => handleFilterChange('page', filter.page + 1)}
                >
                  Siguiente <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      <Modal isOpen={modalOpen} onClose={closeModal} title="Nueva Venta" size="xl">
        <form onSubmit={handleSubmit}>
          {formError && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-sm text-red-600 dark:text-red-400">
              {formError}
            </div>
          )}

          <div className="space-y-4">
            <Input
              label="Cliente"
              placeholder="Nombre del cliente (opcional)"
              value={form.cliente}
              onChange={(e) => setForm((prev) => ({ ...prev, cliente: e.target.value }))}
            />

            <Select
              label="Método de Pago"
              options={METODOS_PAGO}
              value={form.metodo_pago}
              onChange={(e) => setForm((prev) => ({ ...prev, metodo_pago: e.target.value }))}
            />

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-mono uppercase tracking-wider text-gray-500 dark:text-gray-400">Productos</label>
                <Button type="button" variant="ghost" size="sm" onClick={addLineItem}>
                  <Plus className="w-4 h-4" /> Agregar producto
                </Button>
              </div>

              <div className="space-y-3">
                {form.detalles.map((item, idx) => {
                  const subtotal = calcSubtotal(item);
                  return (
                    <div key={idx} className="flex items-start gap-2 p-3 rounded-lg bg-gray-50 dark:bg-gray-900">
                      <div className="flex-1 min-w-0">
                        <select
                          value={item.producto_id === '' ? '' : String(item.producto_id)}
                          onChange={(e) => updateLineItem(idx, 'producto_id', e.target.value ? Number(e.target.value) : '')}
                          className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        >
                          <option value="" disabled>Seleccionar producto</option>
                          {productOptions.map((opt) => (
                            <option key={opt.value} value={opt.value}>{opt.label}</option>
                          ))}
                        </select>
                      </div>
                      <div className="w-24 flex-shrink-0">
                        <input
                          type="number"
                          min={1}
                          value={item.cantidad}
                          onChange={(e) => updateLineItem(idx, 'cantidad', e.target.value ? Number(e.target.value) : '')}
                          className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-100 text-center focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        />
                      </div>
                      <div className="w-28 flex-shrink-0 text-right pt-2 text-sm font-semibold text-gray-900 dark:text-white">
                        {formatCurrency(subtotal)}
                      </div>
                      <button
                        type="button"
                        onClick={() => removeLineItem(idx)}
                        className="p-2 text-gray-400 hover:text-red-500 transition-colors flex-shrink-0"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-gray-200 dark:border-gray-700">
              <div className="text-right">
                <p className="text-xs font-mono uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-1">Total</p>
                <p className="text-2xl font-bold text-amber-500">{formatCurrency(totalVenta)}</p>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <Button type="button" variant="secondary" onClick={closeModal}>Cancelar</Button>
            <Button type="submit" loading={submitting}>
              <ShoppingCart className="w-4 h-4" /> Registrar Venta
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
