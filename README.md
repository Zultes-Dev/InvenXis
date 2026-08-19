# InvenSoft Pro — Sistema de Gestión de Inventarios

[![Django](https://img.shields.io/badge/Django-6.0%2B-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-amber?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-22%20passing-success?style=for-the-badge)]()

**InvenSoft Pro** es un sistema de gestión de inventarios con arquitectura **API REST + SPA**. Combina Django REST Framework en el backend con React + Vite + TypeScript en el frontend, demostrando el patrón **cliente-servidor** con autenticación JWT.

---

## Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [Stack Tecnológico](#stack-tecnológico)
- [Requisitos Funcionales (RFU)](#requisitos-funcionales-rfu)
- [Requisitos No Funcionales (RNF)](#requisitos-no-funcionales-rnf)
- [Instalación y Configuración](#instalación-y-configuración)
- [Credenciales de Acceso](#credenciales-de-acceso)
- [Mapa de Endpoints API](#mapa-de-endpoints-api)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Comandos Útiles](#comandos-útiles)
- [Licencia](#licencia)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                    Cliente SPA                       │
│              React + Vite + TypeScript               │
│                    (frontend/)                       │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  Login   │  │Dashboard │  │Páginas CRUD       │   │
│  │  Page    │  │  Page    │  │Productos/Proveed. │   │
│  └────┬─────┘  └────┬─────┘  │Ventas/Reportes    │   │
│       │             │        └────────┬─────────┘   │
│       └─────────────┴─────────────────┘             │
│                        │                            │
│              Axios HTTP + JWT Auth                   │
└────────────────────────┬────────────────────────────┘
                         │ REST API
┌────────────────────────┴────────────────────────────┐
│                  Servidor Django                     │
│            Django REST Framework + JWT               │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  Auth    │  │  CRUD    │  │  Reportes/        │   │
│  │  JWT     │  │Productos │  │  Exportación      │   │
│  └──────────┘  │Proveed.  │  │  PDF/Excel        │   │
│                │Pedidos/  │  └──────────────────┘   │
│                │Ventas    │                          │
│                └──────────┘                          │
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │          Base de Datos SQLite                 │    │
│  └──────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## Stack Tecnológico

| Capa | Tecnología | Descripción |
|------|-----------|-------------|
| **Backend** | Python 3.11+ / Django 6.0 | Framework backend MVC/MVT |
| **API** | Django REST Framework 3.15 | REST API con ViewSets y serializers |
| **Auth** | SimpleJWT 5.3 | Autenticación JWT con access/refresh |
| **Base de Datos** | SQLite3 | Desarrollo local (migrable a MySQL) |
| **Frontend** | React 19 + Vite 8 | SPA moderna con HMR y TypeScript 6 |
| **Estilos** | Tailwind CSS v4 | Utility-first CSS con dark mode nativo |
| **Gráficos** | Chart.js 4 + react-chartjs-2 | Visualización interactiva de datos |
| **Exportación** | openpyxl + reportlab | Exportación Excel y PDF desde API |
| **Testing** | pytest 7 + factory-boy | 22 tests automatizados |

---

## Requisitos Funcionales (RFU)

| ID | Requisito | Estado | Evidencia |
|----|-----------|--------|-----------|
| **RFU-01** | Autenticación de usuarios con JWT (login/logout) | ✅ | `POST /api/auth/login/` retorna access+refresh tokens |
| **RFU-02** | Registro y gestión de productos (CRUD) | ✅ | `CRUD /api/productos/` con filtros y paginación |
| **RFU-03** | Registro y gestión de proveedores (CRUD) | ✅ | `CRUD /api/proveedores/` con conteo de productos |
| **RFU-04** | Historial de pedidos por proveedor | ✅ | `GET /api/proveedores/:id/pedidos/` |
| **RFU-05** | Creación de pedidos con detalles | ✅ | `POST /api/proveedores/:id/pedidos/` con línea de detalles |
| **RFU-06** | Registro de ventas con descuento de stock | ✅ | `POST /api/ventas/` descuenta inventario automáticamente |
| **RFU-07** | Dashboard con KPIs y actividad reciente | ✅ | `GET /api/dashboard/` con métricas y listados |
| **RFU-08** | Reporte de inventario con estadísticas | ✅ | `GET /api/reportes/inventario/` |
| **RFU-09** | Reporte de productos más vendidos | ✅ | `GET /api/reportes/mas-vendidos/` con ranking |
| **RFU-10** | Exportación de reportes a PDF | ✅ | `GET /api/reportes/exportar/pdf/:tipo/` |
| **RFU-11** | Exportación de reportes a Excel | ✅ | `GET /api/reportes/exportar/excel/:tipo/` |
| **RFU-12** | Filtros y búsqueda en listados | ✅ | Parámetros `q`, `categoria`, `estado`, `desde`, `hasta` |
| **RFU-13** | Paginación de resultados | ✅ | `page` y `page_size` en todos los listados |
| **RFU-14** | SPA Frontend standalone (cliente React) | ✅ | `frontend/` - React + Vite + TypeScript |
| **RFU-15** | Dark/Light mode en frontend | ✅ | Toggle con persistencia local |
| **RFU-16** | Visualización de datos con Chart.js | ✅ | Dashboard con gráficos de reportes |

## Requisitos No Funcionales (RNF)

| ID | Requisito | Estado | Evidencia |
|----|-----------|--------|-----------|
| **RNF-01** | API RESTful con endpoints consistentes | ✅ | `/api/{recurso}/` con métodos HTTP estándar |
| **RNF-02** | Formato de respuesta JSON uniforme | ✅ | `{ success, data?, errors? }` en todas las respuestas |
| **RNF-03** | Autenticación segura con JWT | ✅ | Tokens access (5min) + refresh (24h) con renovación |
| **RNF-04** | Frontend responsive (móvil/tablet/desktop) | ✅ | Tailwind responsive: `sm:`, `md:`, `lg:` breakpoints |
| **RNF-05** | Pruebas automatizadas (mín. 20) | ✅ | 22 tests pasando con pytest + factory-boy |
| **RNF-06** | Cobertura de tests > 70% | ✅ | `pytest --cov` configurado |
| **RNF-07** | Documentación de API con Swagger/OpenAPI | ✅ | `/api/docs/` y `/api/redoc/` |
| **RNF-08** | Separación backend/frontend (cliente-servidor) | ✅ | API REST con SPA standalone |
| **RNF-09** | Manejo de errores con códigos HTTP adecuados | ✅ | 200, 201, 204, 400, 401, 404, 500 |
| **RNF-10** | Refresh automático de tokens JWT | ✅ | Interceptor axios renovación silenciosa |
| **RNF-11** | UX moderna con modo oscuro | ✅ | Variables CSS, transiciones, animaciones |

---

## Instalación y Configuración

### Prerrequisitos

- Python 3.11+
- Node.js 20+ (para frontend)
- Git

### Backend (Django API)

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/InvenSoft-Pro.git
cd InvenSoft-Pro

# 2. Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env    # Windows
cp .env.example .env      # Linux/macOS

# 5. Ejecutar migraciones y datos semilla
python manage.py migrate
python manage.py seed_data

# 6. Iniciar servidor
python manage.py runserver
```

### Frontend (React SPA)

```bash
# 1. Ir al directorio frontend
cd frontend

# 2. Instalar dependencias
npm install

# 3. Configurar URL de la API (opcional, default: http://127.0.0.1:8000)
copy .env.example .env    # Windows

# 4. Iniciar en desarrollo (con proxy a Django)
npm run dev

# 5. Abrir navegador en http://localhost:3000

# 6. Para build de producción
npm run build
```

> **Nota**: El frontend en desarrollo (`npm run dev`) usa un proxy de Vite que redirige `/api/*` a `http://127.0.0.1:8000`. Asegúrate de que el backend Django esté corriendo.

---

## Credenciales de Acceso

La API incluye datos semilla. Usa estas credenciales para probar:

| Rol | Usuario | Contraseña |
|-----|---------|-----------|
| **Administrador** | `admin` | `admin` |
| **Operador** | `operador` | `operador123` |

---

## Mapa de Endpoints API

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Iniciar sesión (retorna JWT) |
| POST | `/api/auth/refresh/` | Renovar token de acceso |
| GET | `/api/auth/me/` | Obtener usuario autenticado |

### Productos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/productos/` | Listar productos (filtros: `q`, `categoria`, `estado`, `estado_stock`, `proveedor`) |
| POST | `/api/productos/` | Crear producto |
| GET | `/api/productos/{id}/` | Obtener detalle |
| PUT | `/api/productos/{id}/` | Actualizar producto completo |
| PATCH | `/api/productos/{id}/` | Actualizar producto parcial |
| DELETE | `/api/productos/{id}/` | Eliminar producto |

### Proveedores

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/proveedores/` | Listar proveedores (filtros: `q`, `estado`, `categoria`) |
| POST | `/api/proveedores/` | Crear proveedor |
| GET | `/api/proveedores/{id}/` | Obtener detalle con conteo |
| PUT | `/api/proveedores/{id}/` | Actualizar |
| PATCH | `/api/proveedores/{id}/` | Actualizar parcial |
| DELETE | `/api/proveedores/{id}/` | Eliminar |

### Pedidos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/proveedores/{proveedor_id}/pedidos/` | Historial de pedidos por proveedor |
| POST | `/api/proveedores/{proveedor_id}/pedidos/` | Crear pedido para proveedor |
| GET | `/api/pedidos/{id}/` | Detalle de pedido |
| PATCH | `/api/pedidos/{id}/` | Actualizar estado |
| DELETE | `/api/pedidos/{id}/` | Eliminar |

### Ventas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/ventas/` | Listar ventas (filtros: `desde`, `hasta`) |
| POST | `/api/ventas/` | Crear venta (descuenta stock) |

### Reportes y Dashboard

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/dashboard/` | KPIs + actividad reciente |
| GET | `/api/reportes/inventario/` | Estadísticas de inventario |
| GET | `/api/reportes/mas-vendidos/` | Ranking de productos más vendidos |
| GET | `/api/reportes/ventas/` | Estadísticas de ventas |
| GET | `/api/reportes/exportar/excel/{tipo}/` | Exportar a Excel (`inventario`, `proveedores`, `ventas`) |
| GET | `/api/reportes/exportar/pdf/{tipo}/` | Exportar a PDF |

### Documentación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/schema/` | Schema OpenAPI (JSON) |
| GET | `/api/docs/` | Swagger UI interactivo |
| GET | `/api/redoc/` | Redoc UI |

---

## Estructura del Proyecto

```
InvenSoft-Pro/
│
├── config/                   # Configuración Django
│   ├── settings.py
│   ├── urls.py               # URLs principales + Swagger
│   └── wsgi.py / asgi.py
│
├── productos/                # App principal
│   ├── models.py             # Modelos: Producto, Proveedor, Pedido, Venta
│   ├── api_views.py          # Vistas de la API REST (864 líneas)
│   ├── serializers.py        # Serializers DRF
│   ├── urls.py               # URLs web + API
│   ├── tests.py              # Tests (22 tests)
│   └── management/commands/  # seed_data.py
│
├── templates/                # Templates Django (server render)
│   └── productos/
│
├── frontend/                 # SPA React + Vite + TypeScript
│   ├── src/
│   │   ├── api/              # Servicio API (axios + JWT interceptor)
│   │   ├── contexts/         # AuthContext + ThemeContext
│   │   ├── components/
│   │   │   ├── layout/       # Sidebar, Topbar, AppLayout
│   │   │   └── ui/           # Button, Input, Modal, Table, Card, Badge
│   │   ├── pages/            # Login, Dashboard, Productos, Proveedores, Ventas, Reportes
│   │   ├── types/            # TypeScript interfaces
│   │   └── utils/            # formatCurrency, formatDate, helpers
│   └── package.json
│
├── db.sqlite3                # Base de datos local
├── requirements.txt          # Dependencias Python
├── pytest.ini                # Configuración pytest
└── manage.py                 # CLI Django
```

---

## Comandos Útiles

### Backend

```bash
python manage.py runserver                # Iniciar servidor
python manage.py test                     # Ejecutar tests
pytest --cov --cov-report=term-missing    # Tests con cobertura
python manage.py seed_data                # Poblar datos de ejemplo
python manage.py makemigrations           # Crear migraciones
python manage.py migrate                  # Aplicar migraciones
python manage.py createsuperuser          # Crear admin
```

### Frontend

```bash
npm run dev       # Iniciar en modo desarrollo (puerto 3000)
npm run build     # Build de producción
npm run preview   # Vista previa del build
npm run lint      # Lint (oxlint)
```

---

## Licencia

Este proyecto está bajo la Licencia MIT.
