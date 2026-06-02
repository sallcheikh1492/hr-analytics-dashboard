# Guide de construction du Dashboard Power BI — RH

Objectif : un rapport interactif de 3 pages à partir de `data/processed/hr_clean.csv`.
Temps estimé : ~30-45 min. Aucune compétence avancée requise.

---

## Étape 0 — Préparation
1. Ouvre **Power BI Desktop** (gratuit).
2. *Accueil → Obtenir les données → Texte/CSV* → sélectionne
   `data/processed/hr_clean.csv` → **Charger**.
3. Dans *Affichage des données*, vérifie les types :
   - Entiers : `EmpID`, `Age`, `Salary`, `MonthlyIncome`, `EmpSatisfaction`,
     `PerfScoreID`, `AttritionFlag`, `IsVoluntary`, `HighPerformer`, `LowPerformer`,
     `SpecialProjectsCount`, `DaysLateLast30`, `Absences`
   - Décimaux : `TenureYears`, `EngagementSurvey`, `AbsenteeismRate`
   - Dates : `DateofHire`, `DateofTermination`, `LastPerformanceReview_Date`
   - Texte : tout le reste
4. Crée les **mesures** du fichier [`DAX_measures.md`](DAX_measures.md)
   (*Nouvelle mesure* pour chacune). Regroupe-les dans une table vide `_Measures`.

---

## Page 1 — Vue d'ensemble (Executive Summary)

### Bandeau de KPI (cartes)
Insère 5 visuels **Carte** alignés en haut :

| Carte | Mesure | Format |
|-------|--------|--------|
| Effectif total | `Effectif Total` | nombre entier |
| Taux d'attrition | `Taux d'Attrition %` | % 1 déc. |
| Taux d'absentéisme | `Taux d'Absentéisme %` | % 1 déc. |
| Satisfaction moyenne | `Satisfaction Moyenne` | 0.0 |
| Performance moyenne | `Performance Moyenne` | 0.0 |

### Visuels
1. **Effectif par département** — *Graphique à barres empilées (horizontal)*
   - Axe Y : `Department` · Valeur : `Effectif Total`
2. **Attrition par département** — *Histogramme groupé*
   - Axe X : `Department` · Valeur : `Taux d'Attrition %` · tri décroissant
3. **Attrition par tranche d'âge** — *Histogramme*
   - Axe X : `AgeBand` (trier <30 → 50+) · Valeur : `Taux d'Attrition %`
4. **Attrition par ancienneté** — *Histogramme* (le signal le plus fort)
   - Axe X : `TenureBand` · Valeur : `Taux d'Attrition %`
5. **Répartition Attrition** — *Anneau (Donut)*
   - Légende : `Attrition` · Valeur : `Effectif Total`

---

## Page 2 — Facteurs de départ

1. **Attrition par source de recrutement** — *Barres horizontales*
   - Axe Y : `RecruitmentSource` · Valeur : `Taux d'Attrition %` · tri décroissant
   - 💡 Insight : Google Search ~61 %, Diversity Job Fair ~55 % vs Website ~8 %
2. **Attrition par manager** — *Barres horizontales*
   - Axe Y : `ManagerName` · Valeur : `Taux d'Attrition %`
   - Filtre visuel : `Effectif Total >= 8`
3. **Salaire vs attrition** — *Graphique en aires / boîte à moustaches (visuel custom)*
   - ou *Histogramme* : Axe `Attrition` · Valeur `Salaire Annuel Moyen`
4. **Impact des projets spéciaux (proxy heures sup.)** — *Histogramme*
   - Axe X : `SpecialProjectsCount` · Valeur : `Taux d'Attrition %`
5. **Satisfaction par département** — *Histogramme groupé*
   - Axe X : `Department` · Valeurs : `Satisfaction Moyenne`, `Engagement Moyen`
6. **Carte "Employés à Risque (actifs)"** — mesure `Employés à Risque (actifs)`

---

## Page 3 — Absentéisme & Performance

1. **Heatmap absentéisme** — *Matrice* avec mise en forme conditionnelle
   - Lignes : `Department` · Colonnes : `AgeBand` · Valeurs : `Absences Moyennes`
   - *Mise en forme conditionnelle → Couleur d'arrière-plan* (dégradé jaune→rouge)
2. **Répartition des performances** — *Histogramme*
   - Axe X : `PerformanceScore` (ordre PIP → Exceeds) · Valeur : `Effectif Total`
3. **Performance par poste** — *Barres horizontales*
   - Axe Y : `Position` · Valeur : `Performance Moyenne` · filtre effectif ≥ 4
4. **Absentéisme vs Jours de retard** — *Nuage de points*
   - X : `Absences` · Y : `DaysLateLast30` · taille : `Effectif Total`

---

## Filtres (Slicers) — sur toutes les pages
Ajoute un bandeau latéral de segments (*Slicer*) puis
*Format → Synchroniser les segments* sur les 3 pages :

| Slicer | Champ |
|--------|-------|
| Département | `Department` |
| Sexe | `GenderLabel` |
| Tranche d'âge | `AgeBand` |
| Poste | `Position` |
| Ancienneté | `TenureBand` |
| Statut | `EmploymentStatus` |

> ⚠️ Les filtres « Niveau d'éducation » et « Distance domicile-travail » du brief ne sont
> **pas disponibles** dans ce dataset. Remplacés ici par `TenureBand` et `RecruitmentSource`,
> plus pertinents au vu de l'analyse.

---

## Mise en forme & thème
- **Palette** : bleu `#2E86AB` (neutre) + orange/rouge `#E4572E` (attrition / alerte).
- *Affichage → Thèmes* : choisis un thème sobre, applique des titres en gras.
- Ajoute un **titre de rapport** « Dashboard RH — Analyse des employés » et la source des données en pied de page.
- Active les **info-bulles** (tooltips) et l'**exploration croisée** (cross-filtering) entre visuels.

## Export & publication
- *Fichier → Enregistrer* sous `powerbi/HR_Dashboard.pbix`.
- *Publier* sur Power BI Service (compte gratuit) pour obtenir un lien partageable à mettre dans le README / CV.
- *Fichier → Exporter → PDF* pour une capture statique dans `reports/`.
