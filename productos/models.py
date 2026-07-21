from django.db import models
from django.core.validators import MinValueValidator

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

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f"{self.nombre} ({self.categoria})"
