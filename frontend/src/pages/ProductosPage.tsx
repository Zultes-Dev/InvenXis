import { useEffect, useState, useCallback } from 'react';
import { productosApi, proveedoresApi } from '../api';
import type { ProductoListItem, ProveedorListItem } from '../types/api';
import { Button } from '../components/ui/Button';
import { Input, Select, Textarea } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { Badge } from '../components/ui/Badge';
import { Card } from '../components/ui/Card';
import { Table, Pagination } from '../components/ui/Table';
import { PageSpinner } from '../components/ui/Spinner';
import { formatCurrency, getStockStatus } from '../utils/helpers';
import { Plus, Search, Edit2, Trash2, Package } from 'lucide-react';

interface ProductoFormData {
  nombre: string;
  descripcion: string;
  categoria: string;
  precio: string;
  cantidad: string;
  stock_min: string;
  proveedor: string;
  estado: string;
}

const emptyFormData: ProductoFormData = {
  nombre: '',
  descripcion: '',
  categoria: '',
  precio: '',
  cantidad: '',
  stock_min: '',
  proveedor: '',
  estado: 'activo',
};

type FilterEstado = '' | 'activo' | 'inactivo';
type FilterStock = 'todos' | 'Normal' | 'Stock Bajo' | 'Sin Stock';

export default function ProductosPage() {
  const [productos, setProductos] = useState<ProductoListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [filterEstado, setFilterEstado] = useState<FilterEstado>('');
  const [filterStock, setFilterStock] = useState<FilterStock>('todos');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<ProductoFormData>(emptyFormData);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [deletingName, setDeletingName] = useState('');
  const [deleting, setDeleting] = useState(false);

  const [proveedores, setProveedores] = useState<ProveedorListItem[]>([]);

  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 400);
    return () => clearTimeout(timer);
  }, [search]);

  const fetchProductos = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, string | number | boolean> = { page, page_size: 15 };
      if (debouncedSearch) params.search = debouncedSearch;
      if (filterEstado) params.estado = filterEstado;
      if (filterStock !== 'todos') params.estado_stock = filterStock;
      const res = await productosApi.list(params);
      setProductos(res.data.results);
      setTotalPages(res.data.total_pages);
      setTotal(res.data.count);
    } catch {
      setError('Error al cargar productos');
    } finally {
      setLoading(false);
    }
  }, [page, debouncedSearch, filterEstado, filterStock]);

  useEffect(() => {
    fetchProductos();
  }, [fetchProductos]);

  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 3000);
  };

  const openCreateModal = async () => {
    setEditingId(null);
    setFormData(emptyFormData);
    setFormError(null);
    try {
      const res = await proveedoresApi.list({ page_size: 100, estado: 'activo' });
      setProveedores(res.data.results);
    } catch {
      setProveedores([]);
    }
    setModalOpen(true);
  };

  const openEditModal = async (producto: ProductoListItem) => {
    setEditingId(producto.id);
    setFormData({
      nombre: producto.nombre,
      descripcion: '',
      categoria: producto.categoria,
      precio: String(producto.precio),
      cantidad: String(producto.cantidad),
      stock_min: String(producto.stock_min),
      proveedor: producto.proveedor ? String(producto.proveedor.id) : '',
      estado: producto.estado,
    });
    setFormError(null);
    try {
      const [proveedoresRes, productoRes] = await Promise.all([
        proveedoresApi.list({ page_size: 100, estado: 'activo' }),
        productosApi.get(producto.id),
      ]);
      setProveedores(proveedoresRes.data.results);
      const full = productoRes.data.data;
      setFormData({
        nombre: full.nombre,
        descripcion: full.descripcion,
        categoria: full.categoria,
        precio: String(full.precio),
        cantidad: String(full.cantidad),
        stock_min: String(full.stock_min),
        proveedor: full.proveedor ? String(full.proveedor.id) : '',
        estado: full.estado,
      });
    } catch {
      setProveedores([]);
    }
    setModalOpen(true);
  };

  const handleFormChange = (field: keyof ProductoFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    if (!formData.nombre.trim()) {
      setFormError('El nombre es obligatorio');
      return;
    }
    setSaving(true);
    setFormError(null);
    try {
      const payload = {
        nombre: formData.nombre,
        descripcion: formData.descripcion,
        categoria: formData.categoria,
        precio: Number(formData.precio),
        cantidad: Number(formData.cantidad),
        stock_min: Number(formData.stock_min),
        proveedor: formData.proveedor ? Number(formData.proveedor) : null,
        estado: formData.estado,
      };
      if (editingId) {
        await productosApi.update(editingId, payload);
        showNotification('success', 'Producto actualizado exitosamente');
      } else {
        await productosApi.create(payload);
        showNotification('success', 'Producto creado exitosamente');
      }
      setModalOpen(false);
      fetchProductos();
    } catch {
      setFormError('Error al guardar el producto');
    } finally {
      setSaving(false);
    }
  };

  const openDeleteModal = (producto: ProductoListItem) => {
    setDeletingId(producto.id);
    setDeletingName(producto.nombre);
    setDeleteModalOpen(true);
  };

  const handleDelete = async () => {
    if (deletingId === null) return;
    setDeleting(true);
    try {
      await productosApi.delete(deletingId);
      showNotification('success', 'Producto eliminado exitosamente');
      setDeleteModalOpen(false);
      setDeletingId(null);
      fetchProductos();
    } catch {
      showNotification('error', 'Error al eliminar el producto');
    } finally {
      setDeleting(false);
    }
  };

  const filterStockPills: FilterStock[] = ['todos', 'Normal', 'Stock Bajo', 'Sin Stock'];

  const columns = [
    {
      key: 'nombre',
      header: 'Nombre',
      render: (item: ProductoListItem) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-amber-100 dark:bg-amber-500/10 flex items-center justify-center flex-shrink-0">
            <Package className="w-4 h-4 text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <p className="font-medium text-gray-900 dark:text-white">{item.nombre}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">{item.categoria}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'categoria',
      header: 'Categoría',
      render: (item: ProductoListItem) => (
        <span className="text-xs font-mono text-gray-500 dark:text-gray-400">{item.categoria}</span>
      ),
    },
    {
      key: 'stock',
      header: 'Stock',
      render: (item: ProductoListItem) => {
        const ratio = item.stock_min > 0 ? item.cantidad / item.stock_min : 1;
        const barColor =
          item.cantidad === 0
            ? 'bg-red-500'
            : item.cantidad <= item.stock_min
              ? 'bg-amber-500'
              : 'bg-emerald-500';
        const barWidth = Math.min(Math.max((ratio / 3) * 100, 5), 100);
        return (
          <div className="flex items-center gap-2">
            <div className="w-20 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div className={`h-full rounded-full transition-all ${barColor}`} style={{ width: `${barWidth}%` }} />
            </div>
            <span className={`text-xs font-mono ${item.cantidad === 0 ? 'text-red-500' : item.cantidad <= item.stock_min ? 'text-amber-500' : 'text-emerald-500'}`}>
              {item.cantidad}
            </span>
          </div>
        );
      },
    },
    {
      key: 'precio',
      header: 'Precio',
      render: (item: ProductoListItem) => (
        <span className="font-mono text-sm text-gray-900 dark:text-white">{formatCurrency(item.precio)}</span>
      ),
    },
    {
      key: 'estado',
      header: 'Estado',
      render: (item: ProductoListItem) => {
        const status = getStockStatus(item.cantidad, item.stock_min);
        return <Badge variant={status.color}>{status.label}</Badge>;
      },
    },
    {
      key: 'acciones',
      header: 'Acciones',
      className: 'text-right',
      render: (item: ProductoListItem) => (
        <div className="flex items-center justify-end gap-1">
          <Button variant="ghost" size="sm" onClick={() => openEditModal(item)}>
            <Edit2 className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" onClick={() => openDeleteModal(item)}>
            <Trash2 className="w-4 h-4 text-red-500" />
          </Button>
        </div>
      ),
    },
  ];

  const categoriaOptions = [
    { value: '', label: 'Seleccionar categoría' },
    { value: 'Llantas', label: 'Llantas' },
    { value: 'Baterías', label: 'Baterías' },
    { value: 'Aceites', label: 'Aceites' },
    { value: 'Frenos', label: 'Frenos' },
    { value: 'Filtros', label: 'Filtros' },
    { value: 'Suspensión', label: 'Suspensión' },
    { value: 'Motor', label: 'Motor' },
    { value: 'Transmisión', label: 'Transmisión' },
    { value: 'Eléctrico', label: 'Eléctrico' },
    { value: 'Carrocería', label: 'Carrocería' },
    { value: 'Otros', label: 'Otros' },
  ];

  const proveedorOptions = [
    { value: '', label: 'Sin proveedor' },
    ...proveedores.map((p) => ({ value: String(p.id), label: p.razon_social })),
  ];

  if (loading && productos.length === 0) return <PageSpinner />;

  return (
    <div className="space-y-6">
      {notification && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl shadow-lg text-sm font-medium animate-in slide-in-from-right ${
            notification.type === 'success'
              ? 'bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20'
              : 'bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-500/20'
          }`}
        >
          {notification.message}
        </div>
      )}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Productos</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {total} producto{total !== 1 ? 's' : ''} registrado{total !== 1 ? 's' : ''}
          </p>
        </div>
        <Button iconLeft={<Plus className="w-4 h-4" />} onClick={openCreateModal}>
          Nuevo Producto
        </Button>
      </div>

      <Card>
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Buscar productos..."
                iconLeft={<Search className="w-4 h-4" />}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="w-full sm:w-48">
              <Select
                options={[
                  { value: '', label: 'Todos los estados' },
                  { value: 'activo', label: 'Activo' },
                  { value: 'inactivo', label: 'Inactivo' },
                ]}
                value={filterEstado}
                onChange={(e) => {
                  setFilterEstado(e.target.value as FilterEstado);
                  setPage(1);
                }}
              />
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {filterStockPills.map((pill) => (
              <button
                key={pill}
                onClick={() => {
                  setFilterStock(pill);
                  setPage(1);
                }}
                className={`px-3 py-1.5 text-xs font-mono rounded-full border transition-colors ${
                  filterStock === pill
                    ? 'bg-amber-500 text-gray-900 border-amber-500 font-semibold'
                    : 'border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                {pill === 'todos' ? 'Todos' : pill}
              </button>
            ))}
          </div>
        </div>
      </Card>

      <Card padding={false}>
        {error ? (
          <div className="p-6 text-center">
            <p className="text-red-500 text-sm">{error}</p>
            <Button variant="secondary" size="sm" className="mt-3" onClick={fetchProductos}>
              Reintentar
            </Button>
          </div>
        ) : (
          <>
            <Table
              columns={columns}
              data={productos}
              keyExtractor={(item) => item.id}
              loading={loading}
              emptyMessage="No se encontraron productos"
            />
            {totalPages > 1 && (
              <Pagination page={page} totalPages={totalPages} total={total} onPageChange={setPage} />
            )}
          </>
        )}
      </Card>

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingId ? 'Editar Producto' : 'Nuevo Producto'}
        size="lg"
        footer={
          <>
            <Button variant="secondary" onClick={() => setModalOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleSave} loading={saving}>
              {editingId ? 'Guardar Cambios' : 'Crear Producto'}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-sm text-red-600 dark:text-red-400">
              {formError}
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Nombre"
              placeholder="Nombre del producto"
              value={formData.nombre}
              onChange={(e) => handleFormChange('nombre', e.target.value)}
            />
            <Select
              label="Categoría"
              options={categoriaOptions}
              placeholder="Seleccionar categoría"
              value={formData.categoria}
              onChange={(e) => handleFormChange('categoria', e.target.value)}
            />
          </div>
          <Textarea
            label="Descripción"
            placeholder="Descripción del producto"
            value={formData.descripcion}
            onChange={(e) => handleFormChange('descripcion', e.target.value)}
          />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="Precio"
              type="number"
              placeholder="0"
              value={formData.precio}
              onChange={(e) => handleFormChange('precio', e.target.value)}
            />
            <Input
              label="Cantidad"
              type="number"
              placeholder="0"
              value={formData.cantidad}
              onChange={(e) => handleFormChange('cantidad', e.target.value)}
            />
            <Input
              label="Stock Mínimo"
              type="number"
              placeholder="0"
              value={formData.stock_min}
              onChange={(e) => handleFormChange('stock_min', e.target.value)}
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Select
              label="Proveedor"
              options={proveedorOptions}
              placeholder="Sin proveedor"
              value={formData.proveedor}
              onChange={(e) => handleFormChange('proveedor', e.target.value)}
            />
            <Select
              label="Estado"
              options={[
                { value: 'activo', label: 'Activo' },
                { value: 'inactivo', label: 'Inactivo' },
              ]}
              value={formData.estado}
              onChange={(e) => handleFormChange('estado', e.target.value)}
            />
          </div>
        </div>
      </Modal>

      <Modal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        title="Eliminar Producto"
        size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={() => setDeleteModalOpen(false)}>
              Cancelar
            </Button>
            <Button variant="danger" onClick={handleDelete} loading={deleting}>
              Eliminar
            </Button>
          </>
        }
      >
        <p className="text-sm text-gray-600 dark:text-gray-400">
          ¿Estás seguro de eliminar <span className="font-semibold text-gray-900 dark:text-white">{deletingName}</span>? Esta acción no se puede deshacer.
        </p>
      </Modal>
    </div>
  );
}
