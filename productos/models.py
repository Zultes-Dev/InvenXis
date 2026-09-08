from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class Proveedor(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    CATEGORIAS = [
        ('Papelería', 'Papelería'),
        ('Tecnología', 'Tecnología'),
        ('Mobiliario', 'Mobiliario'),
        ('Insumos', 'Insumos'),
    ]

    razon_social = models.CharField('Razón social', max_length=200)
    nit = models.CharField('NIT', max_length=30)
    categoria = models.CharField('Categoría', max_length=50, choices=CATEGORIAS)
    contacto = models.CharField('Contacto principal', max_length=200)
    telefono = models.CharField('Teléfono', max_length=30)
    email = models.EmailField('Correo electrónico')
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default='activo')
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return f"{self.razon_social} ({self.nit})"


class Producto(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    CATEGORIAS = [
        ('Papelería', 'Papelería'),
        ('Tecnología', 'Tecnología'),
        ('Mobiliario', 'Mobiliario'),
        ('Insumos', 'Insumos'),
        ('Herramientas', 'Herramientas'),
    ]

    nombre = models.CharField('Nombre del producto', max_length=200)
    categoria = models.CharField('Categoría', max_length=50, choices=CATEGORIAS)
    precio = models.DecimalField('Precio unitario', max_digits=12, decimal_places=2,
                                 validators=[MinValueValidator(0)])
    cantidad = models.PositiveIntegerField('Cantidad en stock')
    stock_min = models.PositiveIntegerField('Stock mínimo', default=10)
    descripcion = models.TextField('Descripción', blank=True, null=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default='activo')
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha de actualización', auto_now=True)

    # Relación con proveedor
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos',
        verbose_name='Proveedor'
    )

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f"{self.nombre} ({self.categoria})"

    @property
    def valor_total(self):
        return self.precio * self.cantidad

    @property
    def estado_stock(self):
        if self.cantidad == 0:
            return 'sin_stock'
        elif self.cantidad <= self.stock_min:
            return 'bajo'
        return 'normal'


class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name='pedidos',
        verbose_name='Proveedor'
    )
    numero_orden = models.CharField('Número de orden', max_length=50, unique=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default='pendiente')
    fecha_pedido = models.DateTimeField('Fecha de pedido', auto_now_add=True)
    fecha_entrega_estimada = models.DateTimeField('Fecha entrega estimada', null=True, blank=True)
    fecha_entrega_real = models.DateTimeField('Fecha entrega real', null=True, blank=True)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0,
                                validators=[MinValueValidator(0)])
    observaciones = models.TextField('Observaciones', blank=True, null=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_creados',
        verbose_name='Creado por'
    )
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        ordering = ['-fecha_pedido']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido {self.numero_orden} - {self.proveedor.razon_social}"

    def calcular_total(self):
        self.total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.save(update_fields=['total', 'fecha_actualizacion'])
        return self.total


class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Pedido'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_pedido',
        verbose_name='Producto'
    )
    cantidad = models.PositiveIntegerField('Cantidad', validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField('Precio unitario', max_digits=12, decimal_places=2,
                                           validators=[MinValueValidator(0)])
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2, default=0,
                                   validators=[MinValueValidator(0)])
    recibido = models.PositiveIntegerField('Cantidad recibida', default=0)

    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad} (Pedido {self.pedido.numero_orden})"

    def save(self, *args, **kwargs):
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)

    @property
    def pendiente_recibir(self):
        return self.cantidad - self.recibido


class Venta(models.Model):
    ESTADOS = [
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('pendiente', 'Pendiente'),
    ]

    cliente = models.CharField('Cliente', max_length=200, blank=True, null=True)
    numero_factura = models.CharField('Número de factura', max_length=50, unique=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default='completada')
    fecha_venta = models.DateTimeField('Fecha de venta', auto_now_add=True)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0,
                                validators=[MinValueValidator(0)])
    metodo_pago = models.CharField('Método de pago', max_length=50, blank=True, null=True)
    observaciones = models.TextField('Observaciones', blank=True, null=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventas_creadas',
        verbose_name='Creado por'
    )
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha de actualización', auto_now=True)

    class Meta:
        ordering = ['-fecha_venta']
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def __str__(self):
        return f"Venta {self.numero_factura} - {self.total}"

    def calcular_total(self):
        self.total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.save(update_fields=['total', 'fecha_actualizacion'])
        return self.total


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Venta'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_venta',
        verbose_name='Producto'
    )
    cantidad = models.PositiveIntegerField('Cantidad', validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField('Precio unitario', max_digits=12, decimal_places=2,
                                           validators=[MinValueValidator(0)])
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2, default=0,
                                   validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad} (Venta {self.venta.numero_factura})"

    def save(self, *args, **kwargs):
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)


class ContadorDocumento(models.Model):
    """Consecutivo atómico por tipo de documento (FAC, NC)."""

    codigo = models.CharField('Código', max_length=10, unique=True)
    ultimo = models.PositiveBigIntegerField('Último número', default=0)

    class Meta:
        verbose_name = 'Contador de documento'
        verbose_name_plural = 'Contadores de documentos'

    def __str__(self):
        return f"{self.codigo}-{self.ultimo:06d}"


class Factura(models.Model):
    """Factura de venta con soporte de factura electrónica (DIAN-ready)."""

    ESTADOS = [
        ('borrador', 'Borrador'),
        ('validada_dian', 'Validada DIAN'),
        ('error', 'Error de emisión'),
        ('anulada', 'Anulada'),
    ]

    venta = models.OneToOneField(
        Venta, on_delete=models.PROTECT,
        related_name='factura', verbose_name='Venta')
    numero = models.CharField('Número', max_length=30, unique=True)
    fecha = models.DateTimeField('Fecha de emisión', auto_now_add=True)
    cliente_nombre = models.CharField('Cliente', max_length=200)
    cliente_documento = models.CharField('NIT/CC cliente', max_length=30)
    cliente_email = models.EmailField('Email cliente', blank=True, null=True)
    iva_porcentaje = models.DecimalField(
        'IVA %', max_digits=5, decimal_places=2, default=19)
    descuento = models.DecimalField(
        'Descuento', max_digits=12, decimal_places=2, default=0,
        validators=[MinValueValidator(0)])
    subtotal = models.DecimalField(
        'Subtotal', max_digits=12, decimal_places=2, default=0)
    iva = models.DecimalField('IVA', max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0)
    lineas = models.JSONField('Líneas (snapshot)', default=list)
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS,
                              default='borrador')
    cufe = models.CharField('CUFE', max_length=96, blank=True, default='')
    ubl_xml = models.TextField('UBL XML', blank=True, default='')
    respuesta_dian = models.JSONField('Respuesta DIAN', default=dict, blank=True)
    motivo_anulacion = models.TextField('Motivo anulación', blank=True, default='')
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='facturas_creadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'

    def __str__(self):
        return f"Factura {self.numero} - {self.total}"


class NotaCredito(models.Model):
    """Nota crédito que respalda la anulación de una factura validada."""

    factura = models.ForeignKey(
        Factura, on_delete=models.PROTECT,
        related_name='notas_credito', verbose_name='Factura')
    numero = models.CharField('Número', max_length=30, unique=True)
    motivo = models.TextField('Motivo')
    total = models.DecimalField('Total', max_digits=12, decimal_places=2)
    fecha = models.DateTimeField('Fecha', auto_now_add=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='notas_credito_creadas')

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Nota crédito'
        verbose_name_plural = 'Notas crédito'

    def __str__(self):
        return f"NC {self.numero} -> {self.factura.numero}"