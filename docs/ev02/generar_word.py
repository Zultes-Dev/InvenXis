"""Genera el Word de entrega EV02 (espejo del PDF v2: intro, TOC, snippets, anexos).

Requiere: pip install python-docx
Uso: python docs/ev02/generar_word.py
Sale: docs/ev02/EV02-InvenXis-GA8-220501096-AA1-EV02.docx
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

VERDE = RGBColor(0x00, 0x84, 0x3D)
APRENDIZ = '[NOMBRE DEL APRENDIZ]'
FICHA = '3235904'
CIUDAD = 'Pereira, Risaralda'
INSTRUCTOR = 'Carlos Alberto Fuel Tulcán'
FECHA = '08 de septiembre de 2026'
EVIDENCIA = 'GA8-220501096-AA1-EV02'
REPO = 'https://github.com/Zultes-Dev/InvenXis'


def titulo(doc, texto, nivel=1):
    h = doc.add_heading(texto, level=nivel)
    for r in h.runs:
        r.font.color.rgb = VERDE
    return h


def tabla(doc, filas, anchos=None):
    t = doc.add_table(rows=len(filas), cols=len(filas[0]))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    for i, fila in enumerate(filas):
        for j, val in enumerate(fila):
            celda = t.cell(i, j)
            celda.text = ''
            p = celda.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9)
            if i == 0:
                r.bold = True
    if anchos:
        for j, a in enumerate(anchos):
            for i in range(len(filas)):
                t.cell(i, j).width = Cm(a)
    doc.add_paragraph('')
    return t


def codigo(doc, texto):
    for linea in texto.split('\n'):
        p = doc.add_paragraph()
        r = p.add_run(linea if linea else ' ')
        r.font.name = 'Courier New'
        r.font.size = Pt(8)
    doc.add_paragraph('')


def campo(doc, parrafo, instruccion):
    r = parrafo.add_run()
    f1 = OxmlElement('w:fldChar')
    f1.set(qn('w:fldCharType'), 'begin')
    r._r.append(f1)
    r2 = parrafo.add_run()
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = instruccion
    r2._r.append(instr)
    r3 = parrafo.add_run()
    f2 = OxmlElement('w:fldChar')
    f2.set(qn('w:fldCharType'), 'end')
    r3._r.append(f2)


def main():
    doc = Document()
    for s in doc.sections:
        s.left_margin = Cm(2)
        s.right_margin = Cm(2)
        fp = s.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fp.add_run(f'{EVIDENCIA} · Página ').font.size = Pt(8)
        campo(doc, fp, 'PAGE')

    # PORTADA
    p = doc.add_paragraph()
    p.add_run('SERVICIO NACIONAL DE APRENDIZAJE — SENA\nCentro de Comercio y Turismo — '
              'SENA Regional Quindío\nAnálisis y Desarrollo de Software').font.size = Pt(10)
    t = doc.add_paragraph()
    r = t.add_run(f'{EVIDENCIA} — Módulos integrados')
    r.font.size = Pt(24)
    r.font.color.rgb = VERDE
    r.bold = True
    doc.add_paragraph('Proyecto InvenXis — Sistema de gestión de inventarios, proveedores, '
                      'ventas y facturación electrónica')
    for etiqueta, valor in [('Aprendiz', APRENDIZ), ('Ficha', FICHA), ('Ciudad', CIUDAD),
                            ('Instructor', INSTRUCTOR),
                            ('Fecha de entrega', FECHA.split(' de ')[0] + ' de agosto de 2026')]:
        pa = doc.add_paragraph()
        pa.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = pa.add_run(f'{etiqueta}: {valor}')
        run.bold = True
    doc.add_page_break()

    # TOC (Word la actualiza al abrir: botón derecho > Actualizar campo)
    titulo(doc, 'Tabla de contenido')
    pt = doc.add_paragraph()
    campo(doc, pt, 'TOC \\o "1-1" \\h \\z \\u')
    doc.add_paragraph('Nota: clic derecho sobre el índice → Actualizar campo para ver los números de página.',
                      ).runs[0].font.size = Pt(8)
    doc.add_page_break()

    # 1. INTRO
    titulo(doc, '1. Introducción')
    doc.add_paragraph('Este documento presenta la entrega de la evidencia GA8-220501096-AA1-EV02: Módulos '
                      'integrados, correspondiente al proyecto InvenXis. La evidencia es de producto: no busca '
                      'mostrar de nuevo el proceso de codificación, sino entregar el sistema con sus módulos ya '
                      'integrados, documentados y probados.')
    doc.add_paragraph('El criterio con el que se evalúa es: “Integra los módulos del software de acuerdo con los '
                      'propósitos del sistema”. InvenXis lo cumple integrando ocho módulos funcionales en un mismo '
                      'sistema API-first, de modo que una venta descuenta inventario, genera factura con IVA y '
                      'puede emitirse electrónicamente.')
    doc.add_paragraph('La entrega se organiza según los cinco ítems del instrumento de evaluación '
                      '(IE-GA8-220501096-AA1-EV02), más acta de aceptación y anexos.')

    # 2. ÍTEM 1
    titulo(doc, '2. Ítem 1 — Módulos codificados y documentados')
    doc.add_paragraph('Backend Django (app productos) más SPA React, con ocho módulos funcionales:')
    tabla(doc, [
        ['Módulo', 'Responsabilidad', 'Entrada', 'Salida', 'Se conecta con'],
        ['Autenticación', 'Sesión y permisos', 'usuario + clave', 'JWT + sesión', 'Ventas, Facturación, Admin'],
        ['Productos', 'Inventario', 'nombre, precio, stock', 'Producto disponible', 'Ventas, Pedidos'],
        ['Proveedores', 'Aliados e historial', 'razón social, NIT', 'Proveedor con pedidos', 'Productos, Pedidos'],
        ['Pedidos', 'Pedidos que integran', 'proveedor, productos', 'Pedido con total', 'Proveedores, Productos'],
        ['Ventas', 'Punto de venta atómico', 'cliente, líneas', 'Venta + descuento', 'Productos, Facturación'],
        ['Facturación FE', 'Facturar/emitir/anular', 'venta + NIT', 'Factura, CUFE, UBL, PDF', 'Ventas'],
        ['Dashboard', 'KPIs y recientes', '—', 'Panel con indicadores', 'Todos'],
        ['Reportes', 'Analítica y exports', 'filtros + formato', 'Excel/PDF', 'Ventas, Productos'],
    ], [2.5, 3.5, 3, 3, 3])
    doc.add_paragraph('Punto de integración. La venta integra a los demás (descuento atómico de stock):',
                      ).runs[0].bold = True
    codigo(doc, '# productos/serializers.py\nwith transaction.atomic():\n'
                '    producto = Producto.objects.select_for_update().get(pk=...)\n'
                '    if producto.cantidad < cantidad:\n'
                "        raise serializers.ValidationError({'detalles': 'Stock insuficiente...'})")
    doc.add_paragraph('Integración validada por regla de negocio (CUFE estilo DIAN):').runs[0].bold = True
    codigo(doc, '# productos/fe/cufe.py\nbase = (f"{numero}{fecha}{nit_emisor}{doc_adquiriente}"\n'
                '        f"{total}{iva}01{iva}{clave_tecnica}")\n'
                "return hashlib.sha384(base.encode('utf-8')).hexdigest()")

    # 3. ÍTEM 2
    titulo(doc, '3. Ítem 2 — Documento técnico del sistema')
    doc.add_paragraph('Descripción general. InvenXis gestiona inventario, proveedores, pedidos, ventas con '
                      'descuento automático y facturación electrónica (CUFE + UBL 2.1, IVA 19%, notas crédito).')
    doc.add_paragraph('Arquitectura. API-first sobre MVT: Petición → config/urls.py → productos/urls_api.py → '
                      'APIView/serializers → ORM → JSON → TanStack Query → React.')
    doc.add_paragraph('Modelo de datos. Proveedor 1—N Producto/Pedido; Pedido/Venta 1—N Detalles; Venta 1—1 '
                      'Factura 1—N NotaCredito; User/Group para RBAC. (Anexo A: ER.)')
    titulo(doc, 'Tecnologías utilizadas (verificadas)', nivel=2)
    tabla(doc, [
        ['Componente', 'Tecnología'],
        ['Lenguaje', 'Python 3.13.7'],
        ['Framework', 'Django 6.0.7 (API-first sobre MVT)'],
        ['API', 'DRF 3.17.1 + SimpleJWT + drf-spectacular'],
        ['Base de datos', 'SQLite (dev) / PostgreSQL 16 (prod)'],
        ['Frontend', 'React 19.2.8 + Vite 8.1.5 + TypeScript 6.0.3 + Tailwind v4'],
        ['Datos', 'Axios + TanStack Query 5'],
        ['Calidad', 'pytest + Playwright + oxlint + tsc'],
        ['Runtime/CI', 'Node 24.16.0 / npm 11.13.0 / GitHub Actions'],
    ], [5, 11])
    doc.add_paragraph('Hallazgo documentado (pendiente real). La emisión productiva ante la DIAN exige '
                      'certificado digital y proveedor tecnológico; el sistema incluye mock intercambiable '
                      '(TC-12).')

    # 4. ÍTEM 3
    titulo(doc, '4. Ítem 3 — Ambiente de desarrollo y pruebas')
    tabla(doc, [
        ['Herramienta', 'Versión', 'Rol'],
        ['Python', '3.13.7', 'Lenguaje backend'],
        ['Django / DRF', '6.0.7 / 3.17.1', 'Framework y API'],
        ['Node.js / npm', '24.16.0 / 11.13.0', 'Runtime frontend'],
        ['React / Vite / TS', '19.2.8 / 8.1.5 / 6.0.3', 'SPA'],
        ['SQLite / PostgreSQL', 'dev / 16 prod', 'Base de datos'],
        ['Git + GitHub', '—', 'Versiones'],
        ['Chromium (Playwright)', '—', 'Pruebas e2e'],
        ['Windows + PowerShell', '5.1', 'SO desarrollo'],
    ], [4.5, 4, 7.5])
    doc.add_paragraph('Cómo levantar: python -m venv venv; pip install -r requirements.txt; copiar .env.example '
                      'a .env; python manage.py migrate && python manage.py seed_data; python manage.py runserver '
                      '(:8000); cd frontend && npm install && npm run dev (:3000). Verificar con pytest -q y '
                      'npm run build. Demo: admin/admin, operador/operador123.')

    # 5. ÍTEM 4
    titulo(doc, '5. Ítem 4 — Código por control de versiones')
    doc.add_paragraph(f'Repositorio remoto (público): {REPO}, rama main, 18 commits convencionales:')
    for c in ['ee2616f feat: modulo de ventas completo con facturacion y FE DIAN-ready',
              '6ca0e78 fix: login conserva next al admin + RBAC demo',
              '95e020e feat: acceso al panel Django admin desde el sidebar',
              '39e5ced feat: hardening senior x10 (health, throttle, factura uuid, a11y)',
              'cd0dabd feat: seed_data --force purga demo y resiembra determinista',
              '390eb1e feat: TanStack Query en SPA, API en /api, e2e Playwright, retiro SSR',
              '9d21c8c feat: P0+P1 hardening (venta atómica, logout blacklist, docker)',
              'd12bb07 chore: rename InvenSoft Pro to InvenXis']:
        doc.add_paragraph(c, style='List Bullet')
    doc.add_paragraph('.gitignore: venv/, __pycache__/, *.sqlite3, .env, node_modules/, frontend/dist/, '
                      'test-results/. CI: backend, frontend y e2e.')

    # 6. ÍTEM 5
    titulo(doc, '6. Ítem 5 — Acta de pruebas y aceptación')
    doc.add_paragraph('Este ítem solo aparece en el instrumento de evaluación. Plan ejecutado sobre el sistema real:')
    casos = [
        ('TC-01', 'Inicio de sesión válido', 'Acceso y panel', 'Acceso y panel (API + e2e)', 'Cumple'),
        ('TC-02', 'Crear producto', 'Registro creado', 'Creado vía API y UI', 'Cumple'),
        ('TC-03', 'Listar/buscar/paginar', 'Datos paginados', 'Filtros y páginas OK', 'Cumple'),
        ('TC-04', 'Editar producto', 'Dato actualizado', 'Actualizado', 'Cumple'),
        ('TC-05', 'Eliminar producto', 'Registro eliminado', 'Eliminado', 'Cumple'),
        ('TC-06', 'Registrar venta', 'Venta + descuento', 'Descuento atómico', 'Cumple'),
        ('TC-07', 'Venta sin stock', 'Rechazo 400', '400 + rollback', 'Cumple'),
        ('TC-08', 'Facturar (IVA 19%)', 'Totales correctos', 'Subtotal/IVA/total OK', 'Cumple'),
        ('TC-09', 'Emitir FE', 'CUFE + UBL válido', 'Aceptada mock', 'Cumple'),
        ('TC-10', 'Anular + RBAC', 'NC + 403 operador', 'NC + stock + 403 OK', 'Cumple'),
        ('TC-11', 'Logout + throttle', 'Blacklist + 429', 'Ambos OK', 'Cumple'),
        ('TC-12', 'DIAN en producción', 'Emisión real', 'Falta certificado', 'No cumple'),
    ]
    tabla(doc, [['ID', 'Caso', 'Esperado', 'Obtenido', 'Estado']] + casos, [1.5, 3.5, 3.5, 4.5, 3])
    doc.add_paragraph('Ejecución: 45 pytest en verde sin warnings; tsc + build OK; oxlint 0 errores; '
                      'Playwright 2/2.')
    doc.add_paragraph('Hallazgo (TC-12). Emisión productiva exige certificado, firma UBL y proveedor; mock '
                      'intercambiable en productos/fe/proveedores.py. Prioridad media.')

    # 7. ACTA
    titulo(doc, '7. Acta de aceptación (formato de propuesta)')
    tabla(doc, [['Campo', 'Valor'],
                ['Proyecto', 'InvenXis — Sistema de Gestión de Inventarios (v1.0)'],
                ['Evidencia', EVIDENCIA + ' — Módulos integrados'],
                ['Aprendiz', APRENDIZ],
                ['Ficha', FICHA],
                ['Instructor', INSTRUCTOR],
                ['Fecha', FECHA]], [4, 12])
    doc.add_paragraph('Resultado: 12 casos ejecutados, 11 cumplen y 1 pendiente documentado (TC-12).')
    doc.add_paragraph('Declaración: se acepta el producto con las salvedades documentadas; la configuración '
                      'aún no es apta para producción real ante la DIAN.')
    tabla(doc, [['Elabora y entrega (Aprendiz)', 'Recibe (Instructor)'],
                [f'{APRENDIZ} — Ficha {FICHA}\nFirma: ___________________________',
                 f'{INSTRUCTOR}\nFirma: ___________________________']], [8, 8])

    # 8. ANEXOS
    titulo(doc, '8. Anexos')
    doc.add_paragraph('Anexo A: diagrama entidad-relación — docs/ev02/ER-InvenXis.svg (11 entidades, '
                      '13 relaciones; Mermaid en ER-InvenXis.mmd).', style='List Bullet')
    doc.add_paragraph('Anexo B: capturas por módulo — docs/ev02/anexos/01-login.png, '
                      '02-dashboard.png, 03-productos.png, 04-proveedores.png, 05-ventas.png, '
                      '06-facturacion.png, 07-reportes.png (Playwright contra el sistema real, una por módulo).',
                      style='List Bullet')
    doc.add_paragraph(f'Anexo C: repositorio remoto con historial — {REPO}.', style='List Bullet')

    out = 'docs/ev02/EV02-InvenXis-GA8-220501096-AA1-EV02.docx'
    doc.save(out)
    print(f'OK: {out}')


if __name__ == '__main__':
    main()
