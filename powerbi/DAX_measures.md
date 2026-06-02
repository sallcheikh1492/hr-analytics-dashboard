# Mesures DAX — Dashboard RH

Table importée : **`hr_clean`** (depuis `data/processed/hr_clean.csv`).
Crée une table de mesures dédiée (`_Measures`) pour regrouper toutes les mesures.

> Astuce import : *Obtenir les données → Texte/CSV → `hr_clean.csv`*. Vérifie que
> `Salary`, `Age`, `TenureYears`, `EngagementSurvey`, `AbsenteeismRate`, `Absences`,
> `EmpSatisfaction`, `PerfScoreID`, `AttritionFlag`, `IsVoluntary`, `HighPerformer`
> sont bien typés en **nombre** (entier/décimal), et les colonnes `Date*` en **Date**.

---

## 1. Effectifs

```DAX
Effectif Total = COUNTROWS ( hr_clean )

Effectif Actif = CALCULATE ( COUNTROWS ( hr_clean ), hr_clean[AttritionFlag] = 0 )

Départs = CALCULATE ( COUNTROWS ( hr_clean ), hr_clean[AttritionFlag] = 1 )

Départs Volontaires = CALCULATE ( COUNTROWS ( hr_clean ), hr_clean[IsVoluntary] = 1 )
```

## 2. Attrition

```DAX
Taux d'Attrition % =
DIVIDE ( SUM ( hr_clean[AttritionFlag] ), COUNTROWS ( hr_clean ) )

Taux d'Attrition Volontaire % =
DIVIDE ( SUM ( hr_clean[IsVoluntary] ), COUNTROWS ( hr_clean ) )
```
> Formate les deux mesures en **Pourcentage**, 1 décimale.

## 3. Absentéisme

```DAX
Absences Moyennes = AVERAGE ( hr_clean[Absences] )

Taux d'Absentéisme % =
DIVIDE ( SUM ( hr_clean[Absences] ), COUNTROWS ( hr_clean ) * 261 )
-- 261 = jours ouvrés / an. Formate en pourcentage.
```

## 4. Satisfaction & engagement

```DAX
Satisfaction Moyenne = AVERAGE ( hr_clean[EmpSatisfaction] )      -- échelle 1-5

Engagement Moyen = AVERAGE ( hr_clean[EngagementSurvey] )         -- échelle 1-5
```

## 5. Performance

```DAX
Performance Moyenne = AVERAGE ( hr_clean[PerfScoreID] )           -- 1=PIP .. 4=Exceeds

% Hauts Performeurs =
DIVIDE (
    CALCULATE ( COUNTROWS ( hr_clean ), hr_clean[HighPerformer] = 1 ),
    COUNTROWS ( hr_clean )
)

% Sous-Performeurs =
DIVIDE (
    CALCULATE ( COUNTROWS ( hr_clean ), hr_clean[LowPerformer] = 1 ),
    COUNTROWS ( hr_clean )
)
```

## 6. Ancienneté, salaire, âge

```DAX
Ancienneté Moyenne = AVERAGE ( hr_clean[TenureYears] )

Salaire Annuel Moyen = AVERAGE ( hr_clean[Salary] )

Salaire Médian = MEDIAN ( hr_clean[Salary] )

Âge Moyen = AVERAGE ( hr_clean[Age] )
```

## 7. Mesures d'analyse avancée

```DAX
-- Écart de salaire entre partants et restants (insight clé)
Δ Salaire Partis vs Restés =
CALCULATE ( [Salaire Annuel Moyen], hr_clean[AttritionFlag] = 1 )
    - CALCULATE ( [Salaire Annuel Moyen], hr_clean[AttritionFlag] = 0 )

-- Attrition du segment vs attrition globale (pour repérer les segments à risque)
-- Version autonome : ne dépend d'aucune autre mesure (évite les erreurs de nom/apostrophe)
Indice de Risque Attrition =
VAR TauxSegment =
    DIVIDE ( SUM ( hr_clean[AttritionFlag] ), COUNTROWS ( hr_clean ) )
VAR TauxGlobal =
    CALCULATE (
        DIVIDE ( SUM ( hr_clean[AttritionFlag] ), COUNTROWS ( hr_clean ) ),
        ALL ( hr_clean )
    )
RETURN DIVIDE ( TauxSegment, TauxGlobal )   -- > 1 = segment plus risqué que la moyenne

-- Nb d'employés ACTIFS cumulant >= 3 facteurs de risque
-- Nom sans parenthèses + un seul FILTER (plus robuste qu'un CALCULATE multi-filtres)
Employés à Risque actifs =
COUNTROWS (
    FILTER (
        hr_clean,
        hr_clean[AttritionFlag] = 0
            && (
                IF ( hr_clean[Department] = "Production", 1, 0 )
                + IF ( hr_clean[TenureYears] <= 2, 1, 0 )
                + IF ( hr_clean[EmpSatisfaction] <= 3, 1, 0 )
                + IF ( hr_clean[SpecialProjectsCount] = 0, 1, 0 )
                + IF ( hr_clean[RecruitmentSource] IN { "Google Search", "Diversity Job Fair" }, 1, 0 )
            ) >= 3
    )
)
```

## 8. Titres dynamiques (optionnel)

```DAX
-- Version autonome (ne référence aucune autre mesure -> évite les erreurs de nom/apostrophe)
Titre Attrition =
VAR Departs = CALCULATE ( COUNTROWS ( hr_clean ), hr_clean[AttritionFlag] = 1 )
VAR Effectif = COUNTROWS ( hr_clean )
VAR Taux = DIVIDE ( Departs, Effectif )
RETURN
    "Taux d'attrition : " & FORMAT ( Taux, "0.0%" )
        & "  |  " & Departs & " départs sur " & Effectif & " employés"
```

---

### Colonne calculée recommandée (si pas déjà dans le CSV)
Le CSV contient déjà `AgeBand`, `TenureBand`, `SalaryBand`. Si tu veux une table de dates :

```DAX
Calendrier =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2006, 1, 1 ), DATE ( 2020, 12, 31 ) ),
    "Année", YEAR ( [Date] ),
    "Mois", FORMAT ( [Date], "MMM" ),
    "N° Mois", MONTH ( [Date] )
)
```
Relie `Calendrier[Date]` à `hr_clean[DateofHire]` (et/ou crée une relation inactive
vers `DateofTermination` activée via `USERELATIONSHIP` pour analyser les départs dans le temps).
