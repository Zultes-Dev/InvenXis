"""Seed idempotente --force: purga demo y resiembra canónico."""
import pytest
from django.core.management import call_command
from rest_framework.test import APITestCase

from productos.models import Producto, Proveedor, Pedido, Venta


@pytest.mark.django_db
class SeedForceTests(APITestCase):
    def test_force_purga_extras_y_deja_canonico(self):
        """--force elimina datos extra y deja conteos canónicos."""
        call_command('seed_data')
        Proveedor.objects.create(
            razon_social='Extra', nit='999.999.999-9', categoria='Insumos',
            contacto='X', telefono='3000000000', email='extra@test.com',
        )
        assert Proveedor.objects.count() == 6

        call_command('seed_data', force=True)

        assert Proveedor.objects.count() == 5
        assert Producto.objects.count() == 15
        assert Venta.objects.count() == 15
        assert not Proveedor.objects.filter(nit='999.999.999-9').exists()

    def test_force_es_determinista(self):
        """Dos corridas --force dejan los mismos pedidos."""
        call_command('seed_data', force=True)
        pedidos_1 = sorted(Pedido.objects.values_list('numero_orden', flat=True))
        call_command('seed_data', force=True)
        pedidos_2 = sorted(Pedido.objects.values_list('numero_orden', flat=True))
        assert pedidos_1 == pedidos_2
        assert Proveedor.objects.count() == 5
        assert Producto.objects.count() == 15
