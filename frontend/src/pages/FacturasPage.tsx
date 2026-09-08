import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { facturasApi } from '../api';
import { useFacturas, useFacturaMutations } from '../hooks/useApi';
import type { Factura } from '../types/api';
import { Button } from '../components/ui/Button';
import { Input, Select, Textarea } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { Badge } from '../components/ui/Badge';
import { Card } from '../components/ui/Card';
import { Table, Pagination } from '../components/ui/Table';
import { PageSpinner } from '../components/ui/Spinner';
import { formatCurrency, formatDate, downloadBlob } from '../utils/helpers';
import { Plus, Search, Eye, Send, FileDown, Ban, FileCode } from 'lucide-react';

type FilterEstado = '' | 'borrador' | 'validada_dian' | 'error' | 'anulada';

const estadoVariant: Record<string, 'info' | 'success' | 'danger' | 'muted'> = {
  borrador: 'info',
  validada_dian: 'success',
  error: 'danger',
  anulada: 'muted',
};

const estadoLabel: Record<string, string> = {
  borrador: 'Borrador',
  validada_dian: 'Validada DIAN',
  error: 'Error',
  anulada: 'Anulada',
};

export function FacturasPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [filterEstado, setFilterEstado] = useState<FilterEstado>('');
  const [page, setPage] = useState(1);

  const [detailId, setDetailId] = useState<number | null>(null);
  const [anularId, setAnularId] = useState<number | null>(null);
  const [motivo, setMotivo] = useState('');
  const [downloading, setDownloading] = useState<string | null>(null);
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
    if (debouncedSearch) params.q = debouncedSearch;
    if (filterEstado) params.estado = filterEstado;
    return params;
  }, [page, debouncedSearch, filterEstado]);

  const facturasQuery = useFacturas(listParams);
  const facturas = facturasQuery.data?.results ?? [];
  const totalPages = facturasQuery.data?.total_pages ?? 1;
  const total = facturasQuery.data?.count ?? 0;
  const loading = facturasQuery.isLoading;
  const fetching = facturasQuery.isFetching;
  const error = facturasQuery.isError ? 'Error al cargar facturas' : null;

  const mutations = useFacturaMutations();

  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 3500);
  };

  const handleEmitir = (id: number) => {
    mutations.emitir.mutate(id, {
      onSuccess: () => showNotification('success', 'Factura validada ante la DIAN'),
      onError: () => showNotification('error', 'Error al emitir la factura'),
    });
  };

  const handleAnular = () => {
    if (anularId === null || !motivo.trim()) return;
    mutations.anular.mutate(
      { id: anularId, motivo: motivo.trim() },
      {
        onSuccess: () => {
          showNotification('success', 'Factura anulada con nota crédito');
          setAnularId(null);
          setMotivo('');
        },
        onError: () => showNotification('error', 'No se pudo anular (requiere Administradores)'),
      },
    );
  };

  const handleDownload = async (id: number, numero: string, kind: 'pdf' | 'ubl') => {
    const key = `${kind}-${id}`;
    setDownloading(key);
    try {
      const fn = kind === 'pdf' ? facturasApi.pdf : facturasApi.ubl;
      const res = await fn(id);
      downloadBlob(res.data, `factura-${numero}.${kind === 'pdf' ? 'pdf' : 'xml'}`);
    } catch {
      showNotification('error', `Error al descargar ${kind.toUpperCase()}`);
    } finally {
      setDownloading(null);
    }
  };

  const detail = facturas.find((f) => f.id === detailId) ?? null;

  const columns = [
    {
      key: 'numero',
      header: 'Número',
      render: (item: Factura) => (
        <span className="font-mono font-semibold text-gray-900 dark:text-white">{item.numero}</span>
      ),
    },
    {
      key: 'cliente',
      header: 'Cliente',
      render: (item: Factura) => (
        <div>
          <p className="font-medium text-gray-900 dark:text-white">{item.cliente_nombre}</p>
          <p className="text-xs font-mono text-gray-500 dark:text-gray-400">{item.cliente_documento}</p>
        </div>
      ),
    },
    {
      key: 'total',
      header: 'Total',
      render: (item: Factura) => (
        <span className="font-mono text-sm text-gray-900 dark:text-white">{formatCurrency(Number(item.total))}</span>
      ),
    },
    {
      key: 'estado',
      header: 'Estado',
      render: (item: Factura) => (
        <Badge variant={estadoVariant[item.estado] ?? 'info'}>{estadoLabel[item.estado] ?? item.estado}</Badge>
      ),
    },
    {
      key: 'fecha',
      header: 'Fecha',
      render: (item: Factura) => (
        <span className="text-xs font-mono text-gray-500 dark:text-gray-400">{formatDate(item.fecha)}</span>
      ),
    },
    {
      key: 'acciones',
      header: 'Acciones',
      className: 'text-right',
      render: (item: Factura) => (
        <div className="flex items-center justify-end gap-1">
          <Button variant="ghost" size="sm" aria-label={`Ver ${item.numero}`} onClick={() => setDetailId(item.id)}>
            <Eye className="w-4 h-4" />
          </Button>
          {item.estado === 'borrador' && (
            <Button variant="ghost" size="sm" aria-label={`Emitir ${item.numero}`} onClick={() => handleEmitir(item.id)}>
              <Send className="w-4 h-4 text-emerald-500" />
            </Button>
          )}
          <Button variant="ghost" size="sm" aria-label={`Descargar PDF ${item.numero}`} onClick={() => handleDownload(item.id, item.numero, 'pdf')}>
            <FileDown className="w-4 h-4" />
          </Button>
          {item.estado === 'validada_dian' && (
            <Button variant="ghost" size="sm" aria-label={`Anular ${item.numero}`} onClick={() => setAnularId(item.id)}>
              <Ban className="w-4 h-4 text-red-500" />
            </Button>
          )}
        </div>
      ),
    },
  ];

  if (loading && facturas.length === 0) return <PageSpinner />;

  return (
    <div className="space-y-6">
      {notification && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl shadow-lg text-sm font-medium ${
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
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Facturación</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {total} factura{total !== 1 ? 's' : ''} · facturación electrónica DIAN-ready
          </p>
        </div>
        <Button iconLeft={<Plus className="w-4 h-4" />} onClick={() => navigate('/ventas')}>
          Facturar venta
        </Button>
      </div>

      <Card>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Buscar por número, cliente o documento..."
              iconLeft={<Search className="w-4 h-4" />}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="w-full sm:w-48">
            <Select
              options={[
                { value: '', label: 'Todos los estados' },
                { value: 'borrador', label: 'Borrador' },
                { value: 'validada_dian', label: 'Validada DIAN' },
                { value: 'error', label: 'Error' },
                { value: 'anulada', label: 'Anulada' },
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
            <Button variant="secondary" size="sm" className="mt-3" onClick={() => facturasQuery.refetch()}>
              Reintentar
            </Button>
          </div>
        ) : (
          <>
            <Table
              columns={columns}
              data={facturas}
              keyExtractor={(item) => item.id}
              loading={loading || fetching}
              emptyMessage="No hay facturas. Factura una venta para empezar."
            />
            {totalPages > 1 && (
              <Pagination page={page} totalPages={totalPages} total={total} onPageChange={setPage} />
            )}
          </>
        )}
      </Card>

      <Modal isOpen={detailId !== null} onClose={() => setDetailId(null)} title={detail ? `Factura ${detail.numero}` : ''} size="lg">
        {detail && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant={estadoVariant[detail.estado] ?? 'info'}>{estadoLabel[detail.estado] ?? detail.estado}</Badge>
              <span className="text-xs font-mono text-gray-500 dark:text-gray-400">
                Venta {detail.venta_numero} · {formatDate(detail.fecha)}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 p-3">
                <p className="text-xs font-mono text-gray-500 mb-1">CLIENTE</p>
                <p className="font-medium text-gray-900 dark:text-white">{detail.cliente_nombre}</p>
                <p className="text-xs font-mono text-gray-500">{detail.cliente_documento}</p>
              </div>
              <div className="rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 p-3">
                <p className="text-xs font-mono text-gray-500 mb-1">TOTALES</p>
                <p className="text-xs font-mono text-gray-700 dark:text-gray-300">Subtotal: {formatCurrency(Number(detail.subtotal))}</p>
                <p className="text-xs font-mono text-gray-700 dark:text-gray-300">IVA ({detail.iva_porcentaje}%): {formatCurrency(Number(detail.iva))}</p>
                <p className="font-mono font-bold text-gray-900 dark:text-white">Total: {formatCurrency(Number(detail.total))}</p>
              </div>
            </div>
            <div>
              <p className="text-xs font-mono uppercase tracking-wider text-gray-500 mb-2">Líneas</p>
              {detail.lineas.map((l, i) => (
                <div key={i} className="flex justify-between text-sm py-1.5 border-b border-gray-100 dark:border-gray-800 last:border-0">
                  <span className="text-gray-900 dark:text-white">{l.descripcion} <span className="font-mono text-gray-500">×{l.cantidad}</span></span>
                  <span className="font-mono text-gray-700 dark:text-gray-300">{formatCurrency(Number(l.subtotal))}</span>
                </div>
              ))}
            </div>
            {detail.cufe && (
              <p className="text-[11px] font-mono text-gray-500 dark:text-gray-400 break-all">CUFE: {detail.cufe}</p>
            )}
            {detail.respuesta_dian?.track_id && (
              <p className="text-[11px] font-mono text-gray-500 dark:text-gray-400">Track DIAN: {detail.respuesta_dian.track_id}</p>
            )}
            <div className="flex gap-2">
              <Button variant="secondary" size="sm" iconLeft={<FileDown className="w-4 h-4" />} loading={downloading === `pdf-${detail.id}`} onClick={() => handleDownload(detail.id, detail.numero, 'pdf')}>
                PDF
              </Button>
              <Button variant="secondary" size="sm" iconLeft={<FileCode className="w-4 h-4" />} loading={downloading === `ubl-${detail.id}`} onClick={() => handleDownload(detail.id, detail.numero, 'ubl')}>
                UBL
              </Button>
            </div>
          </div>
        )}
      </Modal>

      <Modal isOpen={anularId !== null} onClose={() => { setAnularId(null); setMotivo(''); }} title="Anular factura" footer={
        <>
          <Button variant="secondary" onClick={() => { setAnularId(null); setMotivo(''); }}>Cancelar</Button>
          <Button variant="danger" onClick={handleAnular} loading={mutations.anular.isPending} disabled={!motivo.trim()}>
            Anular y crear nota crédito
          </Button>
        </>
      }>
        <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
          Se crea nota crédito, se cancela la venta y se devuelve el stock. Solo Administradores.
        </p>
        <Textarea placeholder="Motivo de anulación (obligatorio)" value={motivo} onChange={(e) => setMotivo(e.target.value)} />
      </Modal>
    </div>
  );
}
