-- Arquivo: 02_dim_customers.sql
-- Descrição: Dimensão de clientes — dados demográficos e financeiros do cliente
-- Data: 2026-04-05 | Autor: Banco Ilusório — Equipe de Dados

DROP TABLE IF EXISTS dim_customers;

CREATE TABLE dim_customers (
    customer_id       INTEGER PRIMARY KEY,
    surname           TEXT    NOT NULL,
    credit_score      INTEGER NOT NULL,
    gender            TEXT    NOT NULL,
    age               INTEGER NOT NULL,
    tenure            INTEGER NOT NULL,
    estimated_salary  REAL    NOT NULL
);

-- Carga a partir da tabela staging
INSERT INTO dim_customers (
    customer_id,
    surname,
    credit_score,
    gender,
    age,
    tenure,
    estimated_salary
)
SELECT
    CustomerId,
    Surname,
    CreditScore,
    Gender,
    Age,
    Tenure,
    EstimatedSalary
FROM stg_bank_churn;
