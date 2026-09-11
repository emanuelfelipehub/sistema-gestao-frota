from django.contrib import admin

from .models import ItemManutencao, Manutencao, Mecanico, Motorista, Peca, Veiculo


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'modelo', 'ano', 'quilometragem')
    search_fields = ('placa', 'modelo')
    list_filter = ('ano',)


@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnh', 'categoria', 'telefone', 'ativo')
    search_fields = ('nome', 'cnh')
    list_filter = ('categoria', 'ativo')


@admin.register(Mecanico)
class MecanicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especialidade', 'turno', 'ativo')
    search_fields = ('nome', 'especialidade')
    list_filter = ('turno', 'ativo')


@admin.register(Peca)
class PecaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'fabricante', 'valor', 'qtd_estoque', 'estoque_minimo')
    search_fields = ('nome', 'fabricante')


class ItemManutencaoInline(admin.TabularInline):
    model = ItemManutencao
    extra = 1


@admin.register(Manutencao)
class ManutencaoAdmin(admin.ModelAdmin):
    list_display = ('veiculo', 'mecanico', 'data', 'tipo')
    list_filter = ('tipo', 'data')
    search_fields = ('veiculo__placa', 'descricao')
    date_hierarchy = 'data'
    inlines = [ItemManutencaoInline]
