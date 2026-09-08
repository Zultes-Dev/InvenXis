"""Genera el PDF de entrega EV02 GA8-220501096-AA1-EV02 (InvenXis).

Uso: python docs/ev02/generar_pdf.py
Sale: docs/ev02/EV02-InvenXis-GA8-220501096-AA1-EV02.pdf
Datos verificados el 2026-09-08 contra el repositorio real.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether,
)

VERDE = colors.HexColor('#00843D')
VERDE_CLARO = colors.HexColor('#E6F4EA')
GRIS_OSCURO = colors.HexColor('#333333')
AMBAR = colors.HexColor('#E8A230')

APRENDIZ = '[NOMBRE DEL APRENDIZ]'
FICHA = '3235904'
INSTRUCTOR = 'Carlos Alberto Fuel Tulcán'
FECHA = '08 de septiembre de 2026'
EVIDENCIA = 'GA8-220501096-AA1-EV02'
REPO = 'https://github.com/Zultes-Dev/InvenXis'

styles = getSampleStyleSheet()
sTitle = ParagraphStyle('Titulo', parent=styles['Title'], fontSize=22,
                        textColor=VERDE, spaceAfter=4)
sH1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=15,
                     textColor=VERDE, spaceBefore=14, spaceAfter=6,
                     borderPadding=(0, 0, 4, 0))
sH2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12,
                     textColor=GRIS_OSCURO, spaceBefore=10, spaceAfter=4)
sBody = ParagraphStyle('Cuerpo', parent=styles['Normal'], fontSize=10,
                       leading=14, spaceAfter=4)
sSmall = ParagraphStyle('Peq', parent=styles['Normal'], fontSize=9,
                        leading=12, spaceAfter=3)
sCell = ParagraphStyle('Celda', parent=styles['Normal'], fontSize=8.5,
                       leading=11)
sCellB = ParagraphStyle('CeldaB', parent=sCell, fontName='Helvetica-Bold')
sCode = ParagraphStyle('Cod', parent=styles['Code'], fontSize=8,
                       leading=11, fontName='Courier')


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


def main():
    out = 'docs/ev02/EV02-InvenXis-GA8-220501096-AA1-EV02.pdf'
    doc = SimpleDocTemplate(out, pagesize=A4, topMargin=18 * mm,
                            bottomMargin=18 * mm, leftMargin=18 * mm,
                            rightMargin=18 * mm,
                            title='EV02 InvenXis - Módulos Integrados',
                            author=APRENDIZ)
    el = []

    # ---------------- PORTADA ----------------
    el.append(Spacer(1, 30))
    el.append(P('SERVICIO NACIONAL DE APRENDIZAJE — SENA', sSmall))
    el.append(P('Centro de Comercio y Turismo · Regional Quindío · ADSO', sSmall))
    el.append(Spacer(1, 12))
    el.append(P('InvenXis — Sistema de Gestión de Inventarios', sTitle))
    el.append(P('Evidencia GA8-220501096-AA1-EV02: Módulos Integrados', sH2))
    el.append(Spacer(1, 8))
    el.append(tabla([
        [P('<b>Programa</b>', sCellB), P('Análisis y Desarrollo de Software (ADSO)', sCell)],
        [P('<b>Aprendiz</b>', sCellB), P(APRENDIZ, sCell)],
        [P('<b>Ficha</b>', sCellB), P(FICHA, sCell)],
        [P('<b>Instructor técnico</b>', sCellB), P(INSTRUCTOR, sCell)],
        [P('<b>Fecha de entrega</b>', sCellB), P(FECHA, sCell)],
        [P('<b>Repositorio</b>', sCellB), P(REPO, sCell)],
        [P('<b>Versión</b>', sCellB), P('1.0', sCell)],
    ], [42 * mm, 120 * mm]))
    el.append(Spacer(1, 8))
    el.append(P('Documento único de entrega: reúne los 5 ítems del instrumento '
                'de evaluación (módulos documentados, documento técnico, ambiente, '
                'control de versiones, acta de pruebas y aceptación) más manual de '
                'usuario y anexos. Se entrega en Zajuna junto con el enlace al repositorio.',
                sBody))
    el.append(PageBreak())

    # ---------------- CONTENIDO ----------------
    el.append(P('Tabla de contenido', sH1))
    for i, t in [
        ('1', 'Módulos codificados y documentados (ítem 1)'),
        ('2', 'Documento técnico del sistema (ítem 2)'),
        ('3', 'Ambiente de desarrollo y pruebas (ítem 3)'),
        ('4', 'Código por control de versiones (ítem 4)'),
        ('5', 'Acta de pruebas y aceptación (ítem 5)'),
        ('A', 'Anexos'),
    ]:
        el.append(P(f'<b>{i}.</b> {t}', sBody))

    # ---------------- ÍTEM 1 ----------------
    el.append(P('1. Módulos codificados y documentados (ítem 1)', sH1))
    el.append(P('Cada módulo indica entradas, salidas y archivos donde vive el código. '
                'API base: <font face="Courier" size="8">/api/</font> con envelope '
                '<font face="Courier" size="8">{"success": true, "data": ...}</font> '
                'y JWT Bearer.', sBody))
    modulos = [
        ('Autenticación y autorización',
         'POST /api/auth/login/, /api/auth/refresh/, /api/auth/logout/, GET /api/auth/me/',
         'JWT access+refresh con rotación y blacklist; throttle de login 20/min; RBAC por grupos (Administradores / Operadores).',
         'productos/api_views.py (api_login, api_logout), config/settings.py, frontend/src/contexts/AuthContext.tsx'),
        ('Productos e inventario',
         'CRUD /api/productos/ + filtros (categoría, estado, estado_stock, q) y paginación',
         'Lee/escribe Producto (nombre, categoría, precio, cantidad, stock_min, proveedor).',
         'productos/models.py, api_views.py:ProductoListCreateView, frontend/src/pages/ProductosPage.tsx'),
        ('Proveedores y pedidos',
         'CRUD /api/proveedores/, /api/proveedores/{id}/pedidos/, /api/pedidos/{id}/',
         'Proveedor con conteos; pedidos con estados pendiente/en_proceso/completado/cancelado.',
         'productos/models.py, frontend/src/pages/ProveedoresPage.tsx'),
        ('Ventas (punto de venta)',
         'GET/POST /api/ventas/ con filtros desde/hasta',
         'Crea la venta y descuenta stock en una transacción atómica (select_for_update + F()); sin stock retorna 400 y revierte todo.',
         'productos/serializers.py:VentaCreateSerializer, frontend/src/pages/VentasPage.tsx'),
        ('Facturación y factura electrónica',
         'POST /api/ventas/{id}/facturar/, /api/facturas/, /emitir/, /anular/, /pdf/, /ubl/, /api/notas-credito/',
         'Consecutivo atómico FAC/NC, IVA 19%, CUFE SHA-384, UBL 2.1, proveedor DIAN intercambiable (mock incluido); anular crea nota crédito, cancela la venta y devuelve stock.',
         'productos/fe/ (cufe, ubl, proveedores, servicios), productos/models.py:Factura, frontend/src/pages/FacturasPage.tsx'),
        ('Dashboard y reportes',
         'GET /api/dashboard/ (caché 60 s), /api/reportes/inventario|mas-vendidos|ventas/, exportar excel|pdf',
         'KPIs, recientes, ranking, exportaciones Excel/PDF.',
         'productos/api_views.py, frontend/src/pages/DashboardPage.tsx, ReportesPage.tsx'),
        ('Transversales',
         'GET /api/health/, /api/docs/ (Swagger), /api/redoc/, /admin/',
         'Health-check, documentación OpenAPI, admin Django con 9 modelos, throttling global, caché Redis/local.',
         'config/urls.py, productos/urls_api.py, productos/admin.py'),
    ]
    for nombre, entradas, salidas, archivos in modulos:
        el.append(P(f'<b>{nombre}</b>', sH2))
        el.append(tabla([
            [P('<b>Entradas</b>', sCellB), P(entradas, sCell)],
            [P('<b>Salidas / comportamiento</b>', sCellB), P(salidas, sCell)],
            [P('<b>Código</b>', sCellB), P(f'<font face="Courier" size="8">{archivos}</font>', sCell)],
        ], [34 * mm, 128 * mm], header=False))

    # ---------------- ÍTEM 2 ----------------
    el.append(P('2. Documento técnico del sistema (ítem 2)', sH1))
    el.append(P('<b>2.1 Descripción general.</b> InvenXis es un sistema de gestión de '
                'inventarios, proveedores, ventas y facturación electrónica, con arquitectura '
                'API-first: backend Django + DRF (lógica y datos) y SPA React (presentación).', sBody))
    el.append(P('<b>2.2 Arquitectura.</b> Petición HTTP → <font face="Courier" size="8">config/urls.py '
                '→ productos/urls_api.py → APIView/serializers → ORM → PostgreSQL/SQLite → JSON → '
                'TanStack Query → React</font>. La presentación vive en la SPA; Django expone API, '
                'admin y documentación. Decisiones clave: transacciones atómicas en ventas/facturación, '
                'caché de dashboard con invalidación por escritura, throttling, paginación estándar y '
                'code-splitting por ruta.', sBody))
    el.append(P('<b>2.3 Modelo de datos.</b> Proveedor 1—N Producto; Proveedor 1—N Pedido 1—N '
                'DetallePedido N—1 Producto; Venta 1—N DetalleVenta N—1 Producto; Venta 1—1 Factura '
                '1—N NotaCredito; ContadorDocumento (consecutivos); User/Group de Django para RBAC. '
                'Tablas: Proveedor, Producto, Pedido, DetallePedido, Venta, DetalleVenta, '
                'ContadorDocumento, Factura, NotaCredito.', sBody))
    el.append(P('<b>2.4 Tecnologías y versiones (verificadas).</b>', sH2))
    el.append(tabla([
        [P('<b>Capa</b>', sCellB), P('<b>Tecnología y versión</b>', sCellB), P('<b>Uso</b>', sCellB)],
        [P('Lenguaje', sCell), P('Python 3.13.7', sCell), P('Backend', sCell)],
        [P('Framework', sCell), P('Django 6.0.7', sCell), P('Servidor y ORM', sCell)],
        [P('API', sCell), P('DRF 3.17.1 + SimpleJWT + drf-spectacular', sCell), P('REST, auth, OpenAPI', sCell)],
        [P('Base de datos', sCell), P('SQLite (dev) / PostgreSQL 16 (prod)', sCell), P('Persistencia', sCell)],
        [P('Caché', sCell), P('Redis 7 (prod) / local (dev)', sCell), P('Dashboard', sCell)],
        [P('Servidor prod', sCell), P('Gunicorn + WhiteNoise (Docker)', sCell), P('Despliegue', sCell)],
        [P('Lenguaje', sCell), P('TypeScript 6.0.3', sCell), P('Frontend tipado', sCell)],
        [P('UI', sCell), P('React 19.2.8 + Vite 8.1.5 + Tailwind v4', sCell), P('SPA', sCell)],
        [P('Datos', sCell), P('Axios + TanStack Query 5', sCell), P('HTTP, caché cliente', sCell)],
        [P('Calidad', sCell), P('pytest + Playwright + oxlint + tsc', sCell), P('Tests y lint', sCell)],
        [P('Runtime', sCell), P('Node 24.16.0 / npm 11.13.0', sCell), P('Frontend', sCell)],
    ], [28 * mm, 62 * mm, 72 * mm]))
    el.append(P('<b>2.5 Instalación y ejecución.</b> Backend: <font face="Courier" size="8">python -m venv venv; '
                'pip install -r requirements.txt; copy .env.example .env; python manage.py migrate; '
                'python manage.py seed_data; python manage.py runserver</font> '
                '(http://127.0.0.1:8000). Frontend: <font face="Courier" size="8">cd frontend; npm install; '
                'npm run dev</font> (http://localhost:3000). Demo: admin/admin, operador/operador123. '
                'Producción: <font face="Courier" size="8">docker compose up --build</font>.', sBody))
    el.append(P('<b>2.6 Manual de usuario (resumen).</b> Ingresar con usuario/clave → Dashboard (KPIs y recientes) → '
                'Productos (buscar, filtrar, crear, editar, eliminar) → Proveedores (directorio y pedidos) → Ventas '
                '(registrar con descuento automático de stock) → Facturación (facturar, emitir FE, PDF/UBL, anular con '
                'nota crédito — solo Administradores) → Reportes (inventario, más vendidos, ventas, exportar). '
                'El escudo del sidebar abre el panel Django admin (solo staff).', sBody))
    el.append(P('<b>2.7 Conclusiones.</b> El sistema cumple el alcance con calidad verificable (45 pruebas backend + '
                '2 e2e en verde); el diseño atómico evita sobregiros de stock y duplicados de factura; queda como '
                'trabajo futuro la integración real con la DIAN (certificado y proveedor tecnológico).', sBody))

    # ---------------- ÍTEM 3 ----------------
    el.append(P('3. Ambiente de desarrollo y pruebas (ítem 3)', sH1))
    el.append(tabla([
        [P('<b>Herramienta</b>', sCellB), P('<b>Versión</b>', sCellB)],
        [P('Python', sCell), P('3.13.7', sCell)],
        [P('Django / DRF', sCell), P('6.0.7 / 3.17.1', sCell)],
        [P('Node.js / npm', sCell), P('24.16.0 / 11.13.0', sCell)],
        [P('React / Vite / TypeScript', sCell), P('19.2.8 / 8.1.5 / 6.0.3', sCell)],
        [P('Base de datos dev', sCell), P('SQLite (db.sqlite3, ignorada por git)', sCell)],
        [P('Base de datos prod', sCell), P('PostgreSQL 16 + Redis 7 (docker-compose)', sCell)],
        [P('Control de versiones', sCell), P('Git + GitHub', sCell)],
        [P('Navegador de pruebas', sCell), P('Chromium (Playwright)', sCell)],
        [P('SO de desarrollo', sCell), P('Windows + PowerShell 5.1', sCell)],
    ], [70 * mm, 92 * mm]))
    el.append(P('Reproducción del ambiente (pasos): 1) <font face="Courier" size="8">python -m venv venv</font> y activar; '
                '2) <font face="Courier" size="8">pip install -r requirements.txt</font>; 3) copiar '
                '<font face="Courier" size="8">.env.example → .env</font>; 4) <font face="Courier" size="8">python '
                'manage.py migrate && python manage.py seed_data</font>; 5) <font face="Courier" size="8">python '
                'manage.py runserver</font>; 6) en otra terminal <font face="Courier" size="8">cd frontend && npm '
                'install && npm run dev</font>; 7) verificar con <font face="Courier" size="8">pytest -q</font> y '
                '<font face="Courier" size="8">npm run build</font>. Variables clave en <font face="Courier" size="8">'
                '.env.example</font>: SECRET_KEY, DEBUG, DB_ENGINE/Nombre, JWT_*, REDIS_URL, CORS_ALLOWED_ORIGINS.',
                sBody))

    # ---------------- ÍTEM 4 ----------------
    el.append(P('4. Código por control de versiones (ítem 4)', sH1))
    el.append(P(f'Repositorio remoto (público, accesible al instructor): {REPO}, rama principal '
                '<font face="Courier" size="8">main</font>. 18 commits con mensajes convencionales '
                '(feat/fix/chore/docs/ci). Historial reciente:', sBody))
    commits = [
        'ee2616f feat: modulo de ventas completo con facturacion y FE DIAN-ready',
        '6ca0e78 fix: login conserva next al admin + RBAC demo',
        '95e020e feat: acceso al panel Django admin desde el sidebar',
        '39e5ced feat: hardening senior x10 (health, throttle, factura uuid, a11y)',
        'cd0dabd feat: seed_data --force purga demo y resiembra determinista',
        '390eb1e feat: TanStack Query en SPA, API en /api, e2e Playwright, retiro SSR',
        '9d21c8c feat: P0+P1 hardening (venta atómica, logout blacklist, docker)',
        'd12bb07 chore: rename InvenSoft Pro to InvenXis',
    ]
    for c in commits:
        el.append(P(f'<font face="Courier" size="8">{c}</font>', sSmall))
    el.append(P('CI (GitHub Actions): job backend (<font face="Courier" size="8">pytest --cov</font>), job frontend '
                '(<font face="Courier" size="8">npm run build + lint</font>) y job e2e (Django + seed + Vite + Playwright).',
                sBody))

    # ---------------- ÍTEM 5 ----------------
    el.append(P('5. Acta de pruebas y aceptación (ítem 5)', sH1))
    el.append(P('<b>5.1 Plan de pruebas manual.</b> Casos ejecutados contra el sistema real; se compara '
                'resultado esperado vs. obtenido:', sBody))
    casos = [
        ('TC-01', 'Inicio de sesión válido', 'Acceso y panel principal', 'Acceso y panel (API + e2e)', 'Cumple'),
        ('TC-02', 'Crear producto', 'Registro creado', 'Creado vía API y UI', 'Cumple'),
        ('TC-03', 'Listar/buscar/paginar', 'Datos correctos y paginados', 'Paginación y filtros OK', 'Cumple'),
        ('TC-04', 'Editar producto', 'Dato actualizado', 'Actualizado vía API y UI', 'Cumple'),
        ('TC-05', 'Eliminar producto', 'Registro eliminado', 'Eliminado vía API y UI', 'Cumple'),
        ('TC-06', 'Registrar venta', 'Venta creada y stock descontado', 'Descuento atómico exacto', 'Cumple'),
        ('TC-07', 'Venta sin stock', 'Rechazo 400 sin crear venta', '400 + rollback total', 'Cumple'),
        ('TC-08', 'Facturar venta (IVA 19%)', 'Factura con totales correctos', 'Subtotal/IVA/total exactos', 'Cumple'),
        ('TC-09', 'Emitir FE (CUFE+UBL)', 'Validada con CUFE y XML', 'Aceptada mock, XML válido', 'Cumple'),
        ('TC-10', 'Anular factura + RBAC', 'NC creada, stock devuelto; operador 403', 'NC + stock + 403 OK', 'Cumple'),
        ('TC-11', 'Logout blacklist + throttle', 'Refresh invalidado; abuso 429', 'Blacklist y 429 OK', 'Cumple'),
        ('TC-12', 'Integración DIAN en producción', 'Emisión real ante DIAN', 'Proveedor mock; falta certificado y proveedor tecnológico', 'No cumple'),
    ]
    filas = [[P('<b>ID</b>', sCellB), P('<b>Caso</b>', sCellB), P('<b>Esperado</b>', sCellB),
              P('<b>Obtenido</b>', sCellB), P('<b>Estado</b>', sCellB)]]
    for tc, caso, esp, obt, est in casos:
        color = VERDE if est == 'Cumple' else colors.red
        filas.append([P(tc, sCell), P(caso, sCell), P(esp, sCell), P(obt, sCell),
                      P(f'<font color="{color.hexval()}"><b>{est}</b></font>', sCell)])
    el.append(tabla(filas, [14 * mm, 34 * mm, 38 * mm, 44 * mm, 32 * mm]))
    el.append(P('<b>5.2 Ejecución y resultados.</b> Backend: 45 pruebas pytest en verde '
                '(modelos 21 + venta atómica 3 + seed 2 + hardening 6 + RBAC 3 + facturación 10), sin warnings. '
                'Frontend: <font face="Courier" size="8">tsc + vite build</font> OK, <font face="Courier" size="8">'
                'oxlint</font> 0 errores. E2E Playwright: 2/2 (smoke + facturación punta a punta contra Django real).',
                sBody))
    el.append(P('<b>5.3 Observaciones y pendientes.</b> TC-12 documentado como pendiente con honestidad técnica: '
                'la arquitectura prevé el proveedor real (<font face="Courier" size="8">productos/fe/proveedores.py:'
                'get_proveedor</font>), pero la emisión productiva exige certificado digital, firma del UBL, rango de '
                'numeración autorizado y validación contra la resolución DIAN vigente. Prioridad: media (no bloquea '
                'el uso del sistema en modo demostración).', sBody))
    el.append(P('<b>5.4 Acta de aceptación (formato).</b>', sH2))
    el.append(tabla([
        [P('<b>Proyecto</b>', sCellB), P('InvenXis — Sistema de Gestión de Inventarios (v1.0)', sCell)],
        [P('<b>Evidencia</b>', sCellB), P(EVIDENCIA + ' — Módulos Integrados', sCell)],
        [P('<b>Aprendiz / Ficha</b>', sCellB), P(f'{APRENDIZ} / {FICHA}', sCell)],
        [P('<b>Fecha</b>', sCellB), P(FECHA, sCell)],
        [P('<b>Resultado</b>', sCellB), P('11 casos Cumplen / 1 pendiente documentado (TC-12)', sCell)],
        [P('<b>Soporte</b>', sCellB), P(f'Repositorio Git ({REPO}), pruebas automatizadas, manuales', sCell)],
    ], [42 * mm, 120 * mm], header=False))
    el.append(P('Declaración: el evaluador/cliente, luego de revisar la solución y verificar el cumplimiento de los '
                'requisitos acordados, acepta el entregable con el pendiente TC-12 documentado. Se firma en señal de '
                'conformidad.', sBody))
    el.append(Spacer(1, 6))
    el.append(tabla([
        [P('<b>Evaluador / Instructor</b>', sCellB), P('<b>Aprendiz</b>', sCellB)],
        [P(f'Nombre: {INSTRUCTOR}<br/>Firma: ___________________________<br/>Fecha: {FECHA}', sCell),
         P(f'Nombre: {APRENDIZ}<br/>Firma: ___________________________<br/>Fecha: {FECHA}', sCell)],
    ], [81 * mm, 81 * mm]))

    # ---------------- ANEXOS ----------------
    el.append(P('A. Anexos', sH1))
    el.append(P('<b>Endpoints principales</b> (base <font face="Courier" size="8">/api/</font>): auth/login, '
                'auth/refresh, auth/logout, auth/me, productos/, proveedores/, proveedores/{id}/pedidos/, pedidos/{id}/, '
                'ventas/, ventas/{id}/facturar/, facturas/, facturas/{id}/, facturas/{id}/emitir|anular|pdf|ubl/, '
                'notas-credito/, dashboard/, reportes/inventario|mas-vendidos|ventas/, reportes/exportar/excel|pdf/{tipo}/, '
                'health/, docs/, redoc/.', sBody))
    el.append(P('<b>Credenciales demo</b> (solo desarrollo): admin/admin (superuser), operador/operador123 '
                '(grupo Operadores). <b>Enlaces:</b> app http://localhost:3000, API http://127.0.0.1:8000, docs '
                'http://127.0.0.1:8000/api/docs/, admin http://127.0.0.1:8000/admin/, repo ' + REPO + '.', sBody))

    doc.build(el)
    print(f'OK: {out}')


if __name__ == '__main__':
    main()
