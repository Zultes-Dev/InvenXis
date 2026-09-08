"""Genera el PDF de entrega EV02 GA8-220501096-AA1-EV02 (InvenXis).

Estructura espejo del ejemplo-modelo: portada, tabla de contenido con páginas,
1. Introducción, 2-6. Ítems 1-5, 7. Acta de aceptación, 8. Anexos.

Uso: python docs/ev02/generar_pdf.py
Sale: docs/ev02/EV02-InvenXis-GA8-220501096-AA1-EV02.pdf
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Preformatted,
)
from reportlab.platypus.tableofcontents import TableOfContents

VERDE = colors.HexColor('#00843D')
GRIS_OSCURO = colors.HexColor('#333333')

APRENDIZ = '[NOMBRE DEL APRENDIZ]'
FICHA = '3235904'
CIUDAD = 'Pereira, Risaralda'
INSTRUCTOR = 'Carlos Alberto Fuel Tulcán'
FECHA = '08 de septiembre de 2026'
EVIDENCIA = 'GA8-220501096-AA1-EV02'
REPO = 'https://github.com/Zultes-Dev/InvenXis'

styles = getSampleStyleSheet()
sTitle = ParagraphStyle('Titulo', parent=styles['Title'], fontSize=22,
                        textColor=VERDE, spaceAfter=4)
sH1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=15,
                     textColor=VERDE, spaceBefore=14, spaceAfter=6,
                     outlineLevel=0)
sH2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12,
                     textColor=GRIS_OSCURO, spaceBefore=10, spaceAfter=4,
                     outlineLevel=1)
sBody = ParagraphStyle('Cuerpo', parent=styles['Normal'], fontSize=10,
                       leading=14, spaceAfter=4)
sSmall = ParagraphStyle('Peq', parent=styles['Normal'], fontSize=9,
                        leading=12, spaceAfter=3)
sCell = ParagraphStyle('Celda', parent=styles['Normal'], fontSize=8.5,
                       leading=11)
sCellB = ParagraphStyle('CeldaB', parent=sCell, fontName='Helvetica-Bold')
sCode = ParagraphStyle('Cod', parent=styles['Code'], fontSize=7.5,
                       leading=10, fontName='Courier', textColor=GRIS_OSCURO)


class DocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            nivel = getattr(flowable.style, 'outlineLevel', None)
            if nivel is not None:
                self.notify('TOCEntry', (nivel, flowable.getPlainText(),
                                         self.page))


def pie(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#999999'))
    canvas.drawCentredString(A4[0] / 2, 14 * mm,
                             f'{EVIDENCIA} · Página {doc.page}')
    canvas.restoreState()


def tabla(datos, anchos, header=True):
    t = Table(datos, colWidths=anchos, repeatRows=1 if header else 0)
    estilo = [
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#999999')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]
    if header:
        estilo += [
            ('BACKGROUND', (0, 0), (-1, 0), VERDE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]
    t.setStyle(TableStyle(estilo))
    return t


def P(txt, estilo=sBody):
    return Paragraph(txt, estilo)


def codigo(texto):
    pre = Preformatted(texto, sCode)
    t = Table([[pre]], colWidths=[162 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F5')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


SNIPPET_VENTA = """# productos/serializers.py — descuento atómico de stock
with transaction.atomic():
    producto = Producto.objects.select_for_update().get(pk=...)
    if producto.cantidad < cantidad:
        raise serializers.ValidationError({'detalles': 'Stock insuficiente...'})
    DetalleVenta.objects.create(venta=venta, **detalle_data)
    Producto.objects.filter(pk=producto.pk).update(
        cantidad=F('cantidad') - cantidad)"""

SNIPPET_CUFE = """# productos/fe/cufe.py — CUFE estilo DIAN (SHA-384)
base = (f"{numero}{fecha}{nit_emisor}{doc_adquiriente}"
        f"{total}{iva}01{iva}{clave_tecnica}")
return hashlib.sha384(base.encode('utf-8')).hexdigest()  # 96 hex"""


def main():
    out = 'docs/ev02/EV02-InvenXis-GA8-220501096-AA1-EV02.pdf'
    doc = DocTemplate(out, pagesize=A4, topMargin=18 * mm, bottomMargin=20 * mm,
                      leftMargin=18 * mm, rightMargin=18 * mm,
                      title='EV02 InvenXis - Módulos Integrados', author=APRENDIZ)
    el = []

    # ---------------- PORTADA ----------------
    el.append(Spacer(1, 40))
    el.append(P('Servicio Nacional de Aprendizaje — SENA', sSmall))
    el.append(P('Centro de Comercio y Turismo — SENA Regional Quindío', sSmall))
    el.append(P('Análisis y Desarrollo de Software', sSmall))
    el.append(Spacer(1, 16))
    el.append(P(f'{EVIDENCIA} — Módulos integrados', sTitle))
    el.append(P('Proyecto InvenXis — Sistema de gestión de inventarios, '
                'proveedores, ventas y facturación electrónica',
                ParagraphStyle('Sub', parent=sBody, alignment=1)))
    el.append(Spacer(1, 12))
    for etiqueta, valor in [('Aprendiz', APRENDIZ), ('Ficha', FICHA),
                            ('Ciudad', CIUDAD), ('Instructor', INSTRUCTOR),
                            ('Fecha de entrega', f'___ de agosto de 2026'.replace(
                                '___', FECHA.split(' de ')[0]))]:
        p = P(f'<b>{etiqueta}:</b> {valor}',
              ParagraphStyle('C', parent=sBody, alignment=1))
        el.append(p)
    el.append(PageBreak())

    # ---------------- TOC ----------------
    el.append(P('Tabla de contenido', sH1))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle('TOC1', parent=styles['Normal'], fontSize=10, leading=15,
                       leftIndent=0, firstLineIndent=0),
        ParagraphStyle('TOC2', parent=styles['Normal'], fontSize=9, leading=14,
                       leftIndent=12),
    ]
    toc.dotsMinLevel = 0
    el.append(toc)
    el.append(PageBreak())

    # ---------------- 1. INTRODUCCIÓN ----------------
    el.append(P('1. Introducción', sH1))
    el.append(P('Este documento presenta la entrega de la evidencia GA8-220501096-AA1-EV02: '
                'Módulos integrados, correspondiente al proyecto InvenXis. La evidencia es de producto: '
                'no busca mostrar de nuevo el proceso de codificación, sino entregar el sistema con sus '
                'módulos ya integrados, documentados y probados.', sBody))
    el.append(P('El criterio con el que se evalúa es: “Integra los módulos del software de acuerdo con los '
                'propósitos del sistema”. InvenXis cumple ese criterio integrando ocho módulos funcionales '
                '—autenticación, productos, proveedores, pedidos, ventas, facturación electrónica, dashboard y '
                'reportes— en un mismo sistema API-first, de modo que una venta descuenta inventario, genera '
                'factura con IVA y puede emitirse electrónicamente con CUFE y UBL.', sBody))
    el.append(P('La entrega se organiza según los cinco ítems del instrumento de evaluación '
                '(IE-GA8-220501096-AA1-EV02): módulos documentados, documento técnico, ambiente, control de '
                'versiones y acta de pruebas y aceptación, más acta de aceptación y anexos.', sBody))

    # ---------------- 2. ÍTEM 1 ----------------
    el.append(P('2. Ítem 1 — Módulos codificados y documentados', sH1))
    el.append(P('InvenXis está construido como backend Django (app <font face="Courier" size="8">productos</font>) '
                'más SPA React, con ocho módulos funcionales:', sBody))
    modulos = [
        ('Autenticación', 'Registrar/iniciar sesión y permisos', 'usuario + clave',
         'JWT access/refresh + sesión', 'Ventas, Facturación, Admin'),
        ('Productos', 'Registrar el inventario', 'nombre, precio, stock, proveedor',
         'Producto disponible', 'Ventas, Pedidos'),
        ('Proveedores', 'Registrar aliados y su historial', 'razón social, NIT, contacto',
         'Proveedor con pedidos', 'Productos, Pedidos'),
        ('Pedidos', 'Crear y gestionar pedidos que integran módulos',
         'proveedor, productos, cantidades', 'Pedido con total', 'Proveedores, Productos'),
        ('Ventas', 'Punto de venta con stock atómico', 'cliente, líneas (producto × cantidad)',
         'Venta + descuento exacto', 'Productos, Facturación'),
        ('Facturación FE', 'Facturar, emitir DIAN, anular con NC', 'venta + NIT cliente',
         'Factura, CUFE, UBL, PDF', 'Ventas'),
        ('Dashboard', 'KPIs y actividad reciente', '—', 'Panel con indicadores', 'Todos'),
        ('Reportes', 'Analítica y exportaciones', 'filtros + formato', 'Excel/PDF, rankings', 'Ventas, Productos'),
    ]
    filas = [[P('<b>Módulo</b>', sCellB), P('<b>Responsabilidad</b>', sCellB),
              P('<b>Entrada</b>', sCellB), P('<b>Salida</b>', sCellB),
              P('<b>Se conecta con</b>', sCellB)]]
    for m in modulos:
        filas.append([P(x, sCell) for x in m])
    el.append(tabla(filas, [24 * mm, 38 * mm, 36 * mm, 32 * mm, 32 * mm]))
    el.append(P('<b>Punto de integración.</b> La venta es el módulo que integra a los demás: una venta '
                'referencia productos (FK), descuenta stock, y habilita la factura electrónica:', sBody))
    el.append(codigo(SNIPPET_VENTA))
    el.append(P('<b>Integración validada por regla de negocio.</b> Sin stock suficiente la venta se rechaza '
                'con 400 y revierte todo (rollback atómico):', sBody))
    el.append(codigo(SNIPPET_CUFE))

    # ---------------- 3. ÍTEM 2 ----------------
    el.append(P('3. Ítem 2 — Documento técnico del sistema', sH1))
    el.append(P('<b>Descripción general.</b> InvenXis permite gestionar inventario, proveedores y pedidos, '
                'registrar ventas con descuento automático de stock y emitir facturas electrónicas (CUFE + UBL 2.1, '
                'IVA 19%, notas crédito), con dashboard, reportes y panel admin.', sBody))
    el.append(P('<b>Arquitectura.</b> Patrón API-first sobre MVT de Django: Petición → '
                '<font face="Courier" size="8">config/urls.py → productos/urls_api.py → APIView/serializers → '
                'modelo (ORM) → JSON → TanStack Query → React → respuesta</font>. Presentación desacoplada en SPA; '
                'Django conserva API, admin y documentación.', sBody))
    el.append(P('<b>Modelo de datos (relaciones):</b>', sBody))
    for r in ['Un proveedor tiene muchos productos y pedidos (1 a N).',
              'Un pedido tiene muchos detalles; un detalle referencia un producto (1 a N).',
              'Una venta tiene muchos detalles de venta (1 a N).',
              'Una venta tiene una factura (1 a 1); una factura tiene muchas notas crédito (1 a N).',
              'Usuarios y grupos (RBAC) referenciados como creadores (N a 1).',
              '(Anexo A: diagrama entidad-relación.)']:
        el.append(P(f'• {r}', sBody))
    el.append(P('<b>Tecnologías utilizadas (verificadas):</b>', sBody))
    el.append(tabla([
        [P('<b>Componente</b>', sCellB), P('<b>Tecnología</b>', sCellB)],
        [P('Lenguaje', sCell), P('Python 3.13.7', sCell)],
        [P('Framework', sCell), P('Django 6.0.7 (API-first sobre MVT)', sCell)],
        [P('API', sCell), P('DRF 3.17.1 + SimpleJWT + drf-spectacular', sCell)],
        [P('Base de datos', sCell), P('SQLite (dev) / PostgreSQL 16 (prod)', sCell)],
        [P('Frontend', sCell), P('React 19.2.8 + Vite 8.1.5 + TypeScript 6.0.3 + Tailwind v4', sCell)],
        [P('Datos/tiempo real', sCell), P('Axios + TanStack Query 5', sCell)],
        [P('Calidad', sCell), P('pytest + Playwright + oxlint + tsc', sCell)],
        [P('Runtime/CI', sCell), P('Node 24.16.0 / npm 11.13.0 / GitHub Actions', sCell)],
    ], [45 * mm, 117 * mm]))
    el.append(P('<b>Hallazgo documentado (pendiente real).</b> La emisión productiva ante la DIAN exige '
                'certificado digital, firma del UBL y proveedor tecnológico contratado; el sistema incluye '
                'proveedor mock intercambiable. Se documenta como limitación conocida (TC-12), no como error '
                'oculto.', sBody))

    # ---------------- 4. ÍTEM 3 ----------------
    el.append(P('4. Ítem 3 — Ambiente de desarrollo y pruebas', sH1))
    el.append(P('<b>Herramientas y versiones (verificadas en máquina):</b>', sBody))
    el.append(tabla([
        [P('<b>Herramienta</b>', sCellB), P('<b>Versión</b>', sCellB), P('<b>Rol</b>', sCellB)],
        [P('Python', sCell), P('3.13.7', sCell), P('Lenguaje backend', sCell)],
        [P('Django / DRF', sCell), P('6.0.7 / 3.17.1', sCell), P('Framework y API', sCell)],
        [P('Node.js / npm', sCell), P('24.16.0 / 11.13.0', sCell), P('Runtime frontend', sCell)],
        [P('React / Vite / TS', sCell), P('19.2.8 / 8.1.5 / 6.0.3', sCell), P('SPA', sCell)],
        [P('SQLite / PostgreSQL', sCell), P('dev / 16 prod', sCell), P('Base de datos', sCell)],
        [P('Git + GitHub', sCell), P('—', sCell), P('Versiones', sCell)],
        [P('Chromium (Playwright)', sCell), P('—', sCell), P('Pruebas e2e', sCell)],
        [P('Windows + PowerShell', sCell), P('5.1', sCell), P('SO desarrollo', sCell)],
    ], [50 * mm, 45 * mm, 67 * mm]))
    el.append(P('<b>Cómo levantar el ambiente.</b>', sBody))
    el.append(codigo('python -m venv venv\nvenv\\Scripts\\activate  # Windows\n'
                     'pip install -r requirements.txt\npython manage.py migrate\n'
                     'python manage.py seed_data\npython manage.py runserver  # :8000\n'
                     'cd frontend && npm install && npm run dev  # :3000'))
    el.append(P('<b>Ambiente de pruebas.</b> 45 pruebas pytest (unitarias, API, seguridad, facturación), '
                '2 e2e Playwright contra Django real, type-check, build y lint como compuertas en CI. '
                'Datos demo deterministas con <font face="Courier" size="8">seed_data --force</font>.', sBody))

    # ---------------- 5. ÍTEM 4 ----------------
    el.append(P('5. Ítem 4 — Código por control de versiones', sH1))
    el.append(P('El código se entrega versionado con Git, no como archivo suelto.', sBody))
    el.append(P(f'<b>Repositorio remoto:</b> {REPO}', sBody))
    el.append(P('Accesible al instructor; el enlace se entrega como parte de la evidencia. Rama principal '
                '<font face="Courier" size="8">main</font>, 18 commits convencionales (feat/fix/chore/docs/ci):',
                sBody))
    el.append(codigo('ee2616f feat: modulo de ventas completo con facturacion y FE DIAN-ready\n'
                     '6ca0e78 fix: login conserva next al admin + RBAC demo\n'
                     '95e020e feat: acceso al panel Django admin desde el sidebar\n'
                     '39e5ced feat: hardening senior x10 (health, throttle, factura uuid, a11y)'))
    el.append(P('<b>Archivo .gitignore</b> (no sube dependencias ni temporales): '
                '<font face="Courier" size="8">venv/, __pycache__/, *.sqlite3, .env, node_modules/, '
                'frontend/dist/, test-results/</font>. CI con jobs backend, frontend y e2e.', sBody))

    # ---------------- 6. ÍTEM 5 ----------------
    el.append(P('6. Ítem 5 — Acta de pruebas y aceptación', sH1))
    el.append(P('Este ítem solo aparece en el instrumento de evaluación, no en la guía. '
                'Se incluye explícito para no omitirlo.', sBody))
    el.append(P('<b>Plan de pruebas (manual — ejecutado sobre el sistema real):</b>', sBody))
    casos = [
        ('TC-01', 'Inicio de sesión válido', 'admin/admin', 'Acceso y panel principal',
         'Acceso y panel (API + e2e)', 'Cumple'),
        ('TC-02', 'Crear producto', 'Datos válidos', 'Registro creado', 'Creado vía API y UI', 'Cumple'),
        ('TC-03', 'Listar/buscar/paginar', 'Varios registros', 'Datos paginados', 'Filtros y páginas OK', 'Cumple'),
        ('TC-04', 'Editar producto', 'Cambio de precio', 'Dato actualizado', 'Actualizado', 'Cumple'),
        ('TC-05', 'Eliminar producto', 'Confirmar', 'Registro eliminado', 'Eliminado', 'Cumple'),
        ('TC-06', 'Registrar venta', '2 uds con stock', 'Venta + descuento', 'Descuento atómico', 'Cumple'),
        ('TC-07', 'Venta sin stock', 'Cantidad > stock', 'Rechazo 400', '400 + rollback', 'Cumple'),
        ('TC-08', 'Facturar (IVA 19%)', 'Venta completada', 'Totales correctos', 'Subtotal/IVA/total OK', 'Cumple'),
        ('TC-09', 'Emitir FE', 'Factura borrador', 'CUFE + UBL válido', 'Aceptada mock', 'Cumple'),
        ('TC-10', 'Anular + RBAC', 'Motivo + admin', 'NC + stock + 403 operador', 'NC + 403 OK', 'Cumple'),
        ('TC-11', 'Logout + throttle', 'Refresh / 25 intentos', 'Blacklist + 429', 'Ambos OK', 'Cumple'),
        ('TC-12', 'DIAN en producción', 'Emisión real', 'Validación DIAN', 'Proveedor mock; falta certificado', 'No cumple'),
    ]
    filas = [[P('<b>ID</b>', sCellB), P('<b>Caso</b>', sCellB), P('<b>Entrada</b>', sCellB),
              P('<b>Esperado</b>', sCellB), P('<b>Obtenido</b>', sCellB), P('<b>Estado</b>', sCellB)]]
    for tc, caso, ent, esp, obt, est in casos:
        color = VERDE if est == 'Cumple' else colors.red
        filas.append([P(tc, sCell), P(caso, sCell), P(ent, sCell), P(esp, sCell), P(obt, sCell),
                      P(f'<font color="{color.hexval()}"><b>{est}</b></font>', sCell)])
    el.append(tabla(filas, [13 * mm, 30 * mm, 27 * mm, 32 * mm, 34 * mm, 26 * mm]))
    el.append(P('<b>Hallazgo (TC-12).</b> La emisión productiva exige certificado digital, firma del UBL y '
                'proveedor tecnológico; el sistema trae mock intercambiable '
                '(<font face="Courier" size="8">productos/fe/proveedores.py</font>). Funcionalidad pendiente, '
                'prioridad media: no bloquea el uso en demostración.', sBody))

    # ---------------- 7. ACTA ----------------
    el.append(P('7. Acta de aceptación (formato de propuesta)', sH1))
    el.append(P('ACTA DE ACEPTACIÓN DE PRUEBAS', ParagraphStyle(
        'Bar', parent=sBody, backColor=VERDE, textColor=colors.white,
        fontName='Helvetica-Bold', alignment=1, borderPadding=6)))
    el.append(tabla([
        [P('<b>Proyecto</b>', sCellB), P('InvenXis — Sistema de Gestión de Inventarios', sCell)],
        [P('<b>Evidencia</b>', sCellB), P(f'{EVIDENCIA} — Módulos integrados', sCell)],
        [P('<b>Aprendiz</b>', sCellB), P(APRENDIZ, sCell)],
        [P('<b>Ficha</b>', sCellB), P(FICHA, sCell)],
        [P('<b>Instructor</b>', sCellB), P(INSTRUCTOR, sCell)],
        [P('<b>Fecha</b>', sCellB), P(FECHA, sCell)],
    ], [40 * mm, 122 * mm], header=False))
    el.append(P('<b>Resultado de las pruebas.</b> Se ejecutaron 12 casos: 11 cumplen y 1 queda pendiente '
                'documentado (TC-12).', sBody))
    el.append(P('<b>Declaración de aceptación.</b> Se deja constancia de que el sistema InvenXis fue probado '
                'según el plan registrado. Se acepta el producto con las salvedades documentadas: TC-12 pendiente; '
                'la configuración aún no es apta para producción real ante la DIAN.', sBody))
    el.append(Spacer(1, 6))
    el.append(tabla([
        [P('<b>Elabora y entrega (Aprendiz)</b>', sCellB), P('<b>Recibe (Instructor)</b>', sCellB)],
        [P(f'{APRENDIZ} — Ficha {FICHA}<br/>Firma: ___________________________', sCell),
         P(f'{INSTRUCTOR}<br/>Firma: ___________________________', sCell)],
    ], [81 * mm, 81 * mm]))

    # ---------------- 8. ANEXOS ----------------
    el.append(P('8. Anexos', sH1))
    for a in ['<b>Anexo A:</b> diagrama entidad-relación — <font face="Courier" size="8">docs/ev02/ER-InvenXis.svg '
              '</font>(11 entidades, 13 relaciones; Mermaid en <font face="Courier" size="8">ER-InvenXis.mmd</font>).',
              '<b>Anexo B:</b> capturas por módulo — <font face="Courier" size="8">docs/ev02/anexos/'
              '01-login.png, 02-dashboard.png, 03-productos.png, 04-proveedores.png, 05-ventas.png, '
              '06-facturacion.png, 07-reportes.png</font> (tomadas con Playwright contra el sistema real, una por '
              'módulo).',
              '<b>Anexo C:</b> repositorio remoto con historial de commits — ' + REPO + '.',
              '<b>Anexo D:</b> código por módulo — <font face="Courier" size="8">docs/ev02/anexos/codigo-01-'
              'autenticacion.png … codigo-07-frontend.png</font> (extractos reales con resaltado, generados con '
              '<font face="Courier" size="8">docs/ev02/generar_codigo_png.py</font>).']:
        el.append(P(f'• {a}', sBody))

    doc.multiBuild(el, onFirstPage=pie, onLaterPages=pie)
    print(f'OK: {out}')


if __name__ == '__main__':
    main()
