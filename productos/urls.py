from django.urls import path
from . import views
from . import api_views

app_name = 'productos'

# Web template URLs
web_urls = [
    path('', views.dashboard, name='dashboard'),
    path('productos/', views.lista_productos, name='lista'),
    path('productos/nuevo/', views.crear_producto, name='crear'),
    path('productos/<int:pk>/', views.detalle_producto, name='detalle'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar'),
    path('productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar'),
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedores/nuevo/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/<int:pk>/', views.detalle_proveedor, name='detalle_proveedor'),
    path('proveedores/<int:pk>/editar/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/<int:pk>/eliminar/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/inventario/', views.reporte_inventario, name='reporte_inventario'),
    path('reportes/inventario/excel/', views.reporte_inventario_excel, name='reporte_inventario_excel'),
    path('reportes/proveedores/', views.reporte_proveedores, name='reporte_proveedores'),
    path('reportes/proveedores/excel/', views.reporte_proveedores_excel, name='reporte_proveedores_excel'),
    path('reportes/completo/', views.reporte_completo, name='reporte_completo'),
    path('reportes/completo/excel/', views.reporte_completo_excel, name='reporte_completo_excel'),
]

# REST API URLs
api_urls = [
    # Auth
    path('api/auth/login/', api_views.api_login, name='api_login'),
    path('api/auth/refresh/', api_views.api_refresh_token, name='api_refresh'),
    path('api/auth/me/', api_views.api_me, name='api_me'),

    # Productos
    path('api/productos/', api_views.ProductoListCreateView.as_view(), name='api_productos_list'),
    path('api/productos/<int:pk>/', api_views.ProductoDetailView.as_view(), name='api_productos_detail'),

    # Proveedores
    path('api/proveedores/', api_views.ProveedorListCreateView.as_view(), name='api_proveedores_list'),
    path('api/proveedores/<int:pk>/', api_views.ProveedorDetailView.as_view(), name='api_proveedores_detail'),

    # Pedidos (historial por proveedor)
    path('api/proveedores/<int:proveedor_pk>/pedidos/', api_views.PedidoListCreateView.as_view(), name='api_pedidos_list'),
    path('api/pedidos/<int:pk>/', api_views.PedidoDetailView.as_view(), name='api_pedidos_detail'),

    # Ventas
    path('api/ventas/', api_views.VentaListCreateView.as_view(), name='api_ventas_list'),

    # Dashboard
    path('api/dashboard/', api_views.dashboard_api, name='api_dashboard'),

    # Reportes
    path('api/reportes/inventario/', api_views.reporte_inventario_api, name='api_reporte_inventario'),
    path('api/reportes/mas-vendidos/', api_views.reporte_mas_vendidos_api, name='api_reporte_mas_vendidos'),
    path('api/reportes/ventas/', api_views.reporte_ventas_api, name='api_reporte_ventas'),

    # Exportaciones
    path('api/reportes/exportar/excel/<str:tipo>/', api_views.exportar_reporte_excel, name='api_exportar_excel'),
    path('api/reportes/exportar/pdf/<str:tipo>/', api_views.exportar_reporte_pdf, name='api_exportar_pdf'),
]

urlpatterns = web_urls + api_urls
