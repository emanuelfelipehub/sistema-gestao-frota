from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Veículos
    path('veiculos/', views.VeiculoList.as_view(), name='veiculo_list'),
    path('veiculos/novo/', views.VeiculoCreate.as_view(), name='veiculo_create'),
    path('veiculos/<int:pk>/', views.VeiculoDetail.as_view(), name='veiculo_detail'),
    path('veiculos/<int:pk>/editar/', views.VeiculoUpdate.as_view(), name='veiculo_update'),
    path('veiculos/<int:pk>/excluir/', views.VeiculoDelete.as_view(), name='veiculo_delete'),

    # Motoristas
    path('motoristas/', views.MotoristaList.as_view(), name='motorista_list'),
    path('motoristas/novo/', views.MotoristaCreate.as_view(), name='motorista_create'),
    path('motoristas/<int:pk>/', views.MotoristaDetail.as_view(), name='motorista_detail'),
    path('motoristas/<int:pk>/editar/', views.MotoristaUpdate.as_view(), name='motorista_update'),
    path('motoristas/<int:pk>/excluir/', views.MotoristaDelete.as_view(), name='motorista_delete'),

    # Mecânicos
    path('mecanicos/', views.MecanicoList.as_view(), name='mecanico_list'),
    path('mecanicos/novo/', views.MecanicoCreate.as_view(), name='mecanico_create'),
    path('mecanicos/<int:pk>/', views.MecanicoDetail.as_view(), name='mecanico_detail'),
    path('mecanicos/<int:pk>/editar/', views.MecanicoUpdate.as_view(), name='mecanico_update'),
    path('mecanicos/<int:pk>/excluir/', views.MecanicoDelete.as_view(), name='mecanico_delete'),

    # Peças
    path('pecas/', views.PecaList.as_view(), name='peca_list'),
    path('pecas/novo/', views.PecaCreate.as_view(), name='peca_create'),
    path('pecas/<int:pk>/', views.PecaDetail.as_view(), name='peca_detail'),
    path('pecas/<int:pk>/editar/', views.PecaUpdate.as_view(), name='peca_update'),
    path('pecas/<int:pk>/excluir/', views.PecaDelete.as_view(), name='peca_delete'),

    # Manutenções (entidade associativa Item_Manutenção tratada via formset)
    path('manutencoes/', views.ManutencaoList.as_view(), name='manutencao_list'),
    path('manutencoes/novo/', views.manutencao_create, name='manutencao_create'),
    path('manutencoes/<int:pk>/', views.ManutencaoDetail.as_view(), name='manutencao_detail'),
    path('manutencoes/<int:pk>/editar/', views.manutencao_update, name='manutencao_update'),
    path('manutencoes/<int:pk>/excluir/', views.manutencao_delete, name='manutencao_delete'),

    # Relatórios
    path('relatorios/estoque/', views.relatorio_estoque, name='relatorio_estoque'),
    path('relatorios/historico/', views.relatorio_historico, name='relatorio_historico'),
]
