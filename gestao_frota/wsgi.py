"""
Configuração WSGI para o projeto gestao_frota.

Expõe a chamada WSGI como uma variável de módulo chamada ``application``.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_frota.settings')

application = get_wsgi_application()
