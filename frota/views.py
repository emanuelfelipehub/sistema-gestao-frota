from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import F, ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .forms import (
    ItemManutencaoFormSet, ManutencaoForm, MecanicoForm, MotoristaForm,
    PecaForm, VeiculoForm, validar_disponibilidade_estoque,
)
from .models import Manutencao, Mecanico, Motorista, Peca, Veiculo


# ---------------------------------------------------------------------------
# Dashboard (home)
# ---------------------------------------------------------------------------
def home(request):
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)

    contexto = {
        'total_veiculos': Veiculo.objects.count(),
        'total_motoristas': Motorista.objects.filter(ativo=True).count(),
        'total_mecanicos': Mecanico.objects.filter(ativo=True).count(),
        'manutencoes_no_mes': Manutencao.objects.filter(data__gte=inicio_mes).count(),
        'pecas_criticas': [p for p in Peca.objects.all() if p.estoque_critico],
        'ultimas_manutencoes': Manutencao.objects.select_related(
            'veiculo', 'mecanico'
        ).order_by('-data')[:5],
    }
    return render(request, 'frota/home.html', contexto)


# ---------------------------------------------------------------------------
# Mixin utilitário para telas de exclusão com tratamento de FK protegida
# ---------------------------------------------------------------------------
class ExclusaoProtegidaMixin:
    protected_message = (
        'Não é possível excluir este registro porque ele está sendo '
        'utilizado em outros cadastros.'
    )

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, self.protected_message)
            return redirect(self.success_url)


# ---------------------------------------------------------------------------
# CRUD Veículos
# ---------------------------------------------------------------------------
class VeiculoList(ListView):
    model = Veiculo
    template_name = 'frota/veiculos/listar.html'
    context_object_name = 'veiculos'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        busca = self.request.GET.get('q')
        if busca:
            qs = qs.filter(Q(placa__icontains=busca) | Q(modelo__icontains=busca))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class VeiculoDetail(DetailView):
    model = Veiculo
    template_name = 'frota/veiculos/detalhe.html'
    context_object_name = 'veiculo'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['manutencoes'] = self.object.manutencoes.select_related('mecanico').all()
        return ctx


class VeiculoCreate(SuccessMessageMixin, CreateView):
    model = Veiculo
    form_class = VeiculoForm
    template_name = 'frota/partials/form.html'
    success_url = reverse_lazy('veiculo_list')
    success_message = 'Veículo "%(modelo)s" cadastrado com sucesso.'
    extra_context = {'titulo': 'Novo Veículo', 'voltar_url': 'veiculo_list'}


class VeiculoUpdate(SuccessMessageMixin, UpdateView):
    model = Veiculo
    form_class = VeiculoForm
    template_name = 'frota/partials/form.html'
    success_url = reverse_lazy('veiculo_list')
    success_message = 'Veículo "%(modelo)s" atualizado com sucesso.'
    extra_context = {'titulo': 'Editar Veículo', 'voltar_url': 'veiculo_list'}


class VeiculoDelete(ExclusaoProtegidaMixin, DeleteView):
    model = Veiculo
    template_name = 'frota/partials/confirmar_exclusao.html'
    success_url = reverse_lazy('veiculo_list')
    extra_context = {'voltar_url': 'veiculo_list'}
    protected_message = (
        'Não é possível excluir este veículo pois existem manutenções '
        'registradas para ele.'
    )

    def form_valid(self, form):
        messages.success(self.request, 'Veículo excluído com sucesso.')
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# CRUD Motoristas
# ---------------------------------------------------------------------------
class MotoristaList(ListView):
    model = Motorista
    template_name = 'frota/motoristas/listar.html'
    context_object_name = 'motoristas'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        busca = self.request.GET.get('q')
        if busca:
            qs = qs.filter(Q(nome__icontains=busca) | Q(cnh__icontains=busca))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class MotoristaDetail(DetailView):
    model = Motorista
    template_name = 'frota/motoristas/detalhe.html'
    context_object_name = 'motorista'


class MotoristaCreate(SuccessMessageMixin, CreateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'frota/partials/form.html'
    success_url = reverse_lazy('motorista_list')
    success_message = 'Motorista "%(nome)s" cadastrado com sucesso.'
    extra_context = {'titulo': 'Novo Motorista', 'voltar_url': 'motorista_list'}


class MotoristaUpdate(SuccessMessageMixin, UpdateView):
    model = Motorista
    form_class = MotoristaForm
    template_name = 'frota/partials/form.html'
    success_url = reverse_lazy('motorista_list')
    success_message = 'Motorista "%(nome)s" atualizado com sucesso.'
    extra_context = {'titulo': 'Editar Motorista', 'voltar_url': 'motorista_list'}


class MotoristaDelete(ExclusaoProtegidaMixin, DeleteView):
    model = Motorista
    template_name = 'frota/partials/confirmar_exclusao.html'
    success_url = reverse_lazy('motorista_list')
    extra_context = {'voltar_url': 'motorista_list'}

    def form_valid(self, form):
        messages.success(self.request, 'Motorista excluído com sucesso.')
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# CRUD Mecânicos
# ---------------------------------------------------------------------------
class MecanicoList(ListView):
    model = Mecanico
    template_name = 'frota/mecanicos/listar.html'
    context_object_name = 'mecanicos'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        busca = self.request.GET.get('q')
        if busca:
            qs = qs.filter(Q(nome__icontains=busca) | Q(especialidade__icontains=busca))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class MecanicoDetail(DetailView):
    model = Mecanico
    template_name = 'frota/mecanicos/detalhe.html'
    context_object_name = 'mecanico'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['manutencoes'] = self.object.manutencoes.select_related('veiculo').all()
        return ctx


class MecanicoCreate(SuccessMessageMixin, CreateView):
    model = Mecanico
    form_class = MecanicoForm
    template_name = 'frota/partials/form.html'
    success_url = reverse_lazy('mecanico_list')
    success_message = 'Mecânico "%(nome)s" cadastrado com sucesso.'
    extra_context = {'titulo': 'Novo Mecânico', 'voltar_url': 'mecanico_list'}


class MecanicoUpdate(SuccessMessageMixin, UpdateView):
    model = Mecanico
    form_class = MecanicoForm
    template_name = 'frota/partials/form.html'
    success_url = reverse_lazy('mecanico_list')
    success_message = 'Mecânico "%(nome)s" atualizado com sucesso.'
    extra_context = {'titulo': 'Editar Mecânico', 'voltar_url': 'mecanico_list'}


class MecanicoDelete(ExclusaoProtegidaMixin, DeleteView):
    model = Mecanico
    template_name = 'frota/partials/confirmar_exclusao.html'
    success_url = reverse_lazy('mecanico_list')
    extra_context = {'voltar_url': 'mecanico_list'}

    def form_valid(self, form):
        messages.success(self.request, 'Mecânico excluído com sucesso.')
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# CRUD Peças
# ---------------------------------------------------------------------------
class PecaList(ListView):
    model = Peca
    template_name = 'frota/pecas/listar.html'
    context_object_name = 'pecas'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        busca = self.request.GET.get('q')
        if busca:
            qs = qs.filter(Q(nome__icontains=busca) | Q(fabricante__icontains=busca))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class PecaDetail(DetailView):
    model = Peca
    template_name = 'frota/pecas/detalhe.html'
    context_object_name = 'peca'


class PecaCreate(SuccessMessageMixin, CreateView):
    model = Peca
    form_class = PecaForm
    template_name = 'frota/partials/form.html'
    success_url = reverse_lazy('peca_list')
    success_message = 'Peça "%(nome)s" cadastrada com sucesso.'
    extra_context = {'titulo': 'Nova Peça', 'voltar_url': 'peca_list'}


class PecaUpdate(SuccessMessageMixin, UpdateView):
    model = Peca
    form_class = PecaForm
    template_name = 'frota/partials/form.html'
    success_url = reverse_lazy('peca_list')
    success_message = 'Peça "%(nome)s" atualizada com sucesso.'
    extra_context = {'titulo': 'Editar Peça', 'voltar_url': 'peca_list'}


class PecaDelete(ExclusaoProtegidaMixin, DeleteView):
    model = Peca
    template_name = 'frota/partials/confirmar_exclusao.html'
    success_url = reverse_lazy('peca_list')
    extra_context = {'voltar_url': 'peca_list'}
    protected_message = (
        'Não é possível excluir esta peça pois ela já foi utilizada em '
        'alguma manutenção.'
    )

    def form_valid(self, form):
        messages.success(self.request, 'Peça excluída com sucesso.')
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# CRUD Manutenções (com itens de peça em N:M via ItemManutencao)
# Inclui a baixa automática de estoque, conforme o caso de uso
# "Baixar Estoque de Peça" descrito na atividade.
# ---------------------------------------------------------------------------
class ManutencaoList(ListView):
    model = Manutencao
    template_name = 'frota/manutencoes/listar.html'
    context_object_name = 'manutencoes'
    paginate_by = 10
    queryset = Manutencao.objects.select_related('veiculo', 'mecanico')

    def get_queryset(self):
        qs = super().get_queryset()
        busca = self.request.GET.get('q')
        if busca:
            qs = qs.filter(veiculo__placa__icontains=busca)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class ManutencaoDetail(DetailView):
    model = Manutencao
    template_name = 'frota/manutencoes/detalhe.html'
    context_object_name = 'manutencao'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['itens'] = self.object.itens.select_related('peca').all()
        return ctx


@transaction.atomic
def manutencao_create(request):
    if request.method == 'POST':
        form = ManutencaoForm(request.POST)
        formset = ItemManutencaoFormSet(request.POST, instance=Manutencao())
        if form.is_valid() and formset.is_valid():
            erros_estoque = validar_disponibilidade_estoque(formset)
            if erros_estoque:
                for erro in erros_estoque:
                    messages.error(request, erro)
            else:
                manutencao = form.save()
                itens = formset.save(commit=False)
                for item in itens:
                    item.manutencao = manutencao
                    if not item.valor_unitario:
                        item.valor_unitario = item.peca.valor
                    item.save()
                    Peca.objects.filter(pk=item.peca_id).update(
                        qtd_estoque=F('qtd_estoque') - item.quantidade
                    )
                for obj in formset.deleted_objects:
                    obj.delete()
                messages.success(request, 'Manutenção registrada e estoque atualizado com sucesso.')
                return redirect('manutencao_detail', pk=manutencao.pk)
    else:
        form = ManutencaoForm()
        formset = ItemManutencaoFormSet(instance=Manutencao())

    return render(request, 'frota/manutencoes/form.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Registrar Manutenção',
        'voltar_url': 'manutencao_list',
    })


@transaction.atomic
def manutencao_update(request, pk):
    manutencao = get_object_or_404(Manutencao, pk=pk)

    if request.method == 'POST':
        form = ManutencaoForm(request.POST, instance=manutencao)
        formset = ItemManutencaoFormSet(request.POST, instance=manutencao)
        if form.is_valid() and formset.is_valid():
            erros_estoque = validar_disponibilidade_estoque(formset, manutencao_original=manutencao)
            if erros_estoque:
                for erro in erros_estoque:
                    messages.error(request, erro)
            else:
                # Devolve ao estoque as quantidades reservadas atualmente
                # antes de aplicar as novas quantidades informadas no formulário.
                for item in manutencao.itens.all():
                    Peca.objects.filter(pk=item.peca_id).update(
                        qtd_estoque=F('qtd_estoque') + item.quantidade
                    )

                form.save()
                itens = formset.save(commit=False)
                for item in itens:
                    item.manutencao = manutencao
                    if not item.valor_unitario:
                        item.valor_unitario = item.peca.valor
                    item.save()
                    Peca.objects.filter(pk=item.peca_id).update(
                        qtd_estoque=F('qtd_estoque') - item.quantidade
                    )
                for obj in formset.deleted_objects:
                    obj.delete()

                messages.success(request, 'Manutenção atualizada e estoque recalculado com sucesso.')
                return redirect('manutencao_detail', pk=manutencao.pk)
    else:
        form = ManutencaoForm(instance=manutencao)
        formset = ItemManutencaoFormSet(instance=manutencao)

    return render(request, 'frota/manutencoes/form.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Editar Manutenção',
        'voltar_url': 'manutencao_list',
        'object': manutencao,
    })


@transaction.atomic
def manutencao_delete(request, pk):
    manutencao = get_object_or_404(Manutencao, pk=pk)
    if request.method == 'POST':
        for item in manutencao.itens.all():
            Peca.objects.filter(pk=item.peca_id).update(
                qtd_estoque=F('qtd_estoque') + item.quantidade
            )
        manutencao.delete()
        messages.success(request, 'Manutenção excluída e estoque das peças devolvido.')
        return redirect('manutencao_list')

    return render(request, 'frota/partials/confirmar_exclusao.html', {
        'object': manutencao,
        'voltar_url': 'manutencao_list',
    })


# ---------------------------------------------------------------------------
# Relatórios (Etapa 6)
# ---------------------------------------------------------------------------
def relatorio_estoque(request):
    pecas = [p for p in Peca.objects.all().order_by('nome') if p.estoque_critico]
    return render(request, 'frota/relatorios/estoque.html', {'pecas': pecas})


def relatorio_historico(request):
    placa_query = request.GET.get('placa', '').strip()
    manutencoes = Manutencao.objects.none()
    custo_total = 0

    if placa_query:
        manutencoes = (
            Manutencao.objects
            .filter(veiculo__placa__icontains=placa_query)
            .select_related('veiculo', 'mecanico')
            .prefetch_related('itens__peca')
            .order_by('-data')
        )
        custo_total = sum((m.custo_total for m in manutencoes), 0)

    return render(request, 'frota/relatorios/historico.html', {
        'manutencoes': manutencoes,
        'placa_query': placa_query,
        'custo_total': custo_total,
    })
