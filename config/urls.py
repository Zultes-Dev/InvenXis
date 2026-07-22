from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

admin.site.site_url = '/productos/'
admin.site.site_header = 'InvenSoft - Administración'
admin.site.site_title = 'InvenSoft Admin'

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('productos:dashboard')
    return redirect('login')

urlpatterns = [
    path('', root_redirect),
    path('admin/', admin.site.urls),
    path('productos/', include('productos.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html', next_page='productos:dashboard'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
