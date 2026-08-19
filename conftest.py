"""Pytest configuration for InvenSoft Pro tests."""
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Ensure logs directory exists
BASE_DIR = Path(__file__).resolve().parent
logs_dir = BASE_DIR / 'logs'
logs_dir.mkdir(exist_ok=True)

django.setup()
