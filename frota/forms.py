from django import forms
from django.forms import inlineformset_factory

from .models import Veiculo, Motorista, Mecanico, Peca, Manutencao, ItemManutencao


class BootstrapModelForm(forms.ModelForm):
    """Aplica a classe 'form-control'/'form-select' e 'is-invalid' automaticamente.

    Importante: a marcação 'is-invalid' só é aplicada depois que a validação
    de fato ocorre (em full_clean, sobrescrito abaixo) — nunca dentro de
    __init__. Ler self.errors dentro de __init__ forçaria uma validação
    prematura (antes de subclasses terminarem de ajustar campos, como
    required=False em ItemManutencaoForm), deixando erros "presos" em cache
    com base em um estado incompleto do formulário.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            css = 'form-select' if isinstance(widget, forms.Select) else 'form-control'
            if isinstance(widget, forms.CheckboxInput):
                css = 'form-check-input'
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{existing} {css}'.strip()

    def full_clean(self):
        super().full_clean()
        for field_name in self.errors:
            field = self.fields.get(field_name)
            if field is None:
                continue
            existing = field.widget.attrs.get('class', '')
            if 'is-invalid' not in existing:
                field.widget.attrs['class'] = f'{existing} is-invalid'.strip()


class VeiculoForm(BootstrapModelForm):
    class Meta:
        model = Veiculo
        fields = ['placa', 'modelo', 'ano', 'quilometragem']
        widgets = {
            'placa': forms.TextInput(attrs={'placeholder': 'ABC1D23', 'maxlength': 8}),
        }


class MotoristaForm(BootstrapModelForm):
    class Meta:
        model = Motorista
        fields = ['nome', 'cnh', 'categoria', 'telefone', 'ativo']


class MecanicoForm(BootstrapModelForm):
    class Meta:
        model = Mecanico
        fields = ['nome', 'especialidade', 'turno', 'ativo']


class PecaForm(BootstrapModelForm):
    class Meta:
        model = Peca
        fields = ['nome', 'fabricante', 'valor', 'qtd_estoque', 'estoque_minimo']
        help_texts = {
            'estoque_minimo': (
                'Quando o estoque atual fica abaixo deste valor, a peça passa a '
                'aparecer no relatório de Estoque Crítico.'
            ),
        }


class ManutencaoForm(BootstrapModelForm):
    class Meta:
        model = Manutencao
        fields = ['veiculo', 'mecanico', 'data', 'tipo', 'descricao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }


class ItemManutencaoForm(BootstrapModelForm):
    class Meta:
        model = ItemManutencao
        fields = ['peca', 'quantidade', 'valor_unitario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Só o valor unitário é opcional: quando deixado em branco, é
        # preenchido automaticamente com o preço atual da peça em clean().
        # Peça e quantidade continuam obrigatórios quando a linha é usada;
        # uma linha extra totalmente vazia é ignorada pelo próprio formset
        # (empty_permitted), então isso não afeta a linha em branco padrão.
        self.fields['valor_unitario'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('DELETE'):
            return cleaned_data
        peca = cleaned_data.get('peca')
        if peca and not cleaned_data.get('valor_unitario'):
            cleaned_data['valor_unitario'] = peca.valor
        return cleaned_data


ItemManutencaoFormSet = inlineformset_factory(
    Manutencao,
    ItemManutencao,
    form=ItemManutencaoForm,
    fields=['peca', 'quantidade', 'valor_unitario'],
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


def validar_disponibilidade_estoque(formset, manutencao_original=None):
    """
    Garante que a quantidade solicitada de cada peça não ultrapasse o estoque
    disponível (considerando, em edições, a quantidade já reservada pela
    própria manutenção que está sendo editada).
    """
    quantidades_originais = {}
    if manutencao_original is not None:
        for item in manutencao_original.itens.all():
            quantidades_originais[item.peca_id] = quantidades_originais.get(
                item.peca_id, 0
            ) + item.quantidade

    solicitado = {}
    algum_item_valido = False
    for form in formset.forms:
        if not hasattr(form, 'cleaned_data'):
            continue
        cleaned = form.cleaned_data
        if not cleaned or cleaned.get('DELETE'):
            continue
        peca = cleaned.get('peca')
        quantidade = cleaned.get('quantidade')
        if not peca or not quantidade:
            continue
        algum_item_valido = True
        solicitado[peca.pk] = solicitado.get(peca.pk, 0) + quantidade

    erros = []
    for peca_id, quantidade_pedida in solicitado.items():
        peca = Peca.objects.get(pk=peca_id)
        disponivel = peca.qtd_estoque + quantidades_originais.get(peca_id, 0)
        if quantidade_pedida > disponivel:
            erros.append(
                f'Estoque insuficiente para "{peca.nome}": disponível {disponivel}, '
                f'solicitado {quantidade_pedida}.'
            )

    if not algum_item_valido:
        erros.append('Adicione pelo menos uma peça utilizada na manutenção.')

    return erros
