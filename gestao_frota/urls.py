from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('frota.urls')),  # Conecta as rotas do app frota
]
