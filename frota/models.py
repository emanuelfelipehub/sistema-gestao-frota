import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.urls import reverse

ANO_MINIMO = 1950


def ano_maximo_permitido():
    return datetime.date.today().year + 1


def validar_ano_nao_futuro_demais(value):
    limite = ano_maximo_permitido()
    if value > limite:
        raise ValidationError(f'O ano não pode ser maior que {limite}.')


def validar_data_nao_futura(value):
    if value > datetime.date.today():
        raise ValidationError('A data da manutenção não pode estar no futuro.')


placa_validator = RegexValidator(
    # Aceita minúsculas/maiúsculas na digitação; Veiculo.save() normaliza
    # sempre para maiúsculas antes de persistir.
    regex=r'^[A-Za-z]{3}-?\d[A-Za-z0-9]\d{2}$',
    message='Informe uma placa válida no padrão antigo (ABC1234) ou Mercosul (ABC1D23).',
)

cnh_validator = RegexValidator(
    regex=r'^\d{9,11}$',
    message='A CNH deve conter apenas números (entre 9 e 11 dígitos).',
)

telefone_validator = RegexValidator(
    regex=r'^\(?\d{2}\)?[\s-]?9?\d{4}-?\d{4}$',
    message='Informe um telefone válido, ex.: (62) 99999-8888.',
)


class Veiculo(models.Model):
    placa = models.CharField(
        'Placa', max_length=8, unique=True, validators=[placa_validator],
        help_text='Formato antigo ABC1234 ou Mercosul ABC1D23.'
    )
    modelo = models.CharField('Modelo', max_length=50)
    ano = models.IntegerField(
        'Ano',
        validators=[MinValueValidator(ANO_MINIMO), validar_ano_nao_futuro_demais],
    )
    quilometragem = models.DecimalField(
        'Quilometragem (km)', max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    criado_em = models.DateTimeField('Cadastrado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['modelo']
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'

    def __str__(self):
        return f'{self.modelo} ({self.placa})'

    def save(self, *args, **kwargs):
        if self.placa:
            self.placa = self.placa.upper().replace(' ', '')
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('veiculo_detail', args=[self.pk])

    @property
    def custo_total_manutencoes(self):
        total = 0
        for manutencao in self.manutencoes.all():
            total += manutencao.custo_total
        return total


class Motorista(models.Model):
    CATEGORIA_CHOICES = [
        ('A', 'A - Motocicletas'),
        ('B', 'B - Carros'),
        ('AB', 'AB - Carros e motos'),
        ('C', 'C - Caminhões'),
        ('D', 'D - Ônibus'),
        ('E', 'E - Carretas/combinações'),
    ]

    cnh = models.CharField(
        'CNH', max_length=11, unique=True, validators=[cnh_validator]
    )
    nome = models.CharField('Nome', max_length=100)
    categoria = models.CharField('Categoria', max_length=2, choices=CATEGORIA_CHOICES)
    telefone = models.CharField(
        'Telefone', max_length=20, validators=[telefone_validator]
    )
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Motorista'
        verbose_name_plural = 'Motoristas'

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse('motorista_detail', args=[self.pk])


class Mecanico(models.Model):
    TURNO_CHOICES = [
        ('MANHA', 'Manhã'),
        ('TARDE', 'Tarde'),
        ('NOITE', 'Noite'),
    ]

    nome = models.CharField('Nome', max_length=100)
    especialidade = models.CharField('Especialidade', max_length=50)
    turno = models.CharField('Turno', max_length=10, choices=TURNO_CHOICES)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Mecânico'
        verbose_name_plural = 'Mecânicos'

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse('mecanico_detail', args=[self.pk])


class Peca(models.Model):
    nome = models.CharField('Nome', max_length=100)
    fabricante = models.CharField('Fabricante', max_length=100)
    valor = models.DecimalField(
        'Valor unitário (R$)', max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    qtd_estoque = models.IntegerField(
        'Quantidade em estoque', default=0, validators=[MinValueValidator(0)]
    )
    estoque_minimo = models.IntegerField(
        'Estoque mínimo ideal', default=5, validators=[MinValueValidator(0)],
        help_text='Usado no relatório de Estoque Crítico.'
    )

    class Meta:
        ordering = ['nome']
        verbose_name = 'Peça'
        verbose_name_plural = 'Peças'

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse('peca_detail', args=[self.pk])

    @property
    def estoque_critico(self):
        return self.qtd_estoque < self.estoque_minimo

    @property
    def estoque_faltante(self):
        return max(0, self.estoque_minimo - self.qtd_estoque)


class Manutencao(models.Model):
    TIPO_CHOICES = [
        ('PREVENTIVA', 'Preventiva'),
        ('CORRETIVA', 'Corretiva'),
    ]

    veiculo = models.ForeignKey(
        Veiculo, on_delete=models.CASCADE, related_name='manutencoes',
        verbose_name='Veículo'
    )
    mecanico = models.ForeignKey(
        Mecanico, on_delete=models.CASCADE, related_name='manutencoes',
        verbose_name='Mecânico responsável'
    )
    data = models.DateField('Data', validators=[validar_data_nao_futura])
    tipo = models.CharField('Tipo', max_length=15, choices=TIPO_CHOICES)
    descricao = models.TextField('Descrição do serviço')

    class Meta:
        ordering = ['-data']
        verbose_name = 'Manutenção'
        verbose_name_plural = 'Manutenções'

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.veiculo} ({self.data:%d/%m/%Y})'

    def get_absolute_url(self):
        return reverse('manutencao_detail', args=[self.pk])

    @property
    def custo_pecas(self):
        total = 0
        for item in self.itens.all():
            total += item.subtotal
        return total

    @property
    def custo_total(self):
        return self.custo_pecas


class ItemManutencao(models.Model):
    manutencao = models.ForeignKey(
        Manutencao, on_delete=models.CASCADE, related_name='itens'
    )
    peca = models.ForeignKey(
        Peca, on_delete=models.PROTECT, related_name='itens_utilizados',
        verbose_name='Peça'
    )
    quantidade = models.IntegerField('Quantidade', validators=[MinValueValidator(1)])
    valor_unitario = models.DecimalField(
        'Valor unitário (R$)', max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )

    class Meta:
        verbose_name = 'Item da manutenção'
        verbose_name_plural = 'Itens da manutenção'

    def __str__(self):
        return f'{self.quantidade}x {self.peca}'

    @property
    def subtotal(self):
        return self.quantidade * self.valor_unitario
