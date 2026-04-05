-- Arquivo: 01_dim_geography.sql
-- Descrição: Dimensão de geografia — países onde o banco opera
-- Data: 2026-04-05 | Autor: Banco Ilusório — Equipe de Dados

DROP TABLE IF EXISTS dim_geography;

CREATE TABLE dim_geography (
    geography_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    geography_name  TEXT    NOT NULL UNIQUE
);

-- Carga a partir de valores distintos da tabela staging
INSERT INTO dim_geography (geography_name)
SELECT DISTINCT Geography
FROM stg_bank_churn
ORDER BY Geography;
