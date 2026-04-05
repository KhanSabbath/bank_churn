-- Arquivo: 03_fact_bank_churn.sql
-- Descrição: Tabela fato de churn bancário — métricas de produto, atividade e evasão
-- Data: 2026-04-05 | Autor: Banco Ilusório — Equipe de Dados

DROP TABLE IF EXISTS fact_bank_churn;

CREATE TABLE fact_bank_churn (
    customer_id       INTEGER NOT NULL,
    geography_id      INTEGER NOT NULL,
    balance           REAL    NOT NULL,
    num_of_products   INTEGER NOT NULL,
    has_credit_card   INTEGER NOT NULL CHECK (has_credit_card IN (0, 1)),
    is_active_member  INTEGER NOT NULL CHECK (is_active_member IN (0, 1)),
    exited            INTEGER NOT NULL CHECK (exited IN (0, 1)),
    PRIMARY KEY (customer_id),
    FOREIGN KEY (customer_id)  REFERENCES dim_customers(customer_id),
    FOREIGN KEY (geography_id) REFERENCES dim_geography(geography_id)
);

-- Índices para consultas analíticas frequentes
CREATE INDEX idx_fact_churn_geography ON fact_bank_churn(geography_id);
CREATE INDEX idx_fact_churn_exited    ON fact_bank_churn(exited);

-- Carga a partir da staging + lookup na dimensão de geografia
INSERT INTO fact_bank_churn (
    customer_id,
    geography_id,
    balance,
    num_of_products,
    has_credit_card,
    is_active_member,
    exited
)
SELECT
    s.CustomerId,
    g.geography_id,
    s.Balance,
    s.NumOfProducts,
    s.HasCrCard,
    s.IsActiveMember,
    s.Exited
FROM stg_bank_churn  s
INNER JOIN dim_geography g ON s.Geography = g.geography_name;
