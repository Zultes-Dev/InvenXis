from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

admin.site.site_header = 'InvenXis - Administración'
admin.site.site_title = 'InvenXis Admin'


def root_redirect(request):
    # API-first: la UI vive en la SPA (frontend/). La raíz expone la
    # documentación interactiva de la API.
    return redirect('swagger-ui')


urlpatterns = [
    path('', root_redirect),
    path('admin/', admin.site.urls),
    path('api/', include('productos.urls_api')),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        next_page='swagger-ui'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # API Schema (Swagger/OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
