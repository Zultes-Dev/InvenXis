"""Diagrama entidad-relación de InvenXis desde los modelos vivos.

Uso: python docs/ev02/generar_er.py
Sale: docs/ev02/ER-InvenXis.mmd  (Mermaid, se ve en GitHub/VS Code)
      docs/ev02/ER-InvenXis.svg  (vectorial para el PDF de entrega)
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps  # noqa: E402

VERDE = '#00843D'
AMBAR = '#E8A230'
GRIS = '#333333'

# (modelo, columna, fila) — layout fijo, campos extraídos en vivo.
LAYOUT = [
    ('User', 0, 0), ('Group', 0, 1),
    ('Proveedor', 1, 0), ('ContadorDocumento', 1, 1),
    ('Producto', 2, 0), ('Pedido', 2, 1), ('Venta', 2, 2),
    ('DetallePedido', 3, 0), ('DetalleVenta', 3, 1), ('Factura', 3, 2),
    ('NotaCredito', 4, 1),
]

MODELOS = {
    'User': apps.get_model('auth', 'User'),
    'Group': apps.get_model('auth', 'Group'),
    'Proveedor': apps.get_model('productos', 'Proveedor'),
    'Producto': apps.get_model('productos', 'Producto'),
    'Pedido': apps.get_model('productos', 'Pedido'),
    'DetallePedido': apps.get_model('productos', 'DetallePedido'),
    'Venta': apps.get_model('productos', 'Venta'),
    'DetalleVenta': apps.get_model('productos', 'DetalleVenta'),
    'Factura': apps.get_model('productos', 'Factura'),
    'NotaCredito': apps.get_model('productos', 'NotaCredito'),
    'ContadorDocumento': apps.get_model('productos', 'ContadorDocumento'),
}

CAMPOS_CLAVE = {
    'User': ['id', 'username', 'email', 'is_staff', 'is_superuser'],
    'Group': ['id', 'name'],
    'Proveedor': ['id', 'razon_social', 'nit', 'categoria', 'estado'],
    'Producto': ['id', 'nombre', 'categoria', 'precio', 'cantidad', 'stock_min',
                 'proveedor', 'estado'],
    'Pedido': ['id', 'numero_orden', 'proveedor', 'estado', 'total', 'creado_por'],
    'DetallePedido': ['id', 'pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal'],
    'Venta': ['id', 'numero_factura', 'cliente', 'estado', 'total', 'creado_por'],
    'DetalleVenta': ['id', 'venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal'],
    'Factura': ['id', 'numero', 'venta', 'cliente_nombre', 'subtotal', 'iva', 'total',
                'estado', 'cufe'],
    'NotaCredito': ['id', 'numero', 'factura', 'motivo', 'total', 'creado_por'],
    'ContadorDocumento': ['id', 'codigo', 'ultimo'],
}


def tipo_corto(f):
    from django.db import models as m
    if isinstance(f, (m.ForeignKey, m.OneToOneField)):
        return f.related_model.__name__
    if isinstance(f, m.ManyToManyField):
        return f.related_model.__name__ + '[]'
    return f.get_internal_type().replace('Field', '')


def atributos(nombre):
    modelo = MODELOS[nombre]
    por_nombre = {f.name: f for f in modelo._meta.get_fields()}
    filas = []
    for n in CAMPOS_CLAVE[nombre]:
        f = por_nombre[n]
        marcas = []
        if getattr(f, 'primary_key', False):
            marcas.append('PK')
        if getattr(f, 'remote_field', None) is not None and not getattr(f, 'many_to_many', False):
            marcas.append('FK')
        if getattr(f, 'unique', False) and not getattr(f, 'primary_key', False):
            marcas.append('UQ')
        if getattr(f, 'many_to_many', False):
            marcas.append('M2M')
        filas.append((n, tipo_corto(f), ','.join(marcas)))
    return filas


def relaciones():
    """(origen, destino, etiqueta_origen, etiqueta_destino)."""
    rels = []
    vistos = set()
    for nombre, modelo in MODELOS.items():
        for f in modelo._meta.get_fields():
            if not getattr(f, 'remote_field', None) or getattr(f, 'many_to_many', False):
                continue
            if f.auto_created:
                continue
            dest = f.related_model.__name__
            if dest not in MODELOS or (nombre, dest, f.name) in vistos:
                continue
            vistos.add((nombre, dest, f.name))
            from django.db.models import OneToOneField
            card = '1—1' if isinstance(f, OneToOneField) else 'N—1'
            rels.append((nombre, dest, card, f.name))
    # M2M User—Group (tabla intermedia auth_user_groups)
    rels.append(('User', 'Group', 'N—M', 'groups'))
    return rels


# ---------------- MERMAID ----------------
def mermaid():
    L = ['erDiagram']
    for nombre in MODELOS:
        L.append(f'    {nombre.upper().replace("DETALLE", "DET_")} {{')
        for n, t, marcas in atributos(nombre):
            tipo = ''.join(c for c in t if c.isalnum() or c in '[]') or 'txt'
            L.append(f'        {tipo} {n}')
        L.append('    }')
    nombre_m = {n: n.upper().replace('DETALLE', 'DET_') for n in MODELOS}
    for o, d, card, campo in relaciones():
        if card == '1—1':
            op = '||--||'
        elif card == 'N—M':
            op = '}o--o{'
        else:
            op = '}o--||'
        L.append(f'    {nombre_m[o]} {op} {nombre_m[d]} : "{campo}"')
    return '\n'.join(L) + '\n'


# ---------------- SVG ----------------
ANCHO, ALT_FILA, ALT_HEAD, PAD = 250, 19, 30, 8
X0, Y0, DX, DY = 30, 70, 300, 60


def svg():
    pos = {}
    cajas = {}
    for nombre, col, fila in LAYOUT:
        n = len(atributos(nombre))
        h = ALT_HEAD + n * ALT_FILA + PAD
        x = X0 + col * DX
        y = Y0 + fila * 260
        pos[nombre] = (x, y)
        cajas[nombre] = (x, y, h)
    max_x = max(x + ANCHO for x, y in pos.values()) + 40
    max_y = max(y + h for _, y, h in cajas.values()) + 60

    def esc(t):
        return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    S = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{max_x}" height="{max_y}" '
         f'font-family="Helvetica, Arial, sans-serif">',
         '<defs><marker id="fl" markerWidth="8" markerHeight="8" refX="7" refY="4" '
         'orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#555"/></marker></defs>',
         f'<text x="{X0}" y="32" font-size="22" font-weight="bold" fill="{VERDE}">'
         'InvenXis — Diagrama Entidad-Relación</text>',
         f'<text x="{X0}" y="52" font-size="12" fill="#666">Generado por introspección de '
         'los modelos Django (docs/ev02/generar_er.py)</text>']
    for o, d, card, campo in relaciones():
        if o not in pos or d not in pos:
            continue
        x1, y1, h1 = cajas[o]
        x2, y2, h2 = cajas[d]
        xa, ya = x1 + ANCHO, y1 + h1 / 2
        xb, yb = x2, y2 + h2 / 2
        xm = (xa + xb) / 2
        S.append(f'<path d="M{xa},{ya:.0f} C{xm:.0f},{ya:.0f} {xm:.0f},{yb:.0f} {xb},{yb:.0f}" '
                 f'fill="none" stroke="#555" stroke-width="1.5" marker-end="url(#fl)"/>')
        S.append(f'<text x="{xm:.0f}" y="{(ya + yb) / 2 - 4:.0f}" font-size="10" fill="{VERDE}" '
                 f'text-anchor="middle" font-weight="bold">{card} {esc(campo)}</text>')
    for nombre, col, fila in LAYOUT:
        x, y, h = cajas[nombre]
        modelo = MODELOS[nombre]
        S.append(f'<rect x="{x}" y="{y}" width="{ANCHO}" height="{h}" rx="8" fill="white" '
                 f'stroke="{VERDE}" stroke-width="2"/>')
        S.append(f'<rect x="{x}" y="{y}" width="{ANCHO}" height="{ALT_HEAD}" rx="8" fill="{VERDE}"/>')
        S.append(f'<rect x="{x}" y="{y + ALT_HEAD - 8}" width="{ANCHO}" height="8" fill="{VERDE}"/>')
        S.append(f'<text x="{x + 10}" y="{y + 20}" font-size="13" font-weight="bold" fill="white">'
                 f'{esc(nombre)}</text>')
        S.append(f'<text x="{x + ANCHO - 10}" y="{y + 20}" font-size="10" fill="#dff0e3" '
                 f'text-anchor="end">{esc(modelo._meta.db_table)}</text>')
        yy = y + ALT_HEAD + 14
        for n, t, marcas in atributos(nombre):
            color = '#b35400' if 'FK' in marcas or 'PK' in marcas else GRIS
            S.append(f'<text x="{x + 10}" y="{yy}" font-size="11" fill="{color}">{esc(n)}</text>')
            etiqueta = esc(t + (f" [{marcas}]" if marcas else ''))
            S.append(f'<text x="{x + ANCHO - 10}" y="{yy}" font-size="10" fill="#777" '
                     f'text-anchor="end">{etiqueta}</text>')
            yy += ALT_FILA
    S.append('</svg>')
    return '\n'.join(S)


def main():
    with open('docs/ev02/ER-InvenXis.mmd', 'w', encoding='utf-8') as f:
        f.write(mermaid())
    with open('docs/ev02/ER-InvenXis.svg', 'w', encoding='utf-8') as f:
        f.write(svg())
    print('OK: docs/ev02/ER-InvenXis.mmd + docs/ev02/ER-InvenXis.svg '
          f'({len(MODELOS)} entidades, {len(relaciones())} relaciones)')


if __name__ == '__main__':
    main()
