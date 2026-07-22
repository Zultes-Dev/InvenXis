# 📦 InvenSoft Pro — Enterprise Inventory Management System

[![Django](https://img.shields.io/badge/Django-6.0%2B-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-amber?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)](#)
[![UI/UX](https://img.shields.io/badge/UI%2FUX-Senior%20Design%20System-e8a230?style=for-the-badge)](#)

**InvenSoft Pro** es un sistema integral de gestión de inventarios, control de stock y administración de proveedores diseñado con estándares de ingeniería enterprise. Combina una arquitectura limpia en el backend mediante Django con un **Design System customizado** en el frontend que ofrece alta interactividad, analítica visual interactiva y soporte nativo para **Dark/Light Mode**.

---

## 🌟 Características Principales

### 📊 Dashboard Operativo & Analítica
- **KPI Cards con Sparklines**: Visualización de métricas clave (Total Productos, Stock Bajo, Proveedores Activos, Valor Total en Inventario) con acentos cromáticos e indicadores de tendencia.
- **Acciones Rápidas (Quick Actions)**: Flujos directos para creación de ítems, registro de proveedores y exportación de informes.
- **Actividad Reciente en Vivo**: Paneles interactivos con avatares tipográficos por iniciales ybadges de estado dinámicos.

### 📦 Gestión Inteligente de Productos
- **Filtrado Live en Cliente**: Búsqueda instantánea en tablas sin recargas de página.
- **Sorting de Columnas**: Ordenamiento numérico y alfabético directo en encabezados.
- **Nivel de Stock Visual**: Barras de progreso dinámicas con semafórica (Normal / Bajo / Sin Stock).
- **Vista de Detalle Hero**: Tarjetas informativas avanzadas con desglose numérico, stock mínimo, fechas de auditoría y métricas financieras.

### 🏭 Módulo de Proveedores
- **Directorios Interactivos**: Enlaces directos para llamadas (`tel:`) y correo electrónico (`mailto:`).
- **Filtros por Estado**: Gestión de proveedores activos e inactivos con tarjetas de estado visuales.

### 📈 Centro de Reportes & Exportación
- **Integración Chart.js Dinámica**: Gráficas responsivas (barras, dona, pastel) que adaptan su paleta de colores en tiempo real al cambiar entre Dark y Light mode.
- **Reporte Completo de Inventario & Proveedores**: Indicadores financieros consolidados y resúmenes ejecutivos.
- **Soporte de Impresión & Excel**: Vistas optimizadas para impresión (`@media print`) y descargas de reportes en hojas de cálculo.

### 🎨 Design System & UX Senior
- **Navegación Móvil Fluid**: Sidebar deslizable con menú hamburger animado y overlay backdrop blur.
- **Formularios con Steppers & Validación Live**: Indicadores paso a paso, formateadores de precio en tiempo real (`$15,000`), contadores de caracteres y animaciones de carga.
- **Buscador Global (`Ctrl+K` / `Cmd+K`)**: Atajo de teclado universal con menú desplegable de sugerencias en vivo.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Descripción |
|---|---|---|
| **Backend** | Python 3.11+ / Django 6.0 | Arquitectura MVC/MVT robusta, autenticación nativa y ORM optimizado |
| **Database** | SQLite3 / MySQL (`mysqlclient`) | Soporte dual para desarrollo local y despliegue a producción |
| **Frontend** | Vanilla JavaScript (ES6+) | Lógica interactiva en cliente sin dependencias pesadas |
| **Estilos** | CSS Custom Properties (Variables) | Design System propio con soporte dinámico de temas (Dark/Light) |
| **Visualización** | Chart.js 4.x | Gráficos vectoriales e interactivos para análisis de datos |
| **Tipografía** | Google Fonts | *Syne* (Cuerpo y títulos), *DM Serif Display* (Números hero), *DM Mono* (Métricas) |

---

## 📁 Estructura del Proyecto

```
InvenSoft-Pro/
├── config/                   # Configuración global del proyecto Django
│   ├── settings.py           # Ajustes de entorno, base de datos y apps
│   ├── urls.py               # Enrutamiento principal
│   ├── asgi.py & wsgi.py     # Interfaces de despliegue servidor
│
├── productos/                # Aplicación principal de dominio
│   ├── models.py             # Modelos de datos (Producto, Proveedor)
│   ├── views.py              # Lógica de negocio y renderizado de reportes
│   ├── forms.py              # Formularios con validaciones customizadas
│   ├── urls.py               # Enrutamiento de la app
│   └── admin.py              # Configuración de administración Django
│
├── templates/                # Arquitectura de plantillas HTML
│   ├── base.html             # Shell principal, sidebar, topbar, JS global & CSS Tokens
│   └── productos/            # Vistas específicas del módulo
│       ├── dashboard.html
│       ├── lista_productos.html
│       ├── lista_proveedores.html
│       ├── detalle_producto.html
│       ├── formulario_producto.html
│       ├── formulario_proveedor.html
│       ├── reportes.html
│       ├── reporte_detalle.html
│       ├── confirmar_eliminar.html
│       └── confirmar_eliminar_proveedor.html
│
├── static/                   # Recursos estáticos (CSS, JS, imágenes)
├── db.sqlite3                # Base de datos local de desarrollo (git-ignored)
├── requirements.txt          # Dependencias del proyecto
└── manage.py                 # CLI de gestión Django
```

---

## ⚡ Instalación y Configuración Local

### Prerrequisitos
- Python 3.11 o superior instalado
- Git instalado

### Pasos de Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Zultes-Dev/InvenSoft-Pro.git
   cd InvenSoft-Pro
   ```

2. **Crear y activar entorno virtual:**
   ```bash
   # En Windows:
   python -m venv venv
   .\venv\Scripts\activate

   # En Linux/macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar migraciones de base de datos:**
   ```bash
   python manage.py migrate
   ```

5. **Crear superusuario para el panel de administración:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Iniciar servidor de desarrollo:**
   ```bash
   python manage.py runserver
   ```

7. **Acceder a la aplicación:**
   - App Web: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - Panel Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🎨 Sistema de Diseño (Design Tokens)

El proyecto utiliza un sistema de temas basado en CSS Custom Properties en `:root` y selecciones de atributos `[data-theme="dark"]` y `[data-theme="light"]`:

```css
:root {
  --sidebar-w: 264px;
  --amber: #e8a230;
  --success: #5ed8a0;
  --danger: #e86a5e;
  --info: #6ab8e8;
  --font-main: 'Syne', sans-serif;
  --font-serif: 'DM Serif Display', serif;
  --font-mono: 'DM Mono', monospace;
}
```

---

## 📄 Licencia

Este proyecto se encuentra bajo la Licencia MIT. Consulta el archivo `LICENSE` para obtener más detalles.

---

<p center>
  Desarrollado con ❤️ por <strong>Zultes Dev Team</strong> — 2026
</p>
