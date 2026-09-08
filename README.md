# InvenXis

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.15-A93226?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vite.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-amber?style=for-the-badge)](LICENSE)
[![CI](https://github.com/Zultes-Dev/InvenXis/actions/workflows/ci.yml/badge.svg)](https://github.com/Zultes-Dev/InvenXis/actions/workflows/ci.yml)

A full-stack **inventory management system** with a decoupled client–server
architecture: a Django REST Framework API with JWT authentication on the backend and
a React 19 + Vite + TypeScript single-page application on the frontend.

<!-- Project screenshot: drop `dashboard.png` in docs/screenshots/ and uncomment:
<img src="docs/screenshots/dashboard.png" alt="InvenXis dashboard" width="100%" />
-->

## Features

- **JWT authentication** — access + refresh tokens with silent rotation on the frontend
- **Inventory management** — products, categories, stock control, and minimum-stock alerts
- **Supplier management** — profiles, product counts, and purchase order history
- **Sales** — register sales with automatic stock deduction and date-range filtering
- **Dashboard** — KPIs, charts (Chart.js), and recent-activity feeds
- **Reports** — inventory stats, best sellers, and sales analytics
- **PDF & Excel exports** — downloadable reports straight from the API
- **Role-aware UI** — dark/light mode, responsive Tailwind CSS interface
- **API documentation** — interactive Swagger UI and ReDoc

## Tech Stack

| Layer        | Technology                                                | Purpose                              |
|--------------|-----------------------------------------------------------|--------------------------------------|
| Backend      | Python 3.11+ / Django 6.0                                 | MVT application server               |
| API          | Django REST Framework 3.15                                | REST API (viewsets + serializers)    |
| Auth         | djangorestframework-simplejwt                              | Access/refresh JWT tokens            |
| Database     | SQLite3 (dev)                                             | Local persistence (MySQL-ready)      |
| Frontend     | React 19 + Vite 8 + TypeScript 6                          | SPA with HMR                        |
| Styling      | Tailwind CSS v4                                           | Utility-first responsive UI          |
| Charts       | Chart.js 4 + react-chartjs-2                              | Interactive data visualizations      |
| Exports      | openpyxl + reportlab                                      | Excel / PDF report generation        |
| Testing      | pytest 7 + factory-boy, oxlint, `tsc`                     | Backend + frontend quality gates     |

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    React SPA (frontend/)                  │
│         React 19 · Vite · TypeScript · Tailwind           │
│   Login · Dashboard · Inventory · Suppliers · Reports     │
│                 Axios + JWT interceptor                   │
└───────────────────────────┬──────────────────────────────┘
                            │ REST API /api/*
┌───────────────────────────┴──────────────────────────────┐
│                    Django Backend                         │
│         Django 6 · DRF · SimpleJWT · SQLite               │
│   Auth · Products · Suppliers · Orders · Sales · Reports  │
└───────────────────────────────────────────────────────────┘
```

The frontend runs standalone in development on `localhost:3000` and proxies `/api/*`
to the Django dev server; in production it can be served as static assets behind any
web server.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Git

### 1. Clone

```bash
git clone https://github.com/Zultes-Dev/InvenXis.git
cd InvenXis
```

### 2. Backend (Django API)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

pip install -r requirements.txt

copy .env.example .env       # Windows
cp .env.example .env         # Linux/macOS

python manage.py migrate
python manage.py seed_data   # optional demo data
python manage.py runserver   # http://127.0.0.1:8000
```

### 3. Frontend (React SPA)

```bash
cd frontend
npm install
copy .env.example .env       # Windows
cp .env.example .env         # Linux/macOS
npm run dev                  # http://localhost:3000 (proxies /api to Django)
```

### Demo credentials

> **⚠ Demo only — never use these credentials in production.**

| Role       | Username  | Password      |
|------------|-----------|---------------|
| Admin      | `admin`   | `admin`       |
| Operator   | `operador`| `operador123` |

## API Overview

| Method | Endpoint                            | Description                          |
|--------|-------------------------------------|--------------------------------------|
| POST   | `/api/auth/login/`                  | Authenticate, get JWT tokens         |
| POST   | `/api/auth/refresh/`                | Rotate access token                  |
| GET    | `/api/auth/me/`                     | Current authenticated user           |
| CRUD   | `/api/productos/`                   | Products (filters + pagination)      |
| CRUD   | `/api/proveedores/`                 | Suppliers (with product counts)      |
| CRUD   | `/api/proveedores/{id}/pedidos/`    | Purchase orders per supplier         |
| POST   | `/api/ventas/`                      | Register a sale (deducts stock)      |
| GET    | `/api/dashboard/`                   | KPIs + recent activity               |
| GET    | `/api/reportes/inventario/`         | Inventory statistics                 |
| GET    | `/api/reportes/mas-vendidos/`       | Best-selling products ranking        |
| GET    | `/api/reportes/exportar/pdf|excel/{tipo}/` | Export reports               |
| GET    | `/api/docs/`, `/api/redoc/`         | Swagger UI / ReDoc docs              |

## Project Structure

```
invenxis/
├── .github/                  # CI + issue/PR templates
│   └── workflows/ci.yml
├── config/                   # Django settings, routing, WSGI/ASGI
├── productos/                # Core app: models, serializers, API views
│   └── management/commands/seed_data.py
├── templates/                # Server-rendered Django templates
│   ├── admin/
│   ├── productos/
│   └── registration/
├── frontend/                 # React 19 + Vite + TypeScript SPA
│   └── src/
│       ├── api/              # axios client + JWT refresh interceptor
│       ├── components/       # layout + UI primitives
│       ├── contexts/         # auth + theme providers
│       ├── pages/            # login, dashboard, CRUD screens
│       └── types/            # TypeScript domain types
├── docs/
│   └── screenshots/          # project screenshots
├── requirements.txt          # Python dependencies
├── manage.py                 # Django CLI
└── pytest.ini                # pytest configuration
```

## Testing

```bash
# Backend: run suite with coverage
pytest --cov --cov-report=term-missing

# Frontend: type-check, build, lint
cd frontend
npm run build
npm run lint
```

## Roadmap

- [ ] MySQL/PostgreSQL production database profile + Docker Compose
- [ ] Multi-tenant organizations and fine-grained RBAC
- [ ] Product barcode/QR scanning on the SPA
- [ ] Automated end-to-end tests (Playwright) + coverage reports in CI

## License

Released under the [MIT License](LICENSE).