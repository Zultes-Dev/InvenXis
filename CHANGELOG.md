# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- GitHub Actions CI (backend tests + coverage, frontend build & lint)
- Issue and pull request templates
- Security policy and contributing guidelines

## [1.1.0] - 2026-08-19

### Added
- Django REST Framework backend with JWT authentication (SimpleJWT)
- Products, suppliers, purchase orders, and sales modules with automatic stock deduction
- Dashboard with KPIs, recent activity, and Chart.js visualizations
- PDF and Excel report exports
- React 19 + Vite + TypeScript single-page application with dark/light mode
- Automated backend test suite (pytest + factory-boy)
- Professional documentation (README, community and security guidelines)

## [1.0.0] - 2026-07-23

### Added
- Initial Django application with server-rendered templates
- SQLite development database, seed data command, and MIT license