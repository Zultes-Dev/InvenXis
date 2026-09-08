import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import {
  dashboardApi,
  facturasApi,
  productosApi,
  proveedoresApi,
  reportesApi,
  ventasApi,
} from '../api';
import { unwrap, unwrapPaginated } from '../lib/queryClient';
import type {
  DashboardData,
  Factura,
  ProductoListItem,
  ProveedorListItem,
  ReporteInventario,
  ReporteMasVendidos,
  ReporteVentas,
  VentaListItem,
} from '../types/api';

// ---------------------------------------------------------------- Dashboard
export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: async (): Promise<DashboardData> => unwrap(await dashboardApi.get()),
  });
}

// ---------------------------------------------------------------- Productos
export interface ProductosParams {
  page?: number;
  page_size?: number;
  search?: string;
  estado?: string;
  estado_stock?: string;
}

export function useProductos(params: ProductosParams) {
  return useQuery({
    queryKey: ['productos', params],
    queryFn: async () =>
      unwrapPaginated<ProductoListItem>(await productosApi.list(params)),
    placeholderData: keepPreviousData,
  });
}

export function useProveedoresActivos(enabled = true) {
  return useQuery({
    queryKey: ['proveedores-activos'],
    queryFn: async () =>
      unwrapPaginated<ProveedorListItem>(
        await proveedoresApi.list({ page_size: 100, estado: 'activo' }),
      ),
    enabled,
    staleTime: 60_000,
  });
}

export function useProductoMutations() {
  const qc = useQueryClient();
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['productos'] });
    qc.invalidateQueries({ queryKey: ['dashboard'] });
  };
  return {
    create: useMutation({
      mutationFn: (payload: unknown) => productosApi.create(payload),
      onSuccess: invalidate,
    }),
    update: useMutation({
      mutationFn: ({ id, payload }: { id: number; payload: unknown }) =>
        productosApi.update(id, payload),
      onSuccess: invalidate,
    }),
    remove: useMutation({
      mutationFn: (id: number) => productosApi.delete(id),
      onSuccess: invalidate,
    }),
  };
}

// --------------------------------------------------------------- Proveedores
export interface ProveedoresParams {
  page?: number;
  page_size?: number;
  search?: string;
  estado?: string;
}

export function useProveedores(params: ProveedoresParams) {
  return useQuery({
    queryKey: ['proveedores', params],
    queryFn: async () =>
      unwrapPaginated<ProveedorListItem>(await proveedoresApi.list(params)),
    placeholderData: keepPreviousData,
  });
}

export function useProveedorMutations() {
  const qc = useQueryClient();
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['proveedores'] });
    qc.invalidateQueries({ queryKey: ['proveedores-activos'] });
    qc.invalidateQueries({ queryKey: ['dashboard'] });
  };
  return {
    create: useMutation({
      mutationFn: (payload: unknown) => proveedoresApi.create(payload),
      onSuccess: invalidate,
    }),
    update: useMutation({
      mutationFn: ({ id, payload }: { id: number; payload: unknown }) =>
        proveedoresApi.update(id, payload),
      onSuccess: invalidate,
    }),
    remove: useMutation({
      mutationFn: (id: number) => proveedoresApi.delete(id),
      onSuccess: invalidate,
    }),
  };
}

export function usePedidos(proveedorId: number | null) {
  return useQuery({
    queryKey: ['pedidos', proveedorId],
    queryFn: async () =>
      unwrap(await proveedoresApi.getPedidos(proveedorId as number)),
    enabled: proveedorId !== null,
  });
}

// ------------------------------------------------------------------- Ventas
export interface VentasParams {
  page?: number;
  page_size?: number;
  estado?: string;
  desde?: string;
  hasta?: string;
}

export function useVentas(params: VentasParams) {
  return useQuery({
    queryKey: ['ventas', params],
    queryFn: async () =>
      unwrapPaginated<VentaListItem>(await ventasApi.list(params)),
    placeholderData: keepPreviousData,
  });
}

export function useCreateVenta() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: unknown) => ventasApi.create(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['ventas'] });
      qc.invalidateQueries({ queryKey: ['productos'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

// --------------------------------------------------------------- Facturación
export interface FacturasParams {
  page?: number;
  page_size?: number;
  estado?: string;
  q?: string;
}

export function useFacturas(params: FacturasParams) {
  return useQuery({
    queryKey: ['facturas', params],
    queryFn: async () =>
      unwrapPaginated<Factura>(await facturasApi.list(params)),
    placeholderData: keepPreviousData,
  });
}

export function useFacturaMutations() {
  const qc = useQueryClient();
  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['facturas'] });
    qc.invalidateQueries({ queryKey: ['ventas'] });
    qc.invalidateQueries({ queryKey: ['productos'] });
    qc.invalidateQueries({ queryKey: ['dashboard'] });
  };
  return {
    facturar: useMutation({
      mutationFn: ({ ventaId, payload }: { ventaId: number; payload: unknown }) =>
        facturasApi.facturarVenta(ventaId, payload),
      onSuccess: invalidate,
    }),
    emitir: useMutation({
      mutationFn: (id: number) => facturasApi.emitir(id),
      onSuccess: invalidate,
    }),
    anular: useMutation({
      mutationFn: ({ id, motivo }: { id: number; motivo: string }) =>
        facturasApi.anular(id, motivo),
      onSuccess: invalidate,
    }),
  };
}

// ------------------------------------------------------------------ Reportes
export function useReporteInventario(enabled = true) {
  return useQuery({
    queryKey: ['reporte-inventario'],
    queryFn: async (): Promise<ReporteInventario> =>
      unwrap(await reportesApi.inventario()),
    enabled,
  });
}

export function useReporteMasVendidos(top: number, enabled = true) {
  return useQuery({
    queryKey: ['reporte-mas-vendidos', top],
    queryFn: async (): Promise<ReporteMasVendidos> =>
      unwrap(await reportesApi.masVendidos({ top })),
    enabled,
  });
}

export function useReporteVentas(enabled = true) {
  return useQuery({
    queryKey: ['reporte-ventas'],
    queryFn: async (): Promise<ReporteVentas> =>
      unwrap(await reportesApi.ventas()),
    enabled,
  });
}
