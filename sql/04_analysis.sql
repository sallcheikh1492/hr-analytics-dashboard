-- ============================================================================
-- 04_analysis.sql — Requêtes d'analyse (causes du turnover, facteurs de départ)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- A. Départements avec le plus de départs / plus fort taux d'attrition
-- ----------------------------------------------------------------------------
SELECT department,
       COUNT(*)                                   AS effectif,
       SUM(attrition_flag)                        AS departs,
       ROUND(100.0 * SUM(attrition_flag) / COUNT(*), 1) AS taux_attrition_pct
FROM employees
GROUP BY department
ORDER BY taux_attrition_pct DESC;

-- ----------------------------------------------------------------------------
-- B. Impact de l'implication (proxy heures sup. = projets spéciaux)
-- ----------------------------------------------------------------------------
SELECT CASE WHEN special_projects_count = 0 THEN '0 projet'
            ELSE '1+ projet' END                  AS implication,
       COUNT(*)                                   AS effectif,
       ROUND(100.0 * AVG(attrition_flag), 1)      AS taux_attrition_pct
FROM employees
GROUP BY 1
ORDER BY taux_attrition_pct DESC;

-- ----------------------------------------------------------------------------
-- C. Satisfaction & engagement moyens par département
-- ----------------------------------------------------------------------------
SELECT department,
       ROUND(AVG(emp_satisfaction), 2)            AS satisfaction_moy,
       ROUND(AVG(engagement_survey), 2)           AS engagement_moy,
       ROUND(100.0 * AVG(attrition_flag), 1)      AS taux_attrition_pct
FROM employees
GROUP BY department
ORDER BY satisfaction_moy ASC;

-- ----------------------------------------------------------------------------
-- D. Performance selon les postes (top 12 par effectif)
-- ----------------------------------------------------------------------------
SELECT position,
       COUNT(*)                                   AS effectif,
       ROUND(AVG(perf_score_id), 2)               AS perf_moy_id,        -- 1=PIP .. 4=Exceeds
       ROUND(100.0 * AVG(high_performer), 1)      AS pct_exceeds,
       ROUND(100.0 * AVG(low_performer), 1)       AS pct_sous_perf
FROM employees
GROUP BY position
HAVING COUNT(*) >= 4
ORDER BY perf_moy_id DESC;

-- ----------------------------------------------------------------------------
-- E. Absentéisme par tranche d'âge et département
-- ----------------------------------------------------------------------------
SELECT department, age_band,
       COUNT(*)                                   AS effectif,
       ROUND(AVG(absences), 1)                    AS absences_moy,
       ROUND(AVG(absenteeism_rate), 2)            AS taux_absenteisme_pct
FROM employees
GROUP BY department, age_band
ORDER BY department, age_band;

-- ----------------------------------------------------------------------------
-- F. Attrition par ancienneté (signal le plus fort)
-- ----------------------------------------------------------------------------
SELECT tenure_band,
       COUNT(*)                                   AS effectif,
       SUM(attrition_flag)                        AS departs,
       ROUND(100.0 * AVG(attrition_flag), 1)      AS taux_attrition_pct
FROM employees
GROUP BY tenure_band
ORDER BY CASE tenure_band
            WHEN '0-2 ans' THEN 1 WHEN '3-5 ans' THEN 2
            WHEN '6-8 ans' THEN 3 ELSE 4 END;

-- ----------------------------------------------------------------------------
-- G. Attrition par source de recrutement (prédicteur fort)
-- ----------------------------------------------------------------------------
SELECT recruitment_source,
       COUNT(*)                                   AS effectif,
       ROUND(100.0 * AVG(attrition_flag), 1)      AS taux_attrition_pct
FROM employees
GROUP BY recruitment_source
HAVING COUNT(*) >= 10
ORDER BY taux_attrition_pct DESC;

-- ----------------------------------------------------------------------------
-- H. Managers les plus exposés (>= 8 employés gérés)
-- ----------------------------------------------------------------------------
SELECT manager_name,
       COUNT(*)                                   AS equipe,
       SUM(attrition_flag)                        AS departs,
       ROUND(100.0 * AVG(attrition_flag), 1)      AS taux_attrition_pct
FROM employees
GROUP BY manager_name
HAVING COUNT(*) >= 8
ORDER BY taux_attrition_pct DESC;

-- ----------------------------------------------------------------------------
-- I. Salaire moyen : restés vs partis
-- ----------------------------------------------------------------------------
SELECT attrition,
       COUNT(*)                                   AS effectif,
       ROUND(AVG(salary))                         AS salaire_moy,
       ROUND(AVG(tenure_years), 1)                AS anciennete_moy
FROM employees
GROUP BY attrition;

-- ----------------------------------------------------------------------------
-- J. Profils à risque — score composite (départements/sources/ancienneté)
--    Liste des employés ACTIFS cumulant le plus de facteurs de risque
-- ----------------------------------------------------------------------------
SELECT emp_id, employee_name, department, position, manager_name,
       tenure_years, emp_satisfaction, special_projects_count, recruitment_source,
       ( (department = 'Production')::int
       + (tenure_years <= 2)::int
       + (emp_satisfaction <= 3)::int
       + (special_projects_count = 0)::int
       + (recruitment_source IN ('Google Search','Diversity Job Fair'))::int
       ) AS risk_score
FROM employees
WHERE attrition_flag = 0                              -- uniquement les actifs
ORDER BY risk_score DESC, tenure_years ASC
LIMIT 20;

-- ----------------------------------------------------------------------------
-- K. Top motifs de départ (employés partis)
-- ----------------------------------------------------------------------------
SELECT term_reason,
       COUNT(*)                                   AS nb
FROM employees
WHERE attrition_flag = 1
GROUP BY term_reason
ORDER BY nb DESC;
