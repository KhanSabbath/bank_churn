# Copilot Instructions — LH Nautical Data Analytics

## 🎯 Contexto do Projeto

Você é um profissional de dados da **Banco Ilusório**, responsável por pelo sistema de análise de crédito, fraudes e insights acionáveis. O Tech Lead **Gabriel Santos** exige **organização e clareza acima de tudo** — código bem documentado vale mais que código complexo sem explicação.

### Stakeholders
| Stakeholder | Perfil |
|---|---|
| Gabriel Santos | Tech Lead — exige organização, docs e raciocínio claro |
| Marina Costa | Gerente de Negócios — foco em margens e performance |
| Sr. Almir | Fundador — cético, convencido apenas por dados sólidos |

### Frentes de Entrega
1. **EDA** — Qualidade e confiabilidade dos dados brutos
2. **Tratamento de dados** — Limpeza, padronização, modelagem SQL
3. **Análise de vendas** — KPIs, tendências
4. **Análise de clientes** — Segmentação, LTV, comportamento
5. **Previsão de demanda** — Machine Learning
6. **Sistema de recomendação** — IA

---

## 📁 Estrutura do Projeto

```
BANK_CHURN/
├── datasets/
│   ├── raw/          # Dados brutos (nunca modificar)
│   └── processed/    # Dados tratados
│   └── images/       # Visualizações e gráficos salvos
├── notebooks/        # Para notebooks
├── src/
│   ├── data_processing/   # cleaning.ipynb, validation.ipynb, transformations.ipynb
│   ├── analysis/          # eda.ipynb, cliente_analysus.ipynb
│   └── models/            # forecasting.ipynb, recommendation.ipynb
├── sql/
│   ├── modeling/     # DDL das tabelas dimensionais e fatos
│   └── queries/      # Queries analíticas comentadas
└── reports/          # Visualizações e entregável final
```

---

## 🐍 Padrões Python

### Nomenclatura
```python
# DataFrames: df_<contexto>_<estado>
df_bank_churn, df_clean_bank_churn,


# Funções: snake_case com verbo
def clean_sales_dates(df: pd.DataFrame) -> pd.DataFrame: ...
def calculate_customer_ltv(df: pd.DataFrame) -> dict: ...

# Booleanos
is_valid, has_nulls, can_process
```

### Gestão de bibliotecas
Utilize sempre o gerenciador de pacotes uv para instalar, remover ou executar bibliotecas neste projeto.

### Tipagem e Docstring (obrigatórios)
```python
def process_sales(df: pd.DataFrame, min_date: str) -> tuple[pd.DataFrame, dict]:
    """
    Processa e valida os dados de vendas.

    Args:
        df: DataFrame bruto de vendas.
        min_date: Data mínima no formato YYYY-MM-DD.

    Returns:
        Tupla (df_processado, estatísticas).

    Raises:
        ValueError: data em formato inválido.
    """
```

### Estrutura de Funções
1. Validação de entradas (`assert`, `raise`)
2. Preparação / seleção de colunas
3. Processamento principal
4. Retorno tipado

### Imports
```python
# 1. Built-in
import sys
from pathlib import Path
from typing import Dict, Tuple

# 2. Dados
import pandas as pd
import numpy as np

# 3. ML/Stats
from sklearn.preprocessing import StandardScaler

# 4. Visualização — APENAS Plotly
import plotly.express as px
import plotly.graph_objects as go

# 5. Local
from src.analysis.eda import resumo_nulos
```

---

## 📊 Padrões de Visualização — OBRIGATÓRIO

### Biblioteca
> O gerenciador de bibliotecas é o uv.
> **Usar exclusivamente `plotly.express` (px) ou `plotly.graph_objects` (go).**
> Matplotlib e Seaborn são **proibidos** em gráficos de entrega.

### Paletas de Cores

**Paleta 1 — BI Dark Green** (identidade principal)
| Papel | Hex |
|---|---|
| Verde de destaque | `#39FF5A` |
| Fundo | `#1A1A1A` |
| Degradê de fundo | `#0F2015` |
| Texto secundário | `#CCCCCC` |
| Azul petróleo (acento) | `#004D54` |

**Paleta 2 — BI Blue** (alternativa / apresentações)
| Papel | Hex |
|---|---|
| Fundo principal | `#050A30` |
| Botão / destaque | `#2D68FF` |
| Texto principal | `#FFFFFF` |
| Pontos de grade | `#3A4A7D` |

### Template padrão (Paleta 1)
```python
LAYOUT_PADRAO = dict(
    template='plotly_dark',
    paper_bgcolor='#1A1A1A',
    plot_bgcolor='#0F2015',
    font=dict(color='#CCCCCC', size=12, family='Arial'),
    title_font=dict(color='#39FF5A', size=16),
)

COLOR_SEQUENCE = ['#39FF5A', '#004D54', '#2ECC71', '#CCCCCC']
```

### Exemplo mínimo
```python
fig = px.histogram(
    df, x='total',
    title='Distribuição da coluna "total"',
    labels={'total': 'Valor total (R$)', 'count': 'Frequência'},
    color_discrete_sequence=['#39FF5A'],
)
fig.update_layout(**LAYOUT_PADRAO)
fig.show()
```

---

## 🔢 Padrões SQL

```sql
-- Arquivo: 03_fact_sales.sql
-- Descrição: Tabela fato de vendas
-- Data: YYYY-MM-DD | Autor: KhanSabbath

SELECT
    p.product_id,
    p.product_name,
    COUNT(DISTINCT s.sale_id)   AS total_vendas,
    SUM(s.sale_amount)          AS receita_total,
    AVG(s.sale_amount)          AS ticket_medio
FROM dim_products p
INNER JOIN fact_sales s ON p.product_id = s.product_id
WHERE s.sale_date >= CURRENT_DATE - INTERVAL 90 DAY
  AND s.sale_status = 'completed'
GROUP BY p.product_id, p.product_name
HAVING COUNT(DISTINCT s.sale_id) >= 5
ORDER BY receita_total DESC
LIMIT 20;
```

Regras obrigatórias: aliases descritivos, sem `SELECT *`, comentários no topo, `LIMIT` em resultados grandes, índices declarados.

---

## 📓 Padrões de Notebook

Cada notebook deve ter:
- Célula markdown inicial com **Objetivo**, **Dataset** e **Premissas**
- Seções numeradas (`## 1.1`, `## 1.2`…)
- Comentário de uma linha no topo de cada célula de código
- Célula markdown de **Insights** após cada análise
- `random_state=42` em todo modelo

---

## ✅ Checklist Rápido

| Item | Critério |
|---|---|
| Gráficos | Somente `px` ou `go`, paleta LH aplicada |
| Funções | Type hints + docstring Google |
| SQL | Sem `SELECT *`, aliases amigáveis, comentário de cabeçalho |
| Notebook | Objetivo declarado, seções numeradas, insights em markdown |
| DataFrames | Nomeados `df_<contexto>_<estado>`, nunca `df1`, `temp` |
