"""
Configuração ASGI para o projeto gestao_frota.

Expõe a chamada ASGI como uma variável de módulo chamada ``application``.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_frota.settings')

application = get_asgi_application()
