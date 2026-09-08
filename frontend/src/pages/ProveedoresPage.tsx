import { useEffect, useMemo, useState } from 'react';
import { proveedoresApi } from '../api';
import { useProveedores, useProveedorMutations } from '../hooks/useApi';
import type { ProveedorListItem } from '../types/api';
import { Button } from '../components/ui/Button';
import { Input, Select, Textarea } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { Badge } from '../components/ui/Badge';
import { Card } from '../components/ui/Card';
import { Table, Pagination } from '../components/ui/Table';
import { PageSpinner } from '../components/ui/Spinner';
import { Plus, Search, Edit2, Trash2, Building2, Package, ClipboardList } from 'lucide-react';

interface ProveedorFormData {
  razon_social: string;
  nit: string;
  categoria: string;
  contacto: string;
  telefono: string;
  email: string;
  direccion: string;
  estado: string;
}

const emptyFormData: ProveedorFormData = {
  razon_social: '',
  nit: '',
  categoria: '',
  contacto: '',
  telefono: '',
  email: '',
  direccion: '',
  estado: 'activo',
};

type FilterEstado = 'todos' | 'activo' | 'inactivo';

export default function ProveedoresPage() {
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [filterEstado, setFilterEstado] = useState<FilterEstado>('todos');
  const [page, setPage] = useState(1);

  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<ProveedorFormData>(emptyFormData);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [deletingName, setDeletingName] = useState('');

  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 400);
    return () => clearTimeout(timer);
  }, [search]);

  const listParams = useMemo(() => {
    const params: Record<string, string | number | boolean> = { page, page_size: 15 };
    if (debouncedSearch) params.search = debouncedSearch;
    if (filterEstado !== 'todos') params.estado = filterEstado;
    return params;
  }, [page, debouncedSearch, filterEstado]);

  const proveedoresQuery = useProveedores(listParams);
  const proveedores = proveedoresQuery.data?.results ?? [];
  const totalPages = proveedoresQuery.data?.total_pages ?? 1;
  const total = proveedoresQuery.data?.count ?? 0;
  const loading = proveedoresQuery.isLoading;
  const fetching = proveedoresQuery.isFetching;
  const error = proveedoresQuery.isError ? 'Error al cargar proveedores' : null;

  const mutations = useProveedorMutations();
  const saving = mutations.create.isPending || mutations.update.isPending;
  const deleting = mutations.remove.isPending;

  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 3000);
  };

  const openCreateModal = () => {
    setEditingId(null);
    setFormData(emptyFormData);
    setFormError(null);
    setModalOpen(true);
  };

  const openEditModal = async (proveedor: ProveedorListItem) => {
    setEditingId(proveedor.id);
    setFormData({
      razon_social: proveedor.razon_social,
      nit: proveedor.nit,
      categoria: proveedor.categoria,
      contacto: proveedor.contacto,
      telefono: '',
      email: '',
      direccion: '',
      estado: proveedor.estado,
    });
    setFormError(null);
    try {
      const res = await proveedoresApi.get(proveedor.id);
      const full = res.data.data;
      setFormData({
        razon_social: full.razon_social,
        nit: full.nit,
        categoria: full.categoria,
        contacto: full.contacto,
        telefono: full.telefono,
        email: full.email,
        direccion: full.direccion,
        estado: full.estado,
      });
    } catch {
      setFormError('Error al cargar datos del proveedor');
    }
    setModalOpen(true);
  };

  const handleFormChange = (field: keyof ProveedorFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    if (!formData.razon_social.trim()) {
      setFormError('La razón social es obligatoria');
      return;
    }
    if (!formData.nit.trim()) {
      setFormError('El NIT es obligatorio');
      return;
    }
    setFormError(null);
    const payload = {
      razon_social: formData.razon_social,
      nit: formData.nit,
      categoria: formData.categoria,
      contacto: formData.contacto,
      telefono: formData.telefono,
      email: formData.email,
      direccion: formData.direccion,
      estado: formData.estado,
    };
    const onSuccess = (message: string) => {
      showNotification('success', message);
      setModalOpen(false);
    };
    const onError = () => setFormError('Error al guardar el proveedor');
    if (editingId) {
      mutations.update.mutate(
        { id: editingId, payload },
        {
          onSuccess: () => onSuccess('Proveedor actualizado exitosamente'),
          onError,
        },
      );
    } else {
      mutations.create.mutate(payload, {
        onSuccess: () => onSuccess('Proveedor creado exitosamente'),
        onError,
      });
    }
  };

  const openDeleteModal = (proveedor: ProveedorListItem) => {
    setDeletingId(proveedor.id);
    setDeletingName(proveedor.razon_social);
    setDeleteModalOpen(true);
  };

  const handleDelete = () => {
    if (deletingId === null) return;
    mutations.remove.mutate(deletingId, {
      onSuccess: () => {
        showNotification('success', 'Proveedor eliminado exitosamente');
        setDeleteModalOpen(false);
        setDeletingId(null);
      },
      onError: () => showNotification('error', 'Error al eliminar el proveedor'),
    });
  };

  const columns = [
    {
      key: 'razon_social',
      header: 'Razón Social',
      render: (item: ProveedorListItem) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-100 dark:bg-blue-500/10 flex items-center justify-center flex-shrink-0">
            <Building2 className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <p className="font-medium text-gray-900 dark:text-white">{item.razon_social}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">{item.nit}</p>
          </div>
        </div>
      ),
    },
    {
      key: 'nit',
      header: 'NIT',
      render: (item: ProveedorListItem) => (
        <span className="text-xs font-mono text-gray-500 dark:text-gray-400">{item.nit}</span>
      ),
    },
    {
      key: 'contacto',
      header: 'Contacto',
      render: (item: ProveedorListItem) => (
        <span className="text-sm text-gray-700 dark:text-gray-300">{item.contacto}</span>
      ),
    },
    {
      key: 'email',
      header: 'Email',
      render: (item: ProveedorListItem) => (
        <span className="text-sm text-gray-500 dark:text-gray-400">{item.email || '—'}</span>
      ),
    },
    {
      key: 'telefono',
      header: 'Teléfono',
      render: (item: ProveedorListItem) => (
        <span className="text-sm font-mono text-gray-700 dark:text-gray-300">{item.telefono || '—'}</span>
      ),
    },
    {
      key: 'productos',
      header: 'Productos',
      render: (item: ProveedorListItem) => (
        <div className="flex items-center gap-2">
          <Package className="w-3.5 h-3.5 text-gray-400" />
          <span className="text-sm font-mono text-gray-700 dark:text-gray-300">{item.productos_count}</span>
          <span className="text-xs text-gray-400">/</span>
          <ClipboardList className="w-3.5 h-3.5 text-gray-400" />
          <span className="text-sm font-mono text-gray-700 dark:text-gray-300">{item.pedidos_count}</span>
        </div>
      ),
    },
    {
      key: 'estado',
      header: 'Estado',
      render: (item: ProveedorListItem) => (
        <Badge variant={item.estado === 'activo' ? 'success' : 'muted'}>
          {item.estado === 'activo' ? 'Activo' : 'Inactivo'}
        </Badge>
      ),
    },
    {
      key: 'acciones',
      header: 'Acciones',
      className: 'text-right',
      render: (item: ProveedorListItem) => (
        <div className="flex items-center justify-end gap-1">
          <Button variant="ghost" size="sm" aria-label={`Editar ${item.razon_social}`} onClick={() => openEditModal(item)}>
            <Edit2 className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" aria-label={`Eliminar ${item.razon_social}`} onClick={() => openDeleteModal(item)}>
            <Trash2 className="w-4 h-4 text-red-500" />
          </Button>
        </div>
      ),
    },
  ];

  if (loading && proveedores.length === 0) return <PageSpinner />;

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
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Proveedores</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {total} proveedor{total !== 1 ? 'es' : ''} registrado{total !== 1 ? 's' : ''}
          </p>
        </div>
        <Button iconLeft={<Plus className="w-4 h-4" />} onClick={openCreateModal}>
          Nuevo Proveedor
        </Button>
      </div>

      <Card>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Buscar por razón social, NIT o contacto..."
              iconLeft={<Search className="w-4 h-4" />}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="w-full sm:w-48">
            <Select
              options={[
                { value: 'todos', label: 'Todos los estados' },
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
      </Card>

      <Card padding={false}>
        {error ? (
          <div className="p-6 text-center">
            <p className="text-red-500 text-sm">{error}</p>
            <Button variant="secondary" size="sm" className="mt-3" onClick={() => proveedoresQuery.refetch()}>
              Reintentar
            </Button>
          </div>
        ) : (
          <>
            <Table
              columns={columns}
              data={proveedores}
              keyExtractor={(item) => item.id}
              loading={loading || fetching}
              emptyMessage="No se encontraron proveedores"
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
        title={editingId ? 'Editar Proveedor' : 'Nuevo Proveedor'}
        size="lg"
        footer={
          <>
            <Button variant="secondary" onClick={() => setModalOpen(false)}>
              Cancelar
            </Button>
            <Button onClick={handleSave} loading={saving}>
              {editingId ? 'Guardar Cambios' : 'Crear Proveedor'}
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
              label="Razón Social"
              placeholder="Nombre o razón social"
              value={formData.razon_social}
              onChange={(e) => handleFormChange('razon_social', e.target.value)}
            />
            <Input
              label="NIT"
              placeholder="NIT del proveedor"
              value={formData.nit}
              onChange={(e) => handleFormChange('nit', e.target.value)}
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Categoría"
              placeholder="Ej: Autopartes, Lubricantes..."
              value={formData.categoria}
              onChange={(e) => handleFormChange('categoria', e.target.value)}
            />
            <Input
              label="Contacto"
              placeholder="Nombre del contacto"
              value={formData.contacto}
              onChange={(e) => handleFormChange('contacto', e.target.value)}
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Teléfono"
              placeholder="Número de teléfono"
              value={formData.telefono}
              onChange={(e) => handleFormChange('telefono', e.target.value)}
            />
            <Input
              label="Email"
              type="email"
              placeholder="correo@ejemplo.com"
              value={formData.email}
              onChange={(e) => handleFormChange('email', e.target.value)}
            />
          </div>
          <Textarea
            label="Dirección"
            placeholder="Dirección del proveedor"
            value={formData.direccion}
            onChange={(e) => handleFormChange('direccion', e.target.value)}
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
      </Modal>

      <Modal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        title="Eliminar Proveedor"
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
          ¿Estás seguro de eliminar a <span className="font-semibold text-gray-900 dark:text-white">{deletingName}</span>? Esta acción no se puede deshacer.
        </p>
      </Modal>
    </div>
  );
}
