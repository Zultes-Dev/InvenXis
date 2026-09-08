"""Hardening senior: health, invalidación dashboard, factura única, doble gasto."""
import re
import pytest
from django.core.cache import cache
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from productos.models import Producto, Proveedor, Venta


def make_user(client, username='hard', password='pass12345'):
    User.objects.create_user(username, f'{username}@test.com', password)
    login = client.post(
        reverse('productos:api_login'),
        {'username': username, 'password': password}, format='json')
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {login.data['data']['access']}")


@pytest.mark.django_db
class HealthTests(APITestCase):
    def test_health_sin_auth(self):
        resp = self.client.get(reverse('productos:api_health'))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['data']['status'] == 'ok'
        assert resp.data['data']['db'] == 'ok'


@pytest.mark.django_db
class DashboardInvalidationTests(APITestCase):
    def test_crear_producto_invalida_dashboard(self):
        make_user(self.client)
        prov = Proveedor.objects.create(
            razon_social='Prov Dash', nit='900.000.020-1', categoria='Insumos',
            contacto='T', telefono='3001110000', email='d@test.com')
        cache.delete('dashboard_api:v1')
        r1 = self.client.get(reverse('productos:api_dashboard'))
        assert r1.status_code == status.HTTP_200_OK
        n = r1.data['data']['kpi']['total_productos']

        self.client.post(reverse('productos:api_productos_list'), {
            'nombre': 'Nuevo Prod', 'categoria': 'Insumos', 'precio': 1000,
            'cantidad': 5, 'proveedor': prov.id}, format='json')

        r2 = self.client.get(reverse('productos:api_dashboard'))
        assert r2.data['data']['kpi']['total_productos'] == n + 1


@pytest.mark.django_db
class VentaEdgeTests(APITestCase):
    def setUp(self):
        make_user(self.client, 'vend2')
        self.prov = Proveedor.objects.create(
            razon_social='Prov V', nit='900.000.021-1', categoria='Insumos',
            contacto='T', telefono='3001110000', email='v@test.com')
        self.prod = Producto.objects.create(
            nombre='Prod V', categoria='Insumos', precio=5000,
            cantidad=10, stock_min=2, proveedor=self.prov)

    def _vender(self, cantidad):
        return self.client.post(reverse('productos:api_ventas_list'), {
            'detalles': [{'producto': self.prod.id, 'cantidad': cantidad,
                          'precio_unitario': '5000.00'}]}, format='json')

    def test_doble_gasto_segundo_falla_y_no_descuenta(self):
        r1 = self._vender(8)
        assert r1.status_code == status.HTTP_201_CREATED
        r2 = self._vender(5)
        assert r2.status_code == status.HTTP_400_BAD_REQUEST
        self.prod.refresh_from_db()
        assert self.prod.cantidad == 2
        assert Venta.objects.count() == 1

    def test_venta_sin_detalles_400(self):
        resp = self.client.post(
            reverse('productos:api_ventas_list'), {'detalles': []}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert Venta.objects.count() == 0

    def test_facturas_unicas_con_formato(self):
        r1 = self._vender(1)
        r2 = self._vender(1)
        f1 = r1.data['data']['numero_factura']
        f2 = r2.data['data']['numero_factura']
        assert re.fullmatch(r'FAC-\d{8}-[0-9A-F]{8}', f1), f1
        assert re.fullmatch(r'FAC-\d{8}-[0-9A-F]{8}', f2), f2
        assert f1 != f2


@pytest.mark.django_db
class LoginThrottleTests(APITestCase):
    def test_login_masivo_429(self):
        User.objects.create_user('brute', 'b@test.com', 'pass12345')
        url = reverse('productos:api_login')
        codes = set()
        try:
            for _ in range(25):
                r = self.client.post(
                    url, {'username': 'brute', 'password': 'wrong'},
                    format='json')
                codes.add(r.status_code)
        finally:
            cache.clear()
        assert status.HTTP_429_TOO_MANY_REQUESTS in codes, codes
