-- ============================================================================
-- 03_kpis.sql — Indicateurs RH (KPI) globaux
-- ============================================================================

-- 1) Tableau de bord des KPI principaux (une seule ligne récapitulative)
SELECT
    COUNT(*)                                               AS effectif_total,
    COUNT(*) FILTER (WHERE attrition_flag = 0)             AS effectif_actif,
    COUNT(*) FILTER (WHERE attrition_flag = 1)             AS departs,
    ROUND(AVG(attrition_flag) * 100, 1)                    AS taux_attrition_pct,
    ROUND(AVG(is_voluntary)  * 100, 1)                     AS taux_attrition_volontaire_pct,
    ROUND(AVG(absenteeism_rate), 2)                        AS taux_absenteisme_pct,
    ROUND(AVG(absences), 1)                                AS absences_moyennes,
    ROUND(AVG(emp_satisfaction), 2)                        AS satisfaction_moy,
    ROUND(AVG(engagement_survey), 2)                       AS engagement_moy,
    ROUND(AVG(high_performer) * 100, 1)                    AS pct_hauts_performeurs,
    ROUND(AVG(tenure_years), 1)                            AS anciennete_moy_ans,
    ROUND(AVG(salary))                                     AS salaire_annuel_moy,
    ROUND(AVG(age), 1)                                     AS age_moy
FROM employees;

-- 2) Taux d'attrition global (format simple)
SELECT
    ROUND(100.0 * SUM(attrition_flag) / COUNT(*), 1) AS taux_attrition_global_pct
FROM employees;

-- 3) Répartition Actifs / Volontaires / Pour faute
SELECT employment_status,
       COUNT(*)                                       AS effectif,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM employees
GROUP BY employment_status
ORDER BY effectif DESC;
