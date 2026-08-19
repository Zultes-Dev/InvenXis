"""Management command to load seed/initial data for InvenSoft Pro."""

import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from productos.models import Producto, Proveedor, Pedido, DetallePedido, Venta, DetalleVenta


class Command(BaseCommand):
    help = 'Carga datos de prueba para el sistema InvenSoft Pro'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Forzar recarga de datos')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Cargando datos de prueba ==='))

        # Crear usuarios si no existen
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@invensoft.com', 'admin')
            self.stdout.write('  Usuario admin creado (admin/admin)')
        else:
            self.stdout.write('  Usuario admin ya existe')

        operador, created = User.objects.get_or_create(
            username='operador',
            defaults={'email': 'operador@invensoft.com', 'is_staff': True}
        )
        if created:
            operador.set_password('operador123')
            operador.save()
            self.stdout.write('  Usuario operador creado (operador/operador123)')
        else:
            if not operador.is_staff:
                operador.is_staff = True
                operador.save()
            self.stdout.write('  Usuario operador actualizado (operador/operador123)')

        # Proveedores
        proveedores_data = [
            {'razon_social': 'Papelería La Central S.A.S.', 'nit': '900.123.456-7', 'categoria': 'Papelería', 'contacto': 'Carlos Méndez', 'telefono': '3105550101', 'email': 'carlos@lacentral.com'},
            {'razon_social': 'TecnoMundo Colombia', 'nit': '900.234.567-8', 'categoria': 'Tecnología', 'contacto': 'Ana Torres', 'telefono': '3105550102', 'email': 'ana@tecnomundo.co'},
            {'razon_social': 'Muebles Office Ltda.', 'nit': '900.345.678-9', 'categoria': 'Mobiliario', 'contacto': 'Pedro Ramírez', 'telefono': '3105550103', 'email': 'pedro@mueblesoffice.com'},
            {'razon_social': 'Insumos Industriales S.A.', 'nit': '900.456.789-0', 'categoria': 'Insumos', 'contacto': 'Lucía Fernández', 'telefono': '3105550104', 'email': 'lucia@insumosind.com'},
            {'razon_social': 'Distribuidora de Herramientas', 'nit': '900.567.890-1', 'categoria': 'Insumos', 'contacto': 'Jorge Martínez', 'telefono': '3105550105', 'email': 'jorge@distriherramientas.co'},
        ]

        proveedores = []
        for data in proveedores_data:
            prov, created = Proveedor.objects.get_or_create(
                nit=data['nit'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  Proveedor creado: {prov.razon_social}')
            proveedores.append(prov)

        # Productos
        productos_data = [
            {'nombre': 'Resma Papel Carta 75gr', 'categoria': 'Papelería', 'precio': 15000, 'cantidad': 200, 'stock_min': 20, 'proveedor': proveedores[0]},
            {'nombre': 'Lápiz Negro HB Nº2', 'categoria': 'Papelería', 'precio': 2500, 'cantidad': 500, 'stock_min': 100, 'proveedor': proveedores[0]},
            {'nombre': 'Carpeta Archivo Legal', 'categoria': 'Papelería', 'precio': 8500, 'cantidad': 150, 'stock_min': 30, 'proveedor': proveedores[0]},
            {'nombre': 'Monitor 27" 4K IPS', 'categoria': 'Tecnología', 'precio': 1250000, 'cantidad': 15, 'stock_min': 5, 'proveedor': proveedores[1]},
            {'nombre': 'Teclado Mecánico RGB', 'categoria': 'Tecnología', 'precio': 189000, 'cantidad': 8, 'stock_min': 10, 'proveedor': proveedores[1]},
            {'nombre': 'Mouse Inalámbrico', 'categoria': 'Tecnología', 'precio': 78000, 'cantidad': 30, 'stock_min': 15, 'proveedor': proveedores[1]},
            {'nombre': 'Escritorio Ejecutivo', 'categoria': 'Mobiliario', 'precio': 890000, 'cantidad': 12, 'stock_min': 5, 'proveedor': proveedores[2]},
            {'nombre': 'Silla Ergonómica', 'categoria': 'Mobiliario', 'precio': 650000, 'cantidad': 3, 'stock_min': 5, 'proveedor': proveedores[2]},
            {'nombre': 'Archivador Metálico', 'categoria': 'Mobiliario', 'precio': 420000, 'cantidad': 20, 'stock_min': 5, 'proveedor': proveedores[2]},
            {'nombre': 'Caja de Resaltadores x6', 'categoria': 'Papelería', 'precio': 12000, 'cantidad': 0, 'stock_min': 15, 'proveedor': proveedores[0]},
            {'nombre': 'Tóner Impresora HP', 'categoria': 'Tecnología', 'precio': 245000, 'cantidad': 6, 'stock_min': 8, 'proveedor': proveedores[1]},
            {'nombre': 'Pack Folios A4 x500', 'categoria': 'Papelería', 'precio': 18500, 'cantidad': 120, 'stock_min': 25, 'proveedor': proveedores[0]},
            {'nombre': 'Cable USB-C 2m', 'categoria': 'Tecnología', 'precio': 25000, 'cantidad': 0, 'stock_min': 20, 'proveedor': proveedores[1]},
            {'nombre': 'Mesa de Juntas 8 puestos', 'categoria': 'Mobiliario', 'precio': 2100000, 'cantidad': 2, 'stock_min': 1, 'proveedor': proveedores[2]},
            {'nombre': 'Guantes de Seguridad', 'categoria': 'Insumos', 'precio': 8500, 'cantidad': 100, 'stock_min': 20, 'proveedor': proveedores[3]},
        ]

        productos = []
        for data in productos_data:
            prov_data = data.pop('proveedor')
            prod, created = Producto.objects.get_or_create(
                nombre=data['nombre'],
                defaults={**data, 'proveedor': prov_data}
            )
            if created:
                self.stdout.write(f'  Producto creado: {prod.nombre}')
            else:
                # Actualizar datos
                for k, v in data.items():
                    setattr(prod, k, v)
                prod.proveedor = prov_data
                prod.save()
                self.stdout.write(f'  Producto actualizado: {prod.nombre}')
            productos.append(prod)

        # Pedidos (historial por proveedor)
        estados_pedido = ['pendiente', 'en_proceso', 'completado', 'cancelado']
        admin_user = User.objects.filter(is_superuser=True).first()

        for i, proveedor in enumerate(proveedores[:3]):
            for j in range(random.randint(2, 4)):
                fecha_pedido = timezone.now() - timedelta(days=random.randint(1, 60), hours=random.randint(0, 23))
                num_orden = f'PO-{timezone.now().strftime("%Y%m")}-{i * 10 + j + 1:03d}'

                pedido, created = Pedido.objects.get_or_create(
                    numero_orden=num_orden,
                    defaults={
                        'proveedor': proveedor,
                        'estado': random.choice(estados_pedido),
                        'fecha_pedido': fecha_pedido,
                        'creado_por': admin_user,
                    }
                )
                if created:
                    # Agregar 1-3 productos aleatorios
                    for _ in range(random.randint(1, 3)):
                        prod = random.choice(productos)
                        cantidad = random.randint(5, 50)
                        DetallePedido.objects.create(
                            pedido=pedido,
                            producto=prod,
                            cantidad=cantidad,
                            precio_unitario=prod.precio,
                            recibido=random.randint(0, cantidad) if pedido.estado == 'completado' else 0,
                        )
                    pedido.calcular_total()
                    self.stdout.write(f'  Pedido creado: {pedido.numero_orden} - {proveedor.razon_social}')

        # Ventas
        for i in range(15):
            fecha_venta = timezone.now() - timedelta(days=random.randint(1, 45), hours=random.randint(0, 23))
            num_factura = f'FAC-{timezone.now().strftime("%Y")}-{i + 1:04d}'

            venta, created = Venta.objects.get_or_create(
                numero_factura=num_factura,
                defaults={
                    'cliente': random.choice(['Cliente Genérico', 'Empresa ABC S.A.S.', 'Comercial XYZ Ltda.', None]),
                    'estado': 'completada' if random.random() > 0.2 else 'cancelada',
                    'fecha_venta': fecha_venta,
                    'metodo_pago': random.choice(['Efectivo', 'Tarjeta Débito', 'Tarjeta Crédito', 'Transferencia']),
                    'creado_por': admin_user,
                }
            )
            if created:
                for _ in range(random.randint(1, 4)):
                    prod = random.choice(productos)
                    if prod.cantidad > 0:
                        cantidad = min(random.randint(1, 5), prod.cantidad)
                        DetalleVenta.objects.create(
                            venta=venta,
                            producto=prod,
                            cantidad=cantidad,
                            precio_unitario=prod.precio,
                        )
                venta.calcular_total()
                self.stdout.write(f'  Venta creada: {venta.numero_factura}')

        self.stdout.write(self.style.SUCCESS('=== Datos de prueba cargados exitosamente ==='))
        self.stdout.write(self.style.SUCCESS(f'  Usuarios: admin/admin | operador/operador123'))
        self.stdout.write(self.style.SUCCESS(f'  Productos: {Producto.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Proveedores: {Proveedor.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Pedidos: {Pedido.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Ventas: {Venta.objects.count()}'))
