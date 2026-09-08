from django.urls import path
from . import api_views

app_name = 'productos'

# API montada en /api/ (ver config/urls.py). Nombres compatibles con
# reverse('productos:api_*') usado en tests y frontend (/api/*).
urlpatterns = [
    # Health (público, sin auth)
    path('health/', api_views.api_health, name='api_health'),

    # Auth
    path('auth/login/', api_views.api_login, name='api_login'),
    path('auth/refresh/', api_views.api_refresh_token, name='api_refresh'),
    path('auth/logout/', api_views.api_logout, name='api_logout'),
    path('auth/me/', api_views.api_me, name='api_me'),

    # Productos
    path('productos/', api_views.ProductoListCreateView.as_view(), name='api_productos_list'),
    path('productos/<int:pk>/', api_views.ProductoDetailView.as_view(), name='api_productos_detail'),

    # Proveedores
    path('proveedores/', api_views.ProveedorListCreateView.as_view(), name='api_proveedores_list'),
    path('proveedores/<int:pk>/', api_views.ProveedorDetailView.as_view(), name='api_proveedores_detail'),

    # Pedidos (historial por proveedor)
    path('proveedores/<int:proveedor_pk>/pedidos/', api_views.PedidoListCreateView.as_view(), name='api_pedidos_list'),
    path('pedidos/<int:pk>/', api_views.PedidoDetailView.as_view(), name='api_pedidos_detail'),

    # Ventas
    path('ventas/', api_views.VentaListCreateView.as_view(), name='api_ventas_list'),
    path('ventas/<int:venta_id>/facturar/', api_views.facturar_venta, name='api_facturar_venta'),

    # Facturación
    path('facturas/', api_views.FacturaListView.as_view(), name='api_facturas_list'),
    path('facturas/<int:pk>/', api_views.FacturaDetailView.as_view(), name='api_facturas_detail'),
    path('facturas/<int:pk>/emitir/', api_views.emitir_factura_view, name='api_emitir_factura'),
    path('facturas/<int:pk>/anular/', api_views.anular_factura_view, name='api_anular_factura'),
    path('facturas/<int:pk>/pdf/', api_views.factura_pdf_view, name='api_factura_pdf'),
    path('facturas/<int:pk>/ubl/', api_views.factura_ubl_view, name='api_factura_ubl'),
    path('notas-credito/', api_views.NotaCreditoListView.as_view(), name='api_notas_credito_list'),

    # Dashboard
    path('dashboard/', api_views.dashboard_api, name='api_dashboard'),

    # Reportes
    path('reportes/inventario/', api_views.reporte_inventario_api, name='api_reporte_inventario'),
    path('reportes/mas-vendidos/', api_views.reporte_mas_vendidos_api, name='api_reporte_mas_vendidos'),
    path('reportes/ventas/', api_views.reporte_ventas_api, name='api_reporte_ventas'),

    # Exportaciones
    path('reportes/exportar/excel/<str:tipo>/', api_views.exportar_reporte_excel, name='api_exportar_excel'),
    path('reportes/exportar/pdf/<str:tipo>/', api_views.exportar_reporte_pdf, name='api_exportar_pdf'),
]
