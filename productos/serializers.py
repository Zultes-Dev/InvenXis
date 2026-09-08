import uuid
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers
from .models import (
    Producto, Proveedor, Pedido, DetallePedido, Venta, DetalleVenta,
    Factura, NotaCredito,
)


class ProveedorSerializer(serializers.ModelSerializer):
    productos_count = serializers.IntegerField(read_only=True)
    pedidos_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Proveedor
        fields = [
            'id', 'razon_social', 'nit', 'categoria', 'contacto',
            'telefono', 'email', 'estado', 'productos_count', 'pedidos_count',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def validate_email(self, value):
        if value and Proveedor.objects.exclude(pk=self.instance.pk if self.instance else None).filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un proveedor con este email.")
        return value

    def validate_nit(self, value):
        if value and Proveedor.objects.exclude(pk=self.instance.pk if self.instance else None).filter(nit=value).exists():
            raise serializers.ValidationError("Ya existe un proveedor con este NIT.")
        return value


class ProveedorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'razon_social', 'nit', 'categoria', 'contacto', 'telefono', 'email', 'estado']


class ProductoSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.razon_social', read_only=True)
    proveedor_nit = serializers.CharField(source='proveedor.nit', read_only=True)
    estado_stock = serializers.CharField(read_only=True)
    valor_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'categoria', 'precio', 'cantidad', 'stock_min',
            'descripcion', 'estado', 'proveedor', 'proveedor_nombre', 'proveedor_nit',
            'estado_stock', 'valor_total', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def validate_precio(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio no puede ser negativo.")
        return value

    def validate_cantidad(self, value):
        if value < 0:
            raise serializers.ValidationError("La cantidad no puede ser negativa.")
        return value

    def validate_stock_min(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock mínimo no puede ser negativo.")
        return value


class ProductoListSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.razon_social', read_only=True)
    estado_stock = serializers.CharField(read_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'categoria', 'precio', 'cantidad', 'stock_min', 'estado', 'proveedor', 'proveedor_nombre', 'estado_stock']


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_categoria = serializers.CharField(source='producto.categoria', read_only=True)
    pendiente_recibir = serializers.IntegerField(read_only=True)

    class Meta:
        model = DetallePedido
        fields = [
            'id', 'producto', 'producto_nombre', 'producto_categoria',
            'cantidad', 'precio_unitario', 'subtotal', 'recibido', 'pendiente_recibir'
        ]
        read_only_fields = ['id', 'subtotal', 'pendiente_recibir']


class PedidoSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.razon_social', read_only=True)
    proveedor_nit = serializers.CharField(source='proveedor.nit', read_only=True)
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'proveedor', 'proveedor_nombre', 'proveedor_nit', 'numero_orden',
            'estado', 'fecha_pedido', 'fecha_entrega_estimada', 'fecha_entrega_real',
            'total', 'observaciones', 'creado_por', 'creado_por_nombre',
            'detalles', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'numero_orden', 'total', 'fecha_creacion', 'fecha_actualizacion']


class PedidoCreateSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'proveedor', 'numero_orden', 'estado', 'fecha_pedido',
            'fecha_entrega_estimada', 'observaciones', 'detalles'
        ]
        read_only_fields = ['id', 'numero_orden']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        pedido = Pedido.objects.create(**validated_data)
        for detalle_data in detalles_data:
            DetallePedido.objects.create(pedido=pedido, **detalle_data)
        pedido.calcular_total()
        return pedido

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if detalles_data is not None:
            instance.detalles.all().delete()
            for detalle_data in detalles_data:
                DetallePedido.objects.create(pedido=instance, **detalle_data)
            instance.calcular_total()

        return instance


class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_categoria = serializers.CharField(source='producto.categoria', read_only=True)

    class Meta:
        model = DetalleVenta
        fields = [
            'id', 'producto', 'producto_nombre', 'producto_categoria',
            'cantidad', 'precio_unitario', 'subtotal'
        ]
        read_only_fields = ['id', 'subtotal']


class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    factura_numero = serializers.SerializerMethodField()
    factura_estado = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = [
            'id', 'cliente', 'numero_factura', 'estado', 'fecha_venta',
            'total', 'metodo_pago', 'observaciones', 'creado_por', 'creado_por_nombre',
            'detalles', 'factura_numero', 'factura_estado',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'numero_factura', 'total', 'fecha_creacion', 'fecha_actualizacion']

    def get_factura_numero(self, obj):
        factura = getattr(obj, 'factura', None)
        return factura.numero if factura else None

    def get_factura_estado(self, obj):
        factura = getattr(obj, 'factura', None)
        return factura.estado if factura else None


class VentaCreateSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)

    class Meta:
        model = Venta
        fields = [
            'id', 'cliente', 'numero_factura', 'estado', 'fecha_venta',
            'metodo_pago', 'observaciones', 'detalles'
        ]
        read_only_fields = ['id', 'numero_factura']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        if not detalles_data:
            raise serializers.ValidationError(
                {'detalles': 'La venta debe incluir al menos un producto.'})
        with transaction.atomic():
            if not validated_data.get('numero_factura'):
                validated_data['numero_factura'] = (
                    f"FAC-{timezone.now().strftime('%Y%m%d')}"
                    f"-{uuid.uuid4().hex[:8].upper()}")
            venta = Venta.objects.create(**validated_data)
            for detalle_data in detalles_data:
                producto = Producto.objects.select_for_update().get(
                    pk=detalle_data['producto'].pk
                    if hasattr(detalle_data.get('producto'), 'pk')
                    else detalle_data['producto'])
                cantidad = detalle_data['cantidad']
                if producto.cantidad < cantidad:
                    raise serializers.ValidationError(
                        {'detalles': (
                            f"Stock insuficiente para {producto.nombre}: "
                            f"disponible {producto.cantidad}, "
                            f"solicitado {cantidad}.")})
                if not detalle_data.get('precio_unitario'):
                    detalle_data['precio_unitario'] = producto.precio
                DetalleVenta.objects.create(venta=venta, **detalle_data)
                Producto.objects.filter(pk=producto.pk).update(
                    cantidad=F('cantidad') - cantidad)
            venta.calcular_total()
            return venta


class FacturaSerializer(serializers.ModelSerializer):
    venta_numero = serializers.CharField(source='venta.numero_factura', read_only=True)

    class Meta:
        model = Factura
        fields = [
            'id', 'numero', 'fecha', 'venta', 'venta_numero',
            'cliente_nombre', 'cliente_documento', 'cliente_email',
            'iva_porcentaje', 'descuento', 'subtotal', 'iva', 'total',
            'lineas', 'estado', 'cufe', 'motivo_anulacion',
            'respuesta_dian', 'fecha_creacion',
        ]
        read_only_fields = ['id', 'numero', 'fecha', 'subtotal', 'iva', 'total',
                            'lineas', 'estado', 'cufe', 'respuesta_dian',
                            'fecha_creacion']


class NotaCreditoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotaCredito
        fields = ['id', 'numero', 'factura', 'motivo', 'total', 'fecha']
        read_only_fields = ['id', 'numero', 'total', 'fecha']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.DictField()