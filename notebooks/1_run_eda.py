"""
run_eda.py — Executa o pipeline SQL de EDA sobre o dataset Bank Churn.

Objetivo:
    Carregar o CSV bruto em SQLite, aplicar o modelo dimensional (DDL)
    e executar as queries analíticas de EDA, exibindo os resultados
    com visualizações Plotly seguindo a identidade visual do Banco Ilusório.

Dataset:
    datasets/raw/Bank_Churn.csv

Premissas:
    - O CSV original não é modificado (dados brutos intocáveis).
    - O banco SQLite é recriado a cada execução (idempotência).
    - Todas as visualizações usam exclusivamente Plotly (px / go).
"""

# ============================================================================
# 1. Imports
# ============================================================================

# 1. Built-in
import sqlite3
from pathlib import Path

# 2. Dados
import pandas as pd

# 3. Visualização — APENAS Plotly
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# 2. Constantes e caminhos
# ============================================================================

# Raiz do projeto (run_eda.py está em notebooks/)
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
CSV_PATH: Path = PROJECT_ROOT / "datasets" / "raw" / "Bank_Churn.csv"
DDL_DIR: Path = PROJECT_ROOT / "sql" / "modeling"
QUERIES_PATH: Path = PROJECT_ROOT / "sql" / "queries" / "01_eda_bank_churn.sql"
DB_PATH: Path = PROJECT_ROOT / "datasets" / "processed" / "bank_churn.db"
IMAGES_DIR: Path = PROJECT_ROOT / "datasets" / "images"

# Layout padrão — Paleta 1 (BI Dark Green)
LAYOUT_PADRAO: dict = dict(
    template="plotly_dark",
    paper_bgcolor="#1A1A1A",
    plot_bgcolor="#0F2015",
    font=dict(color="#CCCCCC", size=12, family="Arial"),
    title_font=dict(color="#39FF5A", size=16),
)

COLOR_SEQUENCE: list[str] = ["#39FF5A", "#004D54", "#2ECC71", "#CCCCCC"]


# ============================================================================
# 3. Funções auxiliares
# ============================================================================


def load_csv_to_staging(conn: sqlite3.Connection, csv_path: Path) -> int:
    """
    Carrega o CSV bruto para a tabela staging no SQLite.

    Args:
        conn: Conexão ativa com o banco SQLite.
        csv_path: Caminho absoluto do arquivo CSV.

    Returns:
        Quantidade de registros carregados.

    Raises:
        FileNotFoundError: CSV não encontrado no caminho informado.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV não encontrado: {csv_path}")

    df_bank_churn: pd.DataFrame = pd.read_csv(csv_path)
    df_bank_churn.to_sql("stg_bank_churn", conn, if_exists="replace", index=False)

    return len(df_bank_churn)


def execute_ddl_scripts(conn: sqlite3.Connection, ddl_dir: Path) -> list[str]:
    """
    Executa todos os scripts DDL do diretório de modelagem em ordem alfabética.

    Args:
        conn: Conexão ativa com o banco SQLite.
        ddl_dir: Diretório contendo os arquivos .sql de DDL.

    Returns:
        Lista com nomes dos scripts executados.

    Raises:
        FileNotFoundError: Diretório de DDL não encontrado.
    """
    if not ddl_dir.exists():
        raise FileNotFoundError(f"Diretório DDL não encontrado: {ddl_dir}")

    ddl_files: list[Path] = sorted(ddl_dir.glob("*.sql"))
    executed: list[str] = []

    for ddl_file in ddl_files:
        sql_script: str = ddl_file.read_text(encoding="utf-8")
        conn.executescript(sql_script)
        executed.append(ddl_file.name)
        print(f"  ✔ DDL executado: {ddl_file.name}")

    return executed


def parse_labeled_queries(queries_path: Path) -> dict[str, str]:
    """
    Lê o arquivo SQL e separa cada query pelo marcador '-- label: <nome>'.

    Args:
        queries_path: Caminho do arquivo .sql com as queries rotuladas.

    Returns:
        Dicionário {label: sql_query}.

    Raises:
        FileNotFoundError: Arquivo de queries não encontrado.
    """
    if not queries_path.exists():
        raise FileNotFoundError(f"Arquivo de queries não encontrado: {queries_path}")

    content: str = queries_path.read_text(encoding="utf-8")
    queries: dict[str, str] = {}
    current_label: str | None = None
    current_lines: list[str] = []

    for line in content.splitlines():
        stripped: str = line.strip()

        if stripped.startswith("-- label:"):
            # Salva a query anterior, se existir
            if current_label and current_lines:
                queries[current_label] = "\n".join(current_lines).strip()

            current_label = stripped.replace("-- label:", "").strip()
            current_lines = []
        elif current_label is not None:
            current_lines.append(line)

    # Última query
    if current_label and current_lines:
        queries[current_label] = "\n".join(current_lines).strip()

    return queries


def run_query(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    """
    Executa uma query SELECT e retorna o resultado como DataFrame.

    Args:
        conn: Conexão ativa com o banco SQLite.
        sql: String SQL da consulta.

    Returns:
        DataFrame com os resultados da query.
    """
    return pd.read_sql_query(sql, conn)


def save_figure(fig: go.Figure, filename: str, images_dir: Path) -> None:
    """
    Salva a figura como HTML interativo no diretório de imagens.

    Args:
        fig: Figura Plotly a ser salva.
        filename: Nome do arquivo (sem extensão).
        images_dir: Diretório de destino.
    """
    images_dir.mkdir(parents=True, exist_ok=True)
    filepath: Path = images_dir / f"{filename}.html"
    fig.write_html(str(filepath))
    print(f"  📊 Gráfico salvo: {filepath.name}")


# ============================================================================
# 4. Funções de visualização
# ============================================================================


def plot_churn_overview(df_visao_geral: pd.DataFrame) -> go.Figure:
    """
    Exibe gráfico de pizza com a proporção de churn vs retenção.

    Args:
        df_visao_geral: DataFrame com colunas total_churned e total_retidos.

    Returns:
        Figura Plotly.
    """
    labels: list[str] = ["Churned", "Retidos"]
    values: list[int] = [
        int(df_visao_geral["total_churned"].iloc[0]),
        int(df_visao_geral["total_retidos"].iloc[0]),
    ]

    fig: go.Figure = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=["#004D54", "#39FF5A"]),
                textinfo="label+percent",
                textfont=dict(color="#FFFFFF", size=13),
                hole=0.4,
            )
        ]
    )
    fig.update_layout(
        **LAYOUT_PADRAO,
        title="Proporção de Churn vs Retenção",
    )
    return fig


def plot_churn_by_category(
    df_data: pd.DataFrame,
    x_col: str,
    title: str,
    x_label: str,
) -> go.Figure:
    """
    Gráfico de barras da taxa de churn por categoria.

    Args:
        df_data: DataFrame com coluna de categoria e taxa_churn_pct.
        x_col: Nome da coluna categórica (eixo X).
        title: Título do gráfico.
        x_label: Rótulo amigável do eixo X.

    Returns:
        Figura Plotly.
    """
    fig: go.Figure = px.bar(
        df_data,
        x=x_col,
        y="taxa_churn_pct",
        title=title,
        labels={x_col: x_label, "taxa_churn_pct": "Taxa de Churn (%)"},
        color_discrete_sequence=["#39FF5A"],
        text="taxa_churn_pct",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(**LAYOUT_PADRAO)
    return fig


def plot_balance_comparison(df_saldo: pd.DataFrame) -> go.Figure:
    """
    Gráfico de barras agrupadas comparando saldo médio por status de churn.

    Args:
        df_saldo: DataFrame com status_churn e saldo_medio.

    Returns:
        Figura Plotly.
    """
    fig: go.Figure = px.bar(
        df_saldo,
        x="status_churn",
        y="saldo_medio",
        title="Saldo Médio por Status de Churn",
        labels={"status_churn": "Status", "saldo_medio": "Saldo Médio (€)"},
        color="status_churn",
        color_discrete_map={"Churned": "#004D54", "Retido": "#39FF5A"},
        text="saldo_medio",
    )
    fig.update_traces(texttemplate="€%{text:,.0f}", textposition="outside")
    fig.update_layout(**LAYOUT_PADRAO, showlegend=False)
    return fig


def plot_salary_comparison(df_salario: pd.DataFrame) -> go.Figure:
    """
    Gráfico de barras comparando salário médio estimado por status de churn.

    Args:
        df_salario: DataFrame com status_churn e salario_medio.

    Returns:
        Figura Plotly.
    """
    fig: go.Figure = px.bar(
        df_salario,
        x="status_churn",
        y="salario_medio",
        title="Salário Médio Estimado por Status de Churn",
        labels={"status_churn": "Status", "salario_medio": "Salário Médio (€)"},
        color="status_churn",
        color_discrete_map={"Churned": "#004D54", "Retido": "#39FF5A"},
        text="salario_medio",
    )
    fig.update_traces(texttemplate="€%{text:,.0f}", textposition="outside")
    fig.update_layout(**LAYOUT_PADRAO, showlegend=False)
    return fig


# ============================================================================
# 5. Pipeline principal
# ============================================================================


def main() -> None:
    """
    Pipeline completo: staging → DDL → queries → visualizações.
    """
    print("=" * 60)
    print("  BANCO ILUSÓRIO — EDA Bank Churn (SQL Pipeline)")
    print("=" * 60)

    # ---- 5.1 Conexão SQLite ------------------------------------------------
    conn: sqlite3.Connection = sqlite3.connect(str(DB_PATH))
    print(f"\n📂 Banco criado em: {DB_PATH.relative_to(PROJECT_ROOT)}")

    # ---- 5.2 Carga do CSV para staging -------------------------------------
    total_registros: int = load_csv_to_staging(conn, CSV_PATH)
    print(f"📥 CSV carregado: {total_registros} registros na staging")

    # ---- 5.3 Execução dos DDLs (modelo dimensional) ------------------------
    print("\n🏗️  Executando DDLs do modelo dimensional:")
    execute_ddl_scripts(conn, DDL_DIR)

    # ---- 5.4 Parsing e execução das queries de EDA -------------------------
    print("\n🔍 Executando queries de EDA:")
    queries: dict[str, str] = parse_labeled_queries(QUERIES_PATH)

    results: dict[str, pd.DataFrame] = {}
    for label, sql in queries.items():
        df_result: pd.DataFrame = run_query(conn, sql)
        results[label] = df_result
        print(f"  ✔ [{label}] → {len(df_result)} linhas")

    # ---- 5.5 Exibição dos resultados tabulares ------------------------------
    print("\n" + "=" * 60)
    print("  RESULTADOS DAS QUERIES")
    print("=" * 60)

    query_titles: dict[str, str] = {
        "visao_geral": "Q1 — Visão Geral do Dataset",
        "churn_por_geografia": "Q2 — Taxa de Churn por Geografia",
        "churn_por_genero": "Q3 — Taxa de Churn por Gênero",
        "churn_por_faixa_etaria": "Q4 — Taxa de Churn por Faixa Etária",
        "saldo_por_churn": "Q5 — Saldo por Status de Churn",
        "churn_por_produtos": "Q6 — Taxa de Churn por Nº de Produtos",
        "churn_membro_ativo": "Q7 — Churn: Membros Ativos vs Inativos",
        "churn_cartao_credito": "Q8 — Churn: Posse de Cartão de Crédito",
        "credit_score_por_churn": "Q9 — Churn por Faixa de Credit Score",
        "salario_por_churn": "Q10 — Salário Estimado por Status de Churn",
    }

    for label, df_result in results.items():
        title: str = query_titles.get(label, label)
        print(f"\n📋 {title}")
        print("-" * 50)
        print(df_result.to_string(index=False))

    # ---- 5.6 Visualizações Plotly -------------------------------------------
    print("\n" + "=" * 60)
    print("  GERANDO VISUALIZAÇÕES")
    print("=" * 60)

    # Gráfico 1 — Proporção geral de churn
    fig_overview: go.Figure = plot_churn_overview(results["visao_geral"])
    fig_overview.show()
    save_figure(fig_overview, "01_churn_overview", IMAGES_DIR)

    # Gráfico 2 — Churn por geografia
    fig_geo: go.Figure = plot_churn_by_category(
        results["churn_por_geografia"],
        x_col="pais",
        title="Taxa de Churn por País",
        x_label="País",
    )
    fig_geo.show()
    save_figure(fig_geo, "02_churn_por_geografia", IMAGES_DIR)

    # Gráfico 3 — Churn por gênero
    fig_gender: go.Figure = plot_churn_by_category(
        results["churn_por_genero"],
        x_col="genero",
        title="Taxa de Churn por Gênero",
        x_label="Gênero",
    )
    fig_gender.show()
    save_figure(fig_gender, "03_churn_por_genero", IMAGES_DIR)

    # Gráfico 4 — Churn por faixa etária
    fig_age: go.Figure = plot_churn_by_category(
        results["churn_por_faixa_etaria"],
        x_col="faixa_etaria",
        title="Taxa de Churn por Faixa Etária",
        x_label="Faixa Etária",
    )
    fig_age.show()
    save_figure(fig_age, "04_churn_por_faixa_etaria", IMAGES_DIR)

    # Gráfico 5 — Saldo médio por status de churn
    fig_balance: go.Figure = plot_balance_comparison(results["saldo_por_churn"])
    fig_balance.show()
    save_figure(fig_balance, "05_saldo_por_churn", IMAGES_DIR)

    # Gráfico 6 — Churn por número de produtos
    fig_products: go.Figure = plot_churn_by_category(
        results["churn_por_produtos"],
        x_col="qtd_produtos",
        title="Taxa de Churn por Nº de Produtos",
        x_label="Qtd. de Produtos",
    )
    fig_products.show()
    save_figure(fig_products, "06_churn_por_produtos", IMAGES_DIR)

    # Gráfico 7 — Churn: membros ativos vs inativos
    fig_active: go.Figure = plot_churn_by_category(
        results["churn_membro_ativo"],
        x_col="status_membro",
        title="Taxa de Churn — Membros Ativos vs Inativos",
        x_label="Status do Membro",
    )
    fig_active.show()
    save_figure(fig_active, "07_churn_membro_ativo", IMAGES_DIR)

    # Gráfico 8 — Churn por credit score
    fig_credit: go.Figure = plot_churn_by_category(
        results["credit_score_por_churn"],
        x_col="faixa_credit_score",
        title="Taxa de Churn por Faixa de Credit Score",
        x_label="Faixa de Credit Score",
    )
    fig_credit.show()
    save_figure(fig_credit, "08_churn_por_credit_score", IMAGES_DIR)

    # Gráfico 9 — Salário médio por status de churn
    fig_salary: go.Figure = plot_salary_comparison(results["salario_por_churn"])
    fig_salary.show()
    save_figure(fig_salary, "09_salario_por_churn", IMAGES_DIR)

    # ---- 5.7 Encerramento --------------------------------------------------
    conn.close()
    print("\n✅ Pipeline de EDA concluído com sucesso!")
    print(f"   Banco SQLite: {DB_PATH.relative_to(PROJECT_ROOT)}")
    print(f"   Gráficos em : {IMAGES_DIR.relative_to(PROJECT_ROOT)}/")


if __name__ == "__main__":
    main()
