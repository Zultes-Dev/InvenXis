from django.db import models
from django.core.validators import MinValueValidator

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
