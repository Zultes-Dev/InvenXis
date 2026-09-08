"""Módulo de ventas completo: facturación + factura electrónica (DIAN-ready)."""
import re
import xml.etree.ElementTree as ET
import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse

from productos.models import Producto, Proveedor, Venta
from productos.fe.cufe import generar_cufe
from productos.fe.servicios import (
    crear_factura, emitir_factura, anular_factura, siguiente_numero,
)


@pytest.mark.django_db
class ConsecutivoTests(APITestCase):
    def test_consecutivo_atomico_unico(self):
        assert siguiente_numero('FAC') == 'FAC-000001'
        assert siguiente_numero('FAC') == 'FAC-000002'
        assert siguiente_numero('NC') == 'NC-000001'


@pytest.mark.django_db
class CufeTests(APITestCase):
    def test_cufe_sha384_determinista(self):
        c1 = generar_cufe(numero='FAC-000001', fecha='2026-01-15 10:00:00',
                          nit_emisor='900123456', doc_adquiriente='12345678',
                          total='119000.00', iva='19000.00')
        c2 = generar_cufe(numero='FAC-000001', fecha='2026-01-15 10:00:00',
                          nit_emisor='900123456', doc_adquiriente='12345678',
                          total='119000.00', iva='19000.00')
        assert re.fullmatch(r'[0-9a-f]{96}', c1), c1
        assert c1 == c2


def _venta_con_stock(cantidad=10, precio='10000.00'):
    from decimal import Decimal as D
    prov = Proveedor.objects.create(
        razon_social='Prov FE', nit='900.000.030-1', categoria='Insumos',
        contacto='T', telefono='3001110000', email='fe@test.com')
    prod = Producto.objects.create(
        nombre='Prod FE', categoria='Insumos', precio=D(precio),
        cantidad=cantidad, stock_min=1, proveedor=prov)
    user = User.objects.create_user('feuser', 'fe@test.com', 'pass12345')
    venta = Venta.objects.create(numero_factura='T-1', creado_por=user)
    from productos.models import DetalleVenta
    DetalleVenta.objects.create(
        venta=venta, producto=prod, cantidad=2, precio_unitario=D(precio))
    venta.calcular_total()
    return venta


@pytest.mark.django_db
class FacturaTests(APITestCase):
    def test_totales_iva_19(self):
        venta = _venta_con_stock()
        fac = crear_factura(venta, cliente_nombre='Cliente X',
                            cliente_documento='12345678')
        assert fac.subtotal == Decimal('20000.00')
        assert fac.iva == Decimal('3800.00')
        assert fac.total == Decimal('23800.00')
        assert fac.estado == 'borrador'
        assert fac.numero.startswith('FAC-')

    def test_ubl_bienformado_con_cufe(self):
        from productos.fe.ubl import construir_ubl
        venta = _venta_con_stock()
        fac = crear_factura(venta, cliente_nombre='Cliente X',
                            cliente_documento='12345678')
        xml = construir_ubl(fac)
        root = ET.fromstring(xml.encode('utf-8'))
        assert root.tag.endswith('Invoice')
        assert fac.numero in xml
        assert fac.cufe in xml

    def test_emitir_mock_valida(self):
        venta = _venta_con_stock()
        fac = crear_factura(venta, cliente_nombre='Cliente X',
                            cliente_documento='12345678')
        fac = emitir_factura(fac)
        assert fac.estado == 'validada_dian'
        assert fac.respuesta_dian['resultado'] == 'aceptado'

    def test_anular_restaura_stock_y_crea_nc(self):
        from productos.models import NotaCredito
        admin = User.objects.create_superuser('adminfe', 'a@test.com', 'pass12345')
        venta = _venta_con_stock(cantidad=10)
        fac = crear_factura(venta, cliente_nombre='Cliente X',
                            cliente_documento='12345678')
        emitir_factura(fac)
        prod = fac.venta.detalles.first().producto
        stock_antes = Producto.objects.get(pk=prod.pk).cantidad
        nc = anular_factura(fac, motivo='Devolución total', usuario=admin)
        assert fac.estado == 'anulada'
        assert isinstance(nc, NotaCredito)
        assert Producto.objects.get(pk=prod.pk).cantidad == stock_antes + 2

    def test_anular_sin_permiso_403(self):
        user = User.objects.create_user('oper', 'o@test.com', 'pass12345')
        venta = _venta_con_stock()
        fac = crear_factura(venta, cliente_nombre='C', cliente_documento='1')
        with pytest.raises(PermissionError):
            anular_factura(fac, motivo='X', usuario=user)


@pytest.mark.django_db
class FacturaApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            'apiadmin', 'aa@test.com', 'pass12345')
        resp = self.client.post(
            reverse('productos:api_login'),
            {'username': 'apiadmin', 'password': 'pass12345'}, format='json')
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {resp.data['data']['access']}")

    def test_facturar_venta_api(self):
        venta = _venta_con_stock()
        resp = self.client.post(
            reverse('productos:api_facturar_venta', args=[venta.id]),
            {'cliente_nombre': 'Cliente API', 'cliente_documento': '87654321',
             'cliente_email': 'c@test.com'}, format='json')
        assert resp.status_code == status.HTTP_201_CREATED, resp.content[:500]
        assert resp.data['data']['estado'] == 'borrador'

    def test_facturar_dos_veces_400(self):
        venta = _venta_con_stock()
        url = reverse('productos:api_facturar_venta', args=[venta.id])
        self.client.post(url, {'cliente_nombre': 'C'}, format='json')
        resp = self.client.post(url, {'cliente_nombre': 'C'}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_emitir_y_pdf_api(self):
        from productos.models import Factura
        venta = _venta_con_stock()
        fac = crear_factura(venta, cliente_nombre='C', cliente_documento='1')
        r1 = self.client.post(reverse('productos:api_emitir_factura', args=[fac.id]))
        assert r1.status_code == status.HTTP_200_OK
        assert Factura.objects.get(pk=fac.pk).estado == 'validada_dian'
        r2 = self.client.get(reverse('productos:api_factura_pdf', args=[fac.id]))
        assert r2.status_code == status.HTTP_200_OK
        assert r2['Content-Type'] == 'application/pdf'
