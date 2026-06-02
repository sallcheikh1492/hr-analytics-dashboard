-- ============================================================================
-- 02_load.sql  — Chargement des données nettoyées dans la table employees
-- ============================================================================
-- Le fichier source est data/processed/hr_clean.csv (généré par le notebook /
-- scripts/clean_data.py). L'ordre des colonnes du CSV correspond exactement
-- à l'ordre ci-dessous.
--
-- Option A (recommandée) — exécuter depuis psql, côté client :
--   \copy ... FROM 'chemin/vers/hr_clean.csv' ...
--   (pas besoin de droits superuser, le chemin est résolu côté client)
--
-- Option B — COPY côté serveur (nécessite que le serveur lise le fichier) :
--   COPY employees (...) FROM '/chemin/absolu/hr_clean.csv' ...
-- ============================================================================

-- Adaptez le chemin ci-dessous puis exécutez ce bloc dans psql :

\copy employees ( \
    emp_id, employee_name, gender_label, sex, marital_desc, age, age_band, \
    race_desc, hispanic_latino, citizen_desc, state, department, position, \
    manager_name, recruitment_source, salary, monthly_income, salary_band, \
    date_of_hire, date_of_termination, tenure_years, tenure_band, \
    employment_status, term_reason, attrition, attrition_flag, is_voluntary, \
    emp_satisfaction, engagement_survey, performance_score, perf_score_id, \
    high_performer, low_performer, special_projects_count, days_late_last30, \
    absences, absenteeism_rate, last_perf_review_date \
) FROM 'data/processed/hr_clean.csv' WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- Contrôles post-chargement
SELECT COUNT(*) AS nb_lignes FROM employees;                 -- attendu : 311
SELECT COUNT(*) FILTER (WHERE attrition_flag = 1) AS departs,
       COUNT(*) FILTER (WHERE date_of_termination IS NULL) AS actifs
FROM employees;                                              -- attendu : 104 / 207
