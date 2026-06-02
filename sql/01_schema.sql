-- ============================================================================
-- Projet BI : Dashboard RH - Analyse des employés
-- Fichier   : 01_schema.sql  (PostgreSQL 13+)
-- Rôle      : Création de la table cible `employees`
-- ============================================================================

DROP TABLE IF EXISTS employees CASCADE;

CREATE TABLE employees (
    emp_id                  INTEGER PRIMARY KEY,
    employee_name           VARCHAR(120),
    gender_label            VARCHAR(10),          -- Homme / Femme
    sex                     CHAR(1),              -- M / F
    marital_desc            VARCHAR(20),
    age                     SMALLINT,
    age_band                VARCHAR(10),          -- <30 / 30-39 / 40-49 / 50+
    race_desc               VARCHAR(50),
    hispanic_latino         VARCHAR(5),
    citizen_desc            VARCHAR(30),
    state                   CHAR(2),
    department              VARCHAR(40),
    position                VARCHAR(60),
    manager_name            VARCHAR(80),
    recruitment_source      VARCHAR(40),
    salary                  INTEGER,              -- salaire annuel ($)
    monthly_income          INTEGER,
    salary_band             VARCHAR(10),
    date_of_hire            DATE,
    date_of_termination     DATE,                 -- NULL = employé actif
    tenure_years            NUMERIC(5,2),
    tenure_band             VARCHAR(10),
    employment_status       VARCHAR(30),          -- Active / Voluntarily Terminated / Terminated for Cause
    term_reason             VARCHAR(40),
    attrition               VARCHAR(3),           -- Yes / No
    attrition_flag          SMALLINT,             -- 1 = parti, 0 = actif
    is_voluntary            SMALLINT,
    emp_satisfaction        SMALLINT,             -- 1..5
    engagement_survey       NUMERIC(4,2),         -- 1..5
    performance_score       VARCHAR(20),          -- PIP / Needs Improvement / Fully Meets / Exceeds
    perf_score_id           SMALLINT,
    high_performer          SMALLINT,
    low_performer           SMALLINT,
    special_projects_count  SMALLINT,
    days_late_last30        SMALLINT,
    absences                SMALLINT,
    absenteeism_rate        NUMERIC(5,2),         -- proxy = absences / 261 jours ouvrés (%)
    last_perf_review_date   DATE
);

-- Index utiles pour les requêtes analytiques
CREATE INDEX idx_emp_department  ON employees (department);
CREATE INDEX idx_emp_attrition   ON employees (attrition_flag);
CREATE INDEX idx_emp_position    ON employees (position);

COMMENT ON TABLE employees IS 'Table RH nettoyée (HRDataset_v14) - 311 employés';
