from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'cantidad', 'estado', 'fecha_creacion')
    list_filter = ('categoria', 'estado')
    search_fields = ('nombre', 'descripcion')
    ordering = ('-fecha_creacion',)
