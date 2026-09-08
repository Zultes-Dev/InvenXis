"""Casos de uso de facturación: crear, emitir, anular (atómicos)."""
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from productos.models import ContadorDocumento, Factura, NotaCredito, Producto
from productos.fe.cufe import generar_cufe
from productos.fe.proveedores import get_proveedor

IVA_DEFAULT = Decimal('19.00')


def _q2(value):
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def siguiente_numero(codigo):
    """Consecutivo atómico: FAC-000001, NC-000001, ..."""
    with transaction.atomic():
        contador, _ = ContadorDocumento.objects.select_for_update().get_or_create(
            codigo=codigo)
        contador.ultimo = F('ultimo') + 1
        contador.save(update_fields=['ultimo'])
        contador.refresh_from_db()
        return f"{codigo}-{contador.ultimo:06d}"


def es_admin_fe(usuario):
    """Solo superusuarios o grupo Administradores anulan facturas."""
    return bool(
        usuario
        and usuario.is_authenticated
        and (usuario.is_superuser
             or usuario.groups.filter(name='Administradores').exists())
    )


def crear_factura(venta, *, cliente_nombre, cliente_documento,
                  cliente_email=None, descuento=0, iva_porcentaje=IVA_DEFAULT,
                  creado_por=None):
    """Crea la factura en borrador con snapshot de líneas y totales."""
    if venta.estado != 'completada':
        raise ValueError('Solo se facturan ventas completadas')
    if hasattr(venta, 'factura'):
        raise ValueError('La venta ya tiene factura')
    with transaction.atomic():
        numero = siguiente_numero('FAC')
        lineas = []
        subtotal = Decimal('0.00')
        for det in venta.detalles.select_related('producto').all():
            sub = _q2(det.precio_unitario * det.cantidad)
            lineas.append({
                'producto_id': det.producto_id,
                'descripcion': det.producto.nombre,
                'cantidad': det.cantidad,
                'precio_unitario': str(det.precio_unitario),
                'subtotal': str(sub),
            })
            subtotal += sub
        descuento = _q2(descuento or 0)
        base = subtotal - descuento
        iva = _q2(base * Decimal(iva_porcentaje) / Decimal('100'))
        total = base + iva
        factura = Factura.objects.create(
            venta=venta, numero=numero,
            cliente_nombre=cliente_nombre or (venta.cliente or 'Consumidor final'),
            cliente_documento=cliente_documento or '222222222222',
            cliente_email=cliente_email,
            iva_porcentaje=iva_porcentaje, descuento=descuento,
            subtotal=subtotal, iva=iva, total=total, lineas=lineas,
            creado_por=creado_por,
        )
        factura.cufe = generar_cufe(
            numero=factura.numero,
            fecha=timezone.localtime(factura.fecha).strftime('%Y-%m-%d %H:%M:%S'),
            nit_emisor='900123456',
            doc_adquiriente=factura.cliente_documento,
            total=f"{factura.total:.2f}", iva=f"{factura.iva:.2f}")
        factura.save(update_fields=['cufe'])
        return factura


def emitir_factura(factura, proveedor_nombre='mock'):
    """Genera UBL y emite ante el proveedor; deja validada_dian o error."""
    from productos.fe.ubl import construir_ubl
    if factura.estado == 'validada_dian':
        return factura
    if factura.estado == 'anulada':
        raise ValueError('Factura anulada no se puede emitir')
    xml = construir_ubl(factura)
    resultado = get_proveedor(proveedor_nombre).emitir(factura, xml)
    factura.ubl_xml = xml
    factura.respuesta_dian = {
        'resultado': 'aceptado' if resultado.aceptado else 'rechazado',
        'track_id': resultado.track_id,
        'mensaje': resultado.mensaje,
        **resultado.payload,
    }
    factura.estado = 'validada_dian' if resultado.aceptado else 'error'
    factura.save(update_fields=['ubl_xml', 'respuesta_dian', 'estado'])
    return factura


def anular_factura(factura, *, motivo, usuario):
    """Anula factura validada: crea NC, cancela la venta y devuelve stock."""
    if not es_admin_fe(usuario):
        raise PermissionError('Solo Administradores anulan facturas')
    if factura.estado == 'anulada':
        raise ValueError('La factura ya está anulada')
    if factura.estado != 'validada_dian':
        raise ValueError('Solo se anulan facturas validadas por DIAN')
    if not motivo:
        raise ValueError('El motivo de anulación es obligatorio')
    with transaction.atomic():
        numero_nc = siguiente_numero('NC')
        nc = NotaCredito.objects.create(
            factura=factura, numero=numero_nc, motivo=motivo,
            total=factura.total, creado_por=usuario)
        venta = factura.venta
        for det in venta.detalles.select_related('producto').all():
            Producto.objects.filter(pk=det.producto_id).update(
                cantidad=F('cantidad') + det.cantidad)
        venta.estado = 'cancelada'
        venta.save(update_fields=['estado'])
        factura.estado = 'anulada'
        factura.motivo_anulacion = motivo
        factura.save(update_fields=['estado', 'motivo_anulacion'])
        return nc
