from django.contrib import admin
from .models import (
    Producto, Proveedor, Pedido, DetallePedido, Venta, DetalleVenta,
    Factura, NotaCredito, ContadorDocumento,
)


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    autocomplete_fields = ['producto']


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    autocomplete_fields = ['producto']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'cantidad', 'stock_min', 'estado_stock', 'proveedor', 'estado', 'fecha_creacion')
    list_filter = ('categoria', 'estado', 'proveedor')
    search_fields = ('nombre', 'descripcion')
    ordering = ('-fecha_creacion',)
    autocomplete_fields = ['proveedor']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'nit', 'categoria', 'contacto', 'telefono', 'email', 'estado', 'fecha_creacion')
    list_filter = ('categoria', 'estado')
    search_fields = ('razon_social', 'nit', 'contacto', 'email')
    ordering = ('-fecha_creacion',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_orden', 'proveedor', 'estado', 'total', 'fecha_pedido', 'fecha_entrega_estimada')
    list_filter = ('estado', 'proveedor')
    search_fields = ('numero_orden', 'proveedor__razon_social')
    ordering = ('-fecha_pedido',)
    inlines = [DetallePedidoInline]


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal', 'recibido')
    list_filter = ('pedido__estado',)
    search_fields = ('pedido__numero_orden', 'producto__nombre')


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'cliente', 'estado', 'total', 'fecha_venta', 'metodo_pago')
    list_filter = ('estado', 'metodo_pago')
    search_fields = ('numero_factura', 'cliente')
    ordering = ('-fecha_venta',)
    inlines = [DetalleVentaInline]


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('venta__numero_factura', 'producto__nombre')


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente_nombre', 'total', 'estado', 'fecha')
    list_filter = ('estado',)
    search_fields = ('numero', 'cliente_nombre', 'cliente_documento', 'cufe')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('numero', 'cufe', 'ubl_xml', 'respuesta_dian')


@admin.register(NotaCredito)
class NotaCreditoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'factura', 'total', 'fecha')
    search_fields = ('numero', 'factura__numero')
    ordering = ('-fecha',)


@admin.register(ContadorDocumento)
class ContadorDocumentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'ultimo')
    search_fields = ('codigo',)
