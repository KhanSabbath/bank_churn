-- Arquivo: 01_eda_bank_churn.sql
-- Descrição: Queries analíticas de EDA sobre o modelo dimensional de churn bancário
-- Data: 2026-04-05 | Autor: Banco Ilusório — Equipe de Dados
-- ============================================================================


-- ---------------------------------------------------------------------------
-- Q1 — Visão geral do dataset: total de clientes, taxa de churn global
-- ---------------------------------------------------------------------------
-- label: visao_geral
SELECT
    COUNT(f.customer_id)                                    AS total_clientes,
    SUM(f.exited)                                           AS total_churned,
    COUNT(f.customer_id) - SUM(f.exited)                    AS total_retidos,
    ROUND(SUM(f.exited) * 100.0 / COUNT(f.customer_id), 2) AS taxa_churn_pct
FROM fact_bank_churn f;


-- ---------------------------------------------------------------------------
-- Q2 — Taxa de churn por geografia
-- ---------------------------------------------------------------------------
-- label: churn_por_geografia
SELECT
    g.geography_name                                        AS pais,
    COUNT(f.customer_id)                                    AS total_clientes,
    SUM(f.exited)                                           AS total_churned,
    ROUND(SUM(f.exited) * 100.0 / COUNT(f.customer_id), 2) AS taxa_churn_pct
FROM fact_bank_churn f
INNER JOIN dim_geography g ON f.geography_id = g.geography_id
GROUP BY g.geography_name
ORDER BY taxa_churn_pct DESC;


-- ---------------------------------------------------------------------------
-- Q3 — Taxa de churn por gênero
-- ---------------------------------------------------------------------------
-- label: churn_por_genero
SELECT
    c.gender                                                AS genero,
    COUNT(f.customer_id)                                    AS total_clientes,
    SUM(f.exited)                                           AS total_churned,
    ROUND(SUM(f.exited) * 100.0 / COUNT(f.customer_id), 2) AS taxa_churn_pct
FROM fact_bank_churn f
INNER JOIN dim_customers c ON f.customer_id = c.customer_id
GROUP BY c.gender
ORDER BY taxa_churn_pct DESC;


-- ---------------------------------------------------------------------------
-- Q4 — Taxa de churn por faixa etária
-- ---------------------------------------------------------------------------
-- label: churn_por_faixa_etaria
SELECT
    CASE
        WHEN c.age < 30              THEN '18-29'
        WHEN c.age BETWEEN 30 AND 39 THEN '30-39'
        WHEN c.age BETWEEN 40 AND 49 THEN '40-49'
        WHEN c.age BETWEEN 50 AND 59 THEN '50-59'
        ELSE '60+'
    END                                                     AS faixa_etaria,
    COUNT(f.customer_id)                                    AS total_clientes,
    SUM(f.exited)                                           AS total_churned,
    ROUND(SUM(f.exited) * 100.0 / COUNT(f.customer_id), 2) AS taxa_churn_pct
FROM fact_bank_churn f
INNER JOIN dim_customers c ON f.customer_id = c.customer_id
GROUP BY faixa_etaria
ORDER BY faixa_etaria;


-- ---------------------------------------------------------------------------
-- Q5 — Estatísticas de saldo por status de churn
-- ---------------------------------------------------------------------------
-- label: saldo_por_churn
SELECT
    CASE f.exited WHEN 1 THEN 'Churned' ELSE 'Retido' END AS status_churn,
    COUNT(f.customer_id)                                    AS total_clientes,
    ROUND(AVG(f.balance), 2)                                AS saldo_medio,
    ROUND(MIN(f.balance), 2)                                AS saldo_minimo,
    ROUND(MAX(f.balance), 2)                                AS saldo_maximo
FROM fact_bank_churn f
GROUP BY f.exited
ORDER BY f.exited;


-- ---------------------------------------------------------------------------
-- Q6 — Taxa de churn por quantidade de produtos contratados
-- ---------------------------------------------------------------------------
-- label: churn_por_produtos
SELECT
    f.num_of_products                                       AS qtd_produtos,
    COUNT(f.customer_id)                                    AS total_clientes,
    SUM(f.exited)                                           AS total_churned,
    ROUND(SUM(f.exited) * 100.0 / COUNT(f.customer_id), 2) AS taxa_churn_pct
FROM fact_bank_churn f
GROUP BY f.num_of_products
ORDER BY f.num_of_products;


-- ---------------------------------------------------------------------------
-- Q7 — Taxa de churn: membros ativos vs inativos
-- ---------------------------------------------------------------------------
-- label: churn_membro_ativo
SELECT
    CASE f.is_active_member
        WHEN 1 THEN 'Ativo'
        ELSE 'Inativo'
    END                                                     AS status_membro,
    COUNT(f.customer_id)                                    AS total_clientes,
    SUM(f.exited)                                           AS total_churned,
    ROUND(SUM(f.exited) * 100.0 / COUNT(f.customer_id), 2) AS taxa_churn_pct
FROM fact_bank_churn f
GROUP BY f.is_active_member
ORDER BY taxa_churn_pct DESC;


-- ---------------------------------------------------------------------------
-- Q8 — Taxa de churn: posse de cartão de crédito
-- ---------------------------------------------------------------------------
-- label: churn_cartao_credito
SELECT
    CASE f.has_credit_card
        WHEN 1 THEN 'Com cartão'
        ELSE 'Sem cartão'
    END                                                     AS posse_cartao,
    COUNT(f.customer_id)                                    AS total_clientes,
    SUM(f.exited)                                           AS total_churned,
    ROUND(SUM(f.exited) * 100.0 / COUNT(f.customer_id), 2) AS taxa_churn_pct
FROM fact_bank_churn f
GROUP BY f.has_credit_card
ORDER BY taxa_churn_pct DESC;


-- ---------------------------------------------------------------------------
-- Q9 — Distribuição de credit score por faixa e status de churn
-- ---------------------------------------------------------------------------
-- label: credit_score_por_churn
SELECT
    CASE
        WHEN c.credit_score < 500              THEN '< 500'
        WHEN c.credit_score BETWEEN 500 AND 599 THEN '500-599'
        WHEN c.credit_score BETWEEN 600 AND 699 THEN '600-699'
        WHEN c.credit_score BETWEEN 700 AND 799 THEN '700-799'
        ELSE '800+'
    END                                                     AS faixa_credit_score,
    COUNT(f.customer_id)                                    AS total_clientes,
    SUM(f.exited)                                           AS total_churned,
    ROUND(SUM(f.exited) * 100.0 / COUNT(f.customer_id), 2) AS taxa_churn_pct
FROM fact_bank_churn f
INNER JOIN dim_customers c ON f.customer_id = c.customer_id
GROUP BY faixa_credit_score
ORDER BY faixa_credit_score;


-- ---------------------------------------------------------------------------
-- Q10 — Estatísticas de salário estimado por status de churn
-- ---------------------------------------------------------------------------
-- label: salario_por_churn
SELECT
    CASE f.exited WHEN 1 THEN 'Churned' ELSE 'Retido' END AS status_churn,
    ROUND(AVG(c.estimated_salary), 2)                       AS salario_medio,
    ROUND(MIN(c.estimated_salary), 2)                       AS salario_minimo,
    ROUND(MAX(c.estimated_salary), 2)                       AS salario_maximo
FROM fact_bank_churn f
INNER JOIN dim_customers c ON f.customer_id = c.customer_id
GROUP BY f.exited
ORDER BY f.exited;
