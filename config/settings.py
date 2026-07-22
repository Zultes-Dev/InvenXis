"""
Django settings for config project.
Sistema de Gestión de Inventarios — InvPro
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-$y8gwmias&c5d-cyur)5sj_r(#wn7i(lzsbiw)b@3+kc15gh%4'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'productos',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ─── MySQL 8 (Laragon) ─────────────────────────────────────
# Requisito: tener Laragon corriendo con MySQL 8 activo.
# 1. Abre Laragon → Iniciar MySQL
# 2. Crea la base de datos: CREATE DATABASE inventario_db CHARACTER SET utf8mb4;
# 3. Ajusta USER / PASSWORD según tu configuración Laragon.
# Por defecto Laragon usa: root / (sin contraseña) / localhost / 3306
#
# Si no tienes MySQL corriendo, cambia ENGINE a 'django.db.backends.sqlite3'
# y NAME a BASE_DIR / 'db.sqlite3' para desarrollo local.
# ─── MySQL 8 (Laragon) — Producción ───────────────────────
# Requisito: Laragon con MySQL 8 activo y base 'inventario_db' creada.
#   CREATE DATABASE inventario_db CHARACTER SET utf8mb4;
# Ajusta USER / PASSWORD según tu configuración Laragon.
# Por defecto: root / (vacío) / localhost / 3306
#
# Para desarrollo sin MySQL, cambia a:
#   ENGINE: 'django.db.backends.sqlite3'
#   NAME: BASE_DIR / 'db.sqlite3'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─── MySQL 8 (Laragon) — Producción ───────────────────────
# Descomenta y ajusta cuando Laragon con MySQL 8 esté activo.
# Requisito: CREATE DATABASE inventario_db CHARACTER SET utf8mb4;
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'inventario_db',
#         'USER': 'root',
#         'PASSWORD': '',
#         'HOST': 'localhost',
#         'PORT': '3306',
#         'OPTIONS': {'charset': 'utf8mb4'},
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Autenticación ─────────────────────────────────────────
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/productos/'
LOGOUT_REDIRECT_URL = '/accounts/login/'
