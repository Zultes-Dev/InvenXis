export interface PaginatedResponse<T> {
  success: boolean;
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  errors?: ApiError[];
}

export interface ApiError {
  message: string;
  code: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
}

export interface Producto {
  id: number;
  nombre: string;
  descripcion: string;
  categoria: string;
  cantidad: number;
  stock_min: number;
  precio: number;
  estado: 'activo' | 'inactivo' | 'descontinuado';
  proveedor: Proveedor | null;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

export interface ProductoListItem {
  id: number;
  nombre: string;
  categoria: string;
  cantidad: number;
  stock_min: number;
  precio: number;
  estado: string;
  proveedor: Proveedor | null;
  fecha_creacion: string;
}

export interface Proveedor {
  id: number;
  razon_social: string;
  nit: string;
  categoria: string;
  contacto: string;
  telefono: string;
  email: string;
  direccion: string;
  estado: 'activo' | 'inactivo';
  productos_count: number;
  pedidos_count: number;
  fecha_creacion: string;
  fecha_actualizacion: string;
}

export interface ProveedorListItem {
  id: number;
  razon_social: string;
  nit: string;
  categoria: string;
  contacto: string;
  telefono: string;
  email: string;
  estado: string;
  productos_count: number;
  pedidos_count: number;
  fecha_creacion: string;
}

export interface DetallePedido {
  id: number;
  producto: ProductoListItem;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
}

export interface Pedido {
  id: number;
  numero_orden: string;
  proveedor: ProveedorListItem;
  fecha_pedido: string;
  fecha_entrega_esperada: string | null;
  estado: 'pendiente' | 'parcial' | 'recibido' | 'cancelado';
  total: number;
  observaciones: string;
  creado_por: User;
  detalles: DetallePedido[];
  fecha_creacion: string;
  fecha_actualizacion: string;
}

export interface PedidoListItem {
  id: number;
  numero_orden: string;
  proveedor: ProveedorListItem;
  fecha_pedido: string;
  estado: string;
  total: number;
  creado_por: User;
}

export interface DetalleVenta {
  id: number;
  producto: ProductoListItem;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
}

export interface Venta {
  id: number;
  numero_factura: string;
  cliente: string | null;
  fecha_venta: string;
  total: number;
  metodo_pago: string | null;
  estado: 'completada' | 'cancelada' | 'pendiente';
  creado_por: User;
  detalles: DetalleVenta[];
  fecha_creacion: string;
  fecha_actualizacion: string;
}

export interface VentaListItem {
  id: number;
  numero_factura: string;
  cliente: string | null;
  fecha_venta: string;
  total: number;
  metodo_pago: string | null;
  estado: string;
  creado_por: User;
}

export interface DashboardKPI {
  total_productos: number;
  stock_bajo: number;
  sin_stock: number;
  total_proveedores: number;
  proveedores_activos: number;
  valor_total: number;
  total_pedidos: number;
  pedidos_pendientes: number;
  total_ventas: number;
  ingresos_totales: number;
}

export interface DashboardData {
  kpi: DashboardKPI;
  productos_recientes: ProductoListItem[];
  pedidos_recientes: PedidoListItem[];
}

export interface CategoriaReporte {
  nombre: string;
  cantidad: number;
  valor: number;
}

export interface ReporteInventario {
  resumen: {
    total_productos: number;
    valor_total: number;
    stock_normal: number;
    stock_bajo: number;
    sin_stock: number;
  };
  categorias: CategoriaReporte[];
  productos_bajo_stock: ProductoListItem[];
  productos_sin_stock: ProductoListItem[];
}

export interface ProductoMasVendido {
  producto_id: number;
  nombre: string;
  categoria: string;
  precio: number;
  total_vendido: number;
  total_ingresos: number;
  veces_vendido: number;
}

export interface ReporteMasVendidos {
  ranking: ProductoMasVendido[];
  filtros: {
    top: number;
    desde: string | null;
    hasta: string | null;
  };
}

export interface ReporteVentas {
  resumen: {
    total_ventas: number;
    total_ingresos: number;
    promedio_venta: number;
  };
  ventas_recientes: VentaListItem[];
}

export type ExportType = 'inventario' | 'proveedores' | 'ventas';

export interface FormErrors {
  [key: string]: string | undefined;
}