"""RBAC demo + login con next: grupos y retorno al admin."""
import pytest
from django.core.management import call_command
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse


@pytest.mark.django_db
class SeedGroupsTests(APITestCase):
    def test_operador_permisos_limitados(self):
        call_command('seed_data', force=True)
        operador = User.objects.get(username='operador')
        assert operador.has_perm('productos.view_producto')
        assert operador.has_perm('productos.add_producto')
        assert operador.has_perm('productos.change_producto')
        assert not operador.has_perm('productos.delete_producto')
        assert not operador.has_perm('auth.view_user')

    def test_admin_es_superuser(self):
        call_command('seed_data', force=True)
        admin = User.objects.get(username='admin')
        assert admin.is_superuser


@pytest.mark.django_db
class LoginNextTests(APITestCase):
    def test_login_respeta_next(self):
        User.objects.create_superuser('boss', 'boss@test.com', 'pass12345')
        page = self.client.get(reverse('login') + '?next=/admin/')
        assert page.status_code == 200
        assert 'name="next"' in page.content.decode(), 'form sin campo next'
        resp = self.client.post(
            reverse('login'),
            {'username': 'boss', 'password': 'pass12345', 'next': '/admin/'})
        assert resp.status_code == 302, resp.status_code
        assert resp['Location'].endswith('/admin/'), resp['Location']
