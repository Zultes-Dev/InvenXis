from django.contrib import admin
from .models import Producto, Proveedor

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'cantidad', 'stock_min', 'estado', 'fecha_creacion')
    list_filter = ('categoria', 'estado')
    search_fields = ('nombre', 'descripcion')
    ordering = ('-fecha_creacion',)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'nit', 'categoria', 'contacto', 'telefono', 'estado', 'fecha_creacion')
    list_filter = ('categoria', 'estado')
    search_fields = ('razon_social', 'nit', 'contacto')
    ordering = ('-fecha_creacion',)
