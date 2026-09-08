"""Capturas de código por módulo para el Anexo D (EV02).

Requiere: pip install pygments pillow
Uso: python docs/ev02/generar_codigo_png.py
Sale: docs/ev02/anexos/codigo-*.png (extraídos del fuente real)
"""
import io
import os

from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import PythonLexer, TsxLexer
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SALIDA = os.path.join(RAIZ, 'docs', 'ev02', 'anexos')
FUENTE = r'C:\Windows\Fonts\consola.ttf'

CAPTURAS = [
    ('productos/api_views.py', 'class LoginRateThrottle', 42, 'python',
     'codigo-01-autenticacion.png'),
    ('productos/models.py', 'class Producto(models.Model):', 55, 'python',
     'codigo-02-productos.png'),
    ('productos/api_views.py', 'class ProveedorListCreateView(APIView):', 32, 'python',
     'codigo-03-proveedores.png'),
    ('productos/serializers.py', 'class VentaCreateSerializer(serializers.ModelSerializer):', 46,
     'python', 'codigo-04-ventas.png'),
    ('productos/fe/servicios.py', 'def crear_factura(venta', 42, 'python',
     'codigo-05-facturacion.png'),
    ('productos/api_views.py', 'def dashboard_api(request):', 26, 'python',
     'codigo-06-dashboard.png'),
    ('frontend/src/hooks/useApi.ts', 'export function useProductos', 30, 'tsx',
     'codigo-07-frontend.png'),
]


def extraer(ruta, marcador, n):
    with open(os.path.join(RAIZ, ruta), encoding='utf-8') as f:
        lineas = f.readlines()
    for i, lin in enumerate(lineas):
        if marcador in lin:
            return ''.join(lineas[i:i + n]), i + 1
    raise ValueError(f'Marcador no encontrado: {marcador} en {ruta}')


def main():
    os.makedirs(SALIDA, exist_ok=True)
    for ruta, marcador, n, lenguaje, nombre in CAPTURAS:
        texto, desde = extraer(ruta, marcador, n)
        lexer = PythonLexer() if lenguaje == 'python' else TsxLexer()
        buf = io.BytesIO()
        highlight(texto, lexer, ImageFormatter(
            font_name=FUENTE, font_size=15, line_numbers=True,
            style='default', image_pad=14, line_pad=4), outfile=buf)
        buf.seek(0)
        img = Image.open(buf)
        destino = os.path.join(SALIDA, nombre)
        img.save(destino)
        print(f'OK {nombre} ({ruta}:{desde}, {img.size[0]}x{img.size[1]})')


if __name__ == '__main__':
    main()
