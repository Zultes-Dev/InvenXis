"""P0 TDD: venta atómica + logout blacklist (RED primero)."""
import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from productos.models import Producto, Proveedor, Venta


@pytest.mark.django_db
class VentaAtomicaTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('vendedor', 'v@test.com', 'pass12345')
        self.prov = Proveedor.objects.create(
            razon_social='Prov Venta', nit='900.000.010-1', categoria='Papelería',
            contacto='T', telefono='3001110000', email='v@test.com',
        )
        self.prod = Producto.objects.create(
            nombre='Prod Venta', categoria='Papelería',
            precio=10000, cantidad=10, stock_min=2, proveedor=self.prov,
        )
        resp = self.client.post(
            reverse('productos:api_login'),
            {'username': 'vendedor', 'password': 'pass12345'}, format='json')
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {resp.data['data']['access']}")

    def test_crear_venta_descuenta_stock(self):
        """Crear venta descuenta stock exactamente."""
        resp = self.client.post(
            reverse('productos:api_ventas_list'),
            {'detalles': [{'producto': self.prod.id, 'cantidad': 3,
                           'precio_unitario': '10000.00'}]},
            format='json')
        assert resp.status_code == status.HTTP_201_CREATED, resp.content[:500]
        self.prod.refresh_from_db()
        assert self.prod.cantidad == 7

    def test_venta_sin_stock_no_crea_venta(self):
        """Stock insuficiente -> 400 y rollback total (no crea venta)."""
        ventas_antes = Venta.objects.count()
        resp = self.client.post(
            reverse('productos:api_ventas_list'),
            {'detalles': [{'producto': self.prod.id, 'cantidad': 99,
                           'precio_unitario': '10000.00'}]},
            format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST, resp.content[:500]
        assert Venta.objects.count() == ventas_antes
        self.prod.refresh_from_db()
        assert self.prod.cantidad == 10


@pytest.mark.django_db
class LogoutBlacklistTests(APITestCase):
    def test_logout_invalida_refresh(self):
        """Logout blacklista el refresh: reusarlo debe fallar."""
        User.objects.create_user('logoutuser', 'l@test.com', 'pass12345')
        login = self.client.post(
            reverse('productos:api_login'),
            {'username': 'logoutuser', 'password': 'pass12345'}, format='json')
        refresh = login.data['data']['refresh']
        access = login.data['data']['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        out = self.client.post(
            reverse('productos:api_logout'), {'refresh': refresh}, format='json')
        assert out.status_code == status.HTTP_200_OK, out.content[:500]

        # Reusar el refresh debe fallar (blacklisted)
        retry = self.client.post(
            reverse('productos:api_refresh'), {'refresh': refresh}, format='json')
        assert retry.status_code in (status.HTTP_400_BAD_REQUEST,
                                     status.HTTP_401_UNAUTHORIZED), retry.content[:500]
