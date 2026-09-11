# Sistema de Gestão de Frota e Manutenção Automotiva

Sistema web em Django para gerenciar veículos de uma frota, seus motoristas,
os mecânicos da oficina, o catálogo de peças e as manutenções realizadas —
com baixa automática de estoque e relatórios gerenciais.

Desenvolvido para a atividade prática **"Desenvolvimento de Sistema Web
Dinâmico"**. A documentação completa de modelagem (MER), casos de uso e
arquitetura está em [`DOCUMENTACAO.md`](DOCUMENTACAO.md); o script SQL em
[`frota.sql`](frota.sql).

## Funcionalidades

- CRUD completo (criar, listar com busca e paginação, ver detalhes, editar,
  excluir) para Veículos, Motoristas, Mecânicos e Peças.
- Registro de Manutenções com múltiplas peças (relacionamento N:M resolvido
  pela tabela `ItemManutencao`), com **baixa automática de estoque** ao
  salvar e **devolução automática** ao editar ou excluir uma manutenção.
- Validações de formulário: formato de placa (padrão antigo ou Mercosul),
  CNH, telefone, ano do veículo, valores e quantidades não negativos,
  disponibilidade de estoque antes de confirmar uma manutenção.
- Painel inicial com indicadores (total de veículos, manutenções do mês,
  peças em estoque crítico, últimas manutenções).
- Relatório de Histórico do Veículo (por placa) e Relatório de Estoque
  Crítico.
- Interface própria (sem Bootstrap), com identidade visual autoral — ver
  seção *Design* abaixo.

## Stack

- Python 3.12+ / Django 5.x
- SQLite (padrão, zero configuração) — script MySQL equivalente disponível
  em `frota.sql` para quem preferir
- HTML + CSS puro (design system próprio em `gestao_frota/static/css/style.css`)
  e um pouco de JavaScript vanilla (menu mobile e formset dinâmico)

## Como executar

```bash
# 1. Criar e ativar um ambiente virtual
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Criar o banco de dados (SQLite, gera db.sqlite3 na raiz)
python manage.py migrate

# 4. (Opcional) criar um superusuário para acessar /admin/
python manage.py createsuperuser

# 5. (Opcional) carregar dados de exemplo
python manage.py loaddata frota/fixtures/dados_exemplo.json

# 6. Rodar o servidor de desenvolvimento
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`.

### Usando MySQL em vez de SQLite

1. Instale a dependência: descomente `mysqlclient` em `requirements.txt` e
   rode `pip install -r requirements.txt` novamente.
2. Crie o banco com o script `frota.sql` (ou deixe o Django criar as tabelas
   com `migrate`, o schema é equivalente).
3. Ajuste `DATABASES` em `gestao_frota/settings.py` para o backend
   `django.db.backends.mysql` com as credenciais do seu servidor.

## Estrutura do projeto

```
sistema-gestao-frota/
├── manage.py
├── requirements.txt
├── frota.sql                  # DDL (Etapa 3)
├── DOCUMENTACAO.md             # MER, casos de uso, arquitetura (Etapas 1, 2 e 4)
├── gestao_frota/               # Configuração do projeto Django
│   ├── settings.py
│   ├── urls.py
│   └── static/                 # CSS/JS próprios
└── frota/                      # App principal (Model, View, Template)
    ├── models.py
    ├── forms.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── migrations/
    └── templates/frota/
```


