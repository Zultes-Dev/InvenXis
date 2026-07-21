from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('productos/', views.lista_productos, name='lista'),
    path('productos/nuevo/', views.crear_producto, name='crear'),
    path('productos/<int:pk>/', views.detalle_producto, name='detalle'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar'),
    path('productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar'),
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedores/nuevo/', views.crear_proveedor, name='crear_proveedor'),
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
