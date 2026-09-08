"""Tests for InvenXis - Sistema de Gestión de Inventarios."""

import json
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import Producto, Proveedor, Pedido, DetallePedido, Venta, DetalleVenta


# =============================================================================
# MODEL TESTS
# =============================================================================

class ModelTests(TestCase):
    """Pruebas unitarias de modelos."""

    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            razon_social='Proveedor Test S.A.S.',
            nit='900.000.001-1',
            categoria='Papelería',
            contacto='Juan Pérez',
            telefono='3001112233',
            email='juan@test.com',
        )

    def test_producto_creation(self):
        """RFU-01: Registrar producto correctamente."""
        producto = Producto.objects.create(
            nombre='Producto Test',
            categoria='Papelería',
            precio=15000,
            cantidad=100,
            stock_min=10,
            proveedor=self.proveedor,
        )
        self.assertEqual(Producto.objects.count(), 1)
        self.assertEqual(producto.nombre, 'Producto Test')
        self.assertEqual(float(producto.precio), 15000.0)
        self.assertEqual(producto.cantidad, 100)
        self.assertEqual(producto.estado_stock, 'normal')
        self.assertEqual(float(producto.valor_total), 1500000.0)

    def test_producto_sin_stock(self):
        """Verificar estado 'sin_stock' cuando cantidad es 0."""
        producto = Producto.objects.create(
            nombre='Sin Stock',
            categoria='Papelería',
            precio=10000,
            cantidad=0,
            proveedor=self.proveedor,
        )
        self.assertEqual(producto.estado_stock, 'sin_stock')

    def test_producto_stock_bajo(self):
        """Verificar estado 'bajo' cuando cantidad <= stock_min."""
        producto = Producto.objects.create(
            nombre='Stock Bajo',
            categoria='Papelería',
            precio=10000,
            cantidad=5,
            stock_min=10,
            proveedor=self.proveedor,
        )
        self.assertEqual(producto.estado_stock, 'bajo')

    def test_proveedor_creation(self):
        """RFU-05: Registrar proveedor correctamente."""
        self.assertEqual(Proveedor.objects.count(), 1)
        self.assertEqual(self.proveedor.razon_social, 'Proveedor Test S.A.S.')
        self.assertEqual(self.proveedor.estado, 'activo')

    def test_proveedor_str(self):
        """Verificar representación string de Proveedor."""
        self.assertEqual(str(self.proveedor), 'Proveedor Test S.A.S. (900.000.001-1)')


class PedidoModelTests(TestCase):
    """Pruebas del modelo Pedido (RFU-07)."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass123')
        self.proveedor = Proveedor.objects.create(
            razon_social='Prov Pedidos',
            nit='900.000.002-2',
            categoria='Tecnología',
            contacto='Ana',
            telefono='3001112244',
            email='ana@test.com',
        )
        self.producto = Producto.objects.create(
            nombre='Laptop Test',
            categoria='Tecnología',
            precio=2500000,
            cantidad=10,
            stock_min=2,
            proveedor=self.proveedor,
        )

    def test_pedido_creation(self):
        """Crear pedido con detalles."""
        pedido = Pedido.objects.create(
            proveedor=self.proveedor,
            numero_orden='PO-2026-001',
            estado='pendiente',
            creado_por=self.user,
        )
        DetallePedido.objects.create(
            pedido=pedido,
            producto=self.producto,
            cantidad=3,
            precio_unitario=self.producto.precio,
        )
        pedido.calcular_total()
        self.assertEqual(pedido.total, Decimal('7500000.00'))
        self.assertEqual(pedido.detalles.count(), 1)


# =============================================================================
# VIEW TESTS (Template-based)
# =============================================================================

class ViewBaseTests(TestCase):
    """Pruebas de vistas web con autenticación."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_login_required(self):
        """Verificar que las vistas requieren autenticación."""
        self.client.logout()
        urls = [
            'productos:dashboard',
            'productos:lista',
            'productos:lista_proveedores',
            'productos:reportes',
        ]
        for url_name in urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 302, f'{url_name} no redirige a login')


# =============================================================================
# API TESTS
# =============================================================================

class APIAuthTests(APITestCase):
    """Pruebas de autenticación API."""

    def setUp(self):
        self.user = User.objects.create_user('apitest', 'api@test.com', 'apipass123')

    def test_api_login_success(self):
        """Inicio de sesión API correcto."""
        response = self.client.post(
            reverse('productos:api_login'),
            {'username': 'apitest', 'password': 'apipass123'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])

    def test_api_login_failure(self):
        """Inicio de sesión API con credenciales inválidas."""
        response = self.client.post(
            reverse('productos:api_login'),
            {'username': 'apitest', 'password': 'wrongpassword'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])


class APIProductoTests(APITestCase):
    """Pruebas CRUD de productos por API."""

    def setUp(self):
        self.user = User.objects.create_user('apitest', 'api@test.com', 'apipass123')
        self.proveedor = Proveedor.objects.create(
            razon_social='Prov API',
            nit='900.000.003-3',
            categoria='Papelería',
            contacto='Test',
            telefono='3001113355',
            email='provapi@test.com',
        )
        # Obtener token
        response = self.client.post(
            reverse('productos:api_login'),
            {'username': 'apitest', 'password': 'apipass123'},
            format='json'
        )
        self.token = response.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_producto_api(self):
        """RFU-01: Crear producto via API."""
        data = {
            'nombre': 'Producto API Test',
            'categoria': 'Tecnología',
            'precio': 85000,
            'cantidad': 50,
            'stock_min': 5,
            'proveedor': self.proveedor.id,
        }
        response = self.client.post(
            reverse('productos:api_productos_list'),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['nombre'], 'Producto API Test')

    def test_create_producto_invalid_precio(self):
        """RFU-01: Validar precio negativo."""
        data = {
            'nombre': 'Producto Inválido',
            'categoria': 'Tecnología',
            'precio': -100,
            'cantidad': 10,
        }
        response = self.client.post(
            reverse('productos:api_productos_list'),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_productos_api(self):
        """RFU-04: Listar productos via API."""
        Producto.objects.create(
            nombre='Prod 1', categoria='Papelería',
            precio=1000, cantidad=10, proveedor=self.proveedor
        )
        Producto.objects.create(
            nombre='Prod 2', categoria='Tecnología',
            precio=2000, cantidad=20, proveedor=self.proveedor
        )
        response = self.client.get(reverse('productos:api_productos_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_get_producto_detail_api(self):
        """Ver detalle de producto via API."""
        prod = Producto.objects.create(
            nombre='Prod Detail',
            categoria='Papelería',
            precio=50000,
            cantidad=30,
            proveedor=self.proveedor,
        )
        response = self.client.get(reverse('productos:api_productos_detail', args=[prod.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['nombre'], 'Prod Detail')

    def test_update_producto_api(self):
        """RFU-02: Editar producto via API."""
        prod = Producto.objects.create(
            nombre='Prod Original',
            categoria='Papelería',
            precio=50000,
            cantidad=30,
            proveedor=self.proveedor,
        )
        response = self.client.put(
            reverse('productos:api_productos_detail', args=[prod.id]),
            {'nombre': 'Prod Editado', 'categoria': 'Tecnología', 'precio': 75000, 'cantidad': 40},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['nombre'], 'Prod Editado')

    def test_delete_producto_api(self):
        """RFU-03: Eliminar producto via API."""
        prod = Producto.objects.create(
            nombre='Prod a Eliminar',
            categoria='Papelería',
            precio=50000,
            cantidad=30,
            proveedor=self.proveedor,
        )
        response = self.client.delete(reverse('productos:api_productos_detail', args=[prod.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Producto.objects.count(), 0)


class APIProveedorTests(APITestCase):
    """Pruebas CRUD de proveedores por API."""

    def setUp(self):
        self.user = User.objects.create_user('apitest2', 'api2@test.com', 'apipass123')
        self.proveedor = Proveedor.objects.create(
            razon_social='Prov Original',
            nit='900.000.004-4',
            categoria='Mobiliario',
            contacto='Test',
            telefono='3001114466',
            email='provoriginal@test.com',
        )
        response = self.client.post(
            reverse('productos:api_login'),
            {'username': 'apitest2', 'password': 'apipass123'},
            format='json'
        )
        self.token = response.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_proveedor_api(self):
        """RFU-05: Crear proveedor via API."""
        data = {
            'razon_social': 'Nuevo Proveedor API',
            'nit': '900.000.005-5',
            'categoria': 'Insumos',
            'contacto': 'Contacto Test',
            'telefono': '3001115577',
            'email': 'nuevo@api.com',
        }
        response = self.client.post(
            reverse('productos:api_proveedores_list'),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_proveedores_api(self):
        """RFU-06: Consultar proveedores via API."""
        response = self.client.get(reverse('productos:api_proveedores_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_update_proveedor_api(self):
        response = self.client.patch(
            reverse('productos:api_proveedores_detail', args=[self.proveedor.id]),
            {'contacto': 'Nuevo Contacto'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['contacto'], 'Nuevo Contacto')


class APIReporteTests(APITestCase):
    """Pruebas de reportes via API."""

    def setUp(self):
        self.user = User.objects.create_user('reportuser', 'report@test.com', 'reportpass')
        self.proveedor = Proveedor.objects.create(
            razon_social='Prov Reporte',
            nit='900.000.006-6',
            categoria='Papelería',
            contacto='Test',
            telefono='3001116688',
            email='report@test.com',
        )
        self.producto = Producto.objects.create(
            nombre='Prod Reporte',
            categoria='Papelería',
            precio=10000,
            cantidad=50,
            proveedor=self.proveedor,
        )
        response = self.client.post(
            reverse('productos:api_login'),
            {'username': 'reportuser', 'password': 'reportpass'},
            format='json'
        )
        self.token = response.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_reporte_inventario_api(self):
        """RFU-08: Reporte de inventario via API."""
        response = self.client.get(reverse('productos:api_reporte_inventario'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('resumen', response.data['data'])
        self.assertIn('categorias', response.data['data'])

    def test_reporte_mas_vendidos_api(self):
        """RFU-09: Reporte de productos más vendidos via API."""
        response = self.client.get(reverse('productos:api_reporte_mas_vendidos'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ranking', response.data['data'])


class APIExportTests(APITestCase):
    """Pruebas de exportación de reportes."""

    def setUp(self):
        self.user = User.objects.create_user('exportuser', 'export@test.com', 'exportpass')
        response = self.client.post(
            reverse('productos:api_login'),
            {'username': 'exportuser', 'password': 'exportpass'},
            format='json'
        )
        self.token = response.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_export_excel_inventario(self):
        """RFU-10: Exportar reporte de inventario a Excel."""
        response = self.client.get(
            reverse('productos:api_exportar_excel', args=['inventario'])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    def test_export_pdf_inventario(self):
        """RFU-10: Exportar reporte de inventario a PDF."""
        response = self.client.get(
            reverse('productos:api_exportar_pdf', args=['inventario'])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
