"""
HR Analytics - Pipeline de nettoyage et de préparation des données
==================================================================
Projet BI : Dashboard RH - Analyse des employés
Source    : HRDataset_v14.csv (Kaggle - rhuebner/human-resources-data-set)

Ce script :
  1. Charge le dataset brut
  2. Nettoie (types, doublons, casse, valeurs manquantes, aberrantes)
  3. Crée les variables dérivées (Age, Ancienneté, tranches, Attrition...)
  4. Exporte un jeu de données propre prêt pour SQL et Power BI
  5. Génère les KPI RH et les figures du rapport

Usage : python scripts/clean_data.py
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "HRDataset_v14.csv"
OUT_DIR = ROOT / "data" / "processed"
FIG_DIR = ROOT / "reports" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Date de référence pour le calcul de l'âge et de l'ancienneté.
# Le dataset couvre une période qui se termine fin 2018 / 2019
# (dernières évaluations de performance en 2019).
ANALYSIS_DATE = pd.Timestamp("2019-12-31")

sns.set_theme(style="whitegrid")
PALETTE = {"No": "#2E86AB", "Yes": "#E4572E"}
plt.rcParams["figure.dpi"] = 110
plt.rcParams["savefig.bbox"] = "tight"
plt.rcParams["axes.titleweight"] = "bold"


def savefig(name: str):
    plt.savefig(FIG_DIR / name, dpi=130)
    plt.close()


# --------------------------------------------------------------------------- #
# 1. Chargement
# --------------------------------------------------------------------------- #
def load_raw() -> pd.DataFrame:
    # encoding utf-8-sig : le fichier commence par un BOM
    df = pd.read_csv(RAW_PATH, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    print(f"[1] Chargement       : {df.shape[0]} lignes x {df.shape[1]} colonnes")
    return df


# --------------------------------------------------------------------------- #
# 2. Nettoyage
# --------------------------------------------------------------------------- #
def parse_dob(series: pd.Series) -> pd.Series:
    """DOB au format m/d/yy ; corrige le bug du siècle (ex. 83 -> 1983, pas 2083)."""
    dob = pd.to_datetime(series, format="%m/%d/%y", errors="coerce")
    # toute date future doit être ramenée 100 ans en arrière
    future = dob > ANALYSIS_DATE
    dob.loc[future] = dob.loc[future] - pd.offsets.DateOffset(years=100)
    return dob


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 2.1 Doublons -----------------------------------------------------------
    before = len(df)
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["EmpID"], keep="first")
    print(f"[2] Doublons         : {before - len(df)} supprimé(s)")

    # 2.2 Nettoyage des chaînes (espaces superflus) --------------------------
    str_cols = df.select_dtypes(include="object").columns
    for c in str_cols:
        df[c] = df[c].astype(str).str.strip()
        df[c] = df[c].replace({"nan": np.nan})

    # 2.3 Uniformisation des catégories --------------------------------------
    df["HispanicLatino"] = df["HispanicLatino"].str.capitalize()  # no/No -> No
    df["Sex"] = df["Sex"].str.upper().str.strip()
    df["GenderLabel"] = df["Sex"].map({"M": "Homme", "F": "Femme"})

    # 2.4 Conversion des dates -----------------------------------------------
    df["DOB"] = parse_dob(df["DOB"])
    for c in ["DateofHire", "DateofTermination", "LastPerformanceReview_Date"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")

    # 2.5 Valeurs manquantes -------------------------------------------------
    # DateofTermination NaN = employé toujours actif -> normal, on garde NaT
    # ManagerID NaN -> -1 (inconnu)
    df["ManagerID"] = df["ManagerID"].fillna(-1).astype(int)
    n_nat_term = df["DateofTermination"].isna().sum()
    print(f"    Valeurs manquantes DateofTermination (=actifs) : {n_nat_term}")

    return df


# --------------------------------------------------------------------------- #
# 3. Variables dérivées
# --------------------------------------------------------------------------- #
def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Attrition (cible) -------------------------------------------------------
    df["Attrition"] = np.where(df["Termd"] == 1, "Yes", "No")
    df["AttritionFlag"] = df["Termd"].astype(int)
    df["IsVoluntary"] = (df["EmploymentStatus"] == "Voluntarily Terminated").astype(int)

    # Age --------------------------------------------------------------------
    df["Age"] = ((ANALYSIS_DATE - df["DOB"]).dt.days / 365.25).round().astype("Int64")

    # Ancienneté (tenure) : actif -> jusqu'à ANALYSIS_DATE ; parti -> jusqu'au départ
    end = df["DateofTermination"].fillna(ANALYSIS_DATE)
    df["TenureYears"] = ((end - df["DateofHire"]).dt.days / 365.25).round(2)

    # Salaire annuel / mensuel ----------------------------------------------
    df["MonthlyIncome"] = (df["Salary"] / 12).round(0).astype(int)

    # Absentéisme : taux proxy = jours d'absence / 261 jours ouvrés ----------
    df["AbsenteeismRate"] = (df["Absences"] / 261 * 100).round(2)

    # Tranches ---------------------------------------------------------------
    df["AgeBand"] = pd.cut(
        df["Age"].astype(float),
        bins=[0, 29, 39, 49, 200],
        labels=["<30", "30-39", "40-49", "50+"],
    )
    df["TenureBand"] = pd.cut(
        df["TenureYears"],
        bins=[-0.1, 2, 5, 8, 100],
        labels=["0-2 ans", "3-5 ans", "6-8 ans", "9+ ans"],
    )
    df["SalaryBand"] = pd.cut(
        df["Salary"],
        bins=[0, 55000, 70000, 90000, 1e9],
        labels=["<55k", "55-70k", "70-90k", "90k+"],
    )

    # Satisfaction / performance lisibles ------------------------------------
    df["SatisfactionLabel"] = df["EmpSatisfaction"].map(
        {1: "1-Très faible", 2: "2-Faible", 3: "3-Moyenne", 4: "4-Bonne", 5: "5-Excellente"}
    )
    df["HighPerformer"] = df["PerformanceScore"].isin(["Exceeds"]).astype(int)
    df["LowPerformer"] = df["PerformanceScore"].isin(["PIP", "Needs Improvement"]).astype(int)

    return df


# --------------------------------------------------------------------------- #
# 4. Détection des valeurs aberrantes (rapport, pas de suppression)
# --------------------------------------------------------------------------- #
def detect_outliers(df: pd.DataFrame) -> None:
    q1, q3 = df["Salary"].quantile([0.25, 0.75])
    iqr = q3 - q1
    hi = q3 + 1.5 * iqr
    out = df[df["Salary"] > hi]
    print(f"[3] Outliers salaire (>{hi:,.0f}) : {len(out)} "
          f"-> {out['Position'].unique().tolist()[:5]}")
    bad_age = df[(df["Age"] < 18) | (df["Age"] > 75)]
    print(f"    Ages hors [18-75] : {len(bad_age)}")
    bad_tenure = df[df["TenureYears"] < 0]
    print(f"    Ancienneté négative : {len(bad_tenure)}")


# --------------------------------------------------------------------------- #
# 5. KPI RH
# --------------------------------------------------------------------------- #
def compute_kpis(df: pd.DataFrame) -> dict:
    kpis = {
        "Effectif total": len(df),
        "Effectif actif": int((df["Termd"] == 0).sum()),
        "Départs (total)": int((df["Termd"] == 1).sum()),
        "Taux d'attrition (%)": round(df["AttritionFlag"].mean() * 100, 1),
        "Taux d'attrition volontaire (%)": round(df["IsVoluntary"].mean() * 100, 1),
        "Taux d'absentéisme moyen (%)": round(df["AbsenteeismRate"].mean(), 2),
        "Absences moyennes (jours)": round(df["Absences"].mean(), 1),
        "Satisfaction moyenne (/5)": round(df["EmpSatisfaction"].mean(), 2),
        "Engagement moyen (/5)": round(df["EngagementSurvey"].mean(), 2),
        "% hauts performeurs": round(df["HighPerformer"].mean() * 100, 1),
        "Ancienneté moyenne (ans)": round(df["TenureYears"].mean(), 1),
        "Salaire annuel moyen ($)": int(df["Salary"].mean()),
        "Age moyen (ans)": round(df["Age"].astype(float).mean(), 1),
    }
    print("\n[4] KPI RH")
    for k, v in kpis.items():
        print(f"    - {k:<35}: {v}")
    return kpis


# --------------------------------------------------------------------------- #
# 6. Figures
# --------------------------------------------------------------------------- #
def attrition_rate_by(df, col, order=None):
    g = df.groupby(col, observed=True)["AttritionFlag"].mean().mul(100)
    if order:
        g = g.reindex(order)
    return g.dropna()


def make_figures(df: pd.DataFrame) -> None:
    print("\n[5] Génération des figures...")

    # F1 - Attrition globale (donut)
    counts = df["Attrition"].value_counts()
    plt.figure(figsize=(5, 5))
    plt.pie(counts, labels=["Restés", "Partis"], autopct="%1.1f%%",
            colors=["#2E86AB", "#E4572E"], startangle=90,
            wedgeprops=dict(width=0.42, edgecolor="white"))
    plt.title("Répartition Attrition globale")
    savefig("01_attrition_globale.png")

    # F2 - Effectif par département
    plt.figure(figsize=(8, 4.5))
    order = df["Department"].value_counts().index
    sns.countplot(data=df, y="Department", order=order, color="#2E86AB")
    plt.title("Effectif par département")
    plt.xlabel("Nombre d'employés"); plt.ylabel("")
    savefig("02_effectif_departement.png")

    # F3 - Taux d'attrition par département
    g = attrition_rate_by(df, "Department").sort_values()
    plt.figure(figsize=(8, 4.5))
    sns.barplot(x=g.values, y=g.index, color="#E4572E")
    for i, v in enumerate(g.values):
        plt.text(v + 0.5, i, f"{v:.0f}%", va="center")
    plt.title("Taux d'attrition par département")
    plt.xlabel("Taux d'attrition (%)"); plt.ylabel("")
    savefig("03_attrition_departement.png")

    # F4 - Attrition par tranche d'âge
    g = attrition_rate_by(df, "AgeBand", order=["<30", "30-39", "40-49", "50+"])
    plt.figure(figsize=(7, 4.2))
    sns.barplot(x=g.index, y=g.values, color="#E4572E")
    for i, v in enumerate(g.values):
        plt.text(i, v + 0.5, f"{v:.0f}%", ha="center")
    plt.title("Taux d'attrition par tranche d'âge")
    plt.ylabel("Taux d'attrition (%)"); plt.xlabel("")
    savefig("04_attrition_age.png")

    # F5 - Attrition par satisfaction
    g = attrition_rate_by(df, "EmpSatisfaction").sort_index()
    plt.figure(figsize=(7, 4.2))
    sns.barplot(x=g.index.astype(int), y=g.values, color="#E4572E")
    for i, v in enumerate(g.values):
        plt.text(i, v + 0.5, f"{v:.0f}%", ha="center")
    plt.title("Taux d'attrition selon la satisfaction (EmpSatisfaction)")
    plt.ylabel("Taux d'attrition (%)"); plt.xlabel("Niveau de satisfaction (1-5)")
    savefig("05_attrition_satisfaction.png")

    # F6 - Salaire vs Attrition (box)
    plt.figure(figsize=(6.5, 4.5))
    sns.boxplot(data=df, x="Attrition", y="Salary", hue="Attrition",
                palette=PALETTE, legend=False)
    plt.title("Distribution des salaires selon l'attrition")
    plt.ylabel("Salaire annuel ($)")
    savefig("06_salaire_attrition.png")

    # F7 - Motifs de départ (volontaires)
    vol = df[df["TermReason"] != "N/A-StillEmployed"]["TermReason"].value_counts().head(10)
    plt.figure(figsize=(8, 4.8))
    sns.barplot(x=vol.values, y=vol.index, color="#6C5B7B")
    plt.title("Top 10 des motifs de départ")
    plt.xlabel("Nombre de départs"); plt.ylabel("")
    savefig("07_motifs_depart.png")

    # F8 - Heatmap absentéisme moyen (Département x Tranche d'âge)
    pivot = df.pivot_table(index="Department", columns="AgeBand",
                           values="Absences", aggfunc="mean", observed=True)
    plt.figure(figsize=(8, 4.8))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlOrRd", cbar_kws={"label": "Absences moy."})
    plt.title("Absentéisme moyen (jours) — Département x Âge")
    plt.ylabel(""); plt.xlabel("Tranche d'âge")
    savefig("08_heatmap_absenteisme.png")

    # F9 - Répartition des performances
    perf_order = ["PIP", "Needs Improvement", "Fully Meets", "Exceeds"]
    plt.figure(figsize=(7, 4.2))
    sns.countplot(data=df, x="PerformanceScore", order=perf_order, hue="PerformanceScore",
                  palette=["#E4572E", "#F3A712", "#2E86AB", "#3A7D44"], legend=False)
    plt.title("Répartition des scores de performance")
    plt.ylabel("Nombre d'employés"); plt.xlabel("")
    savefig("09_performance.png")

    # F10 - Impact des canaux de recrutement sur l'attrition
    g = attrition_rate_by(df, "RecruitmentSource").sort_values(ascending=False)
    plt.figure(figsize=(8, 4.8))
    sns.barplot(x=g.values, y=g.index, color="#E4572E")
    plt.title("Taux d'attrition par source de recrutement")
    plt.xlabel("Taux d'attrition (%)"); plt.ylabel("")
    savefig("10_attrition_recrutement.png")

    # F11 - Impact des facteurs (synthèse) : taux d'attrition par modalité
    factors = {
        "Satisfaction <=3": df["EmpSatisfaction"] <= 3,
        "SpecialProjects = 0": df["SpecialProjectsCount"] == 0,
        "Salaire <55k": df["Salary"] < 55000,
        "Ancienneté 0-2 ans": df["TenureBand"] == "0-2 ans",
        "Absences > 12": df["Absences"] > 12,
        "Âge < 30": df["Age"].astype(float) < 30,
    }
    rows = []
    base = df["AttritionFlag"].mean() * 100
    for name, mask in factors.items():
        rows.append((name, df.loc[mask, "AttritionFlag"].mean() * 100))
    fdf = pd.DataFrame(rows, columns=["Facteur", "Taux"]).sort_values("Taux")
    plt.figure(figsize=(8, 4.8))
    sns.barplot(data=fdf, x="Taux", y="Facteur", color="#E4572E")
    plt.axvline(base, color="black", ls="--", lw=1)
    plt.text(base + 0.4, 0, f"Moyenne {base:.0f}%", rotation=90, va="bottom", fontsize=8)
    plt.title("Taux d'attrition par profil à risque")
    plt.xlabel("Taux d'attrition (%)"); plt.ylabel("")
    savefig("11_facteurs_risque.png")

    print(f"    {len(list(FIG_DIR.glob('*.png')))} figures écrites dans {FIG_DIR}")


# --------------------------------------------------------------------------- #
# 7. Export
# --------------------------------------------------------------------------- #
def export(df: pd.DataFrame, kpis: dict) -> None:
    # Colonnes finales utiles pour SQL / Power BI
    cols = [
        "EmpID", "Employee_Name", "GenderLabel", "Sex", "MaritalDesc", "Age", "AgeBand",
        "RaceDesc", "HispanicLatino", "CitizenDesc", "State",
        "Department", "Position", "ManagerName", "RecruitmentSource",
        "Salary", "MonthlyIncome", "SalaryBand",
        "DateofHire", "DateofTermination", "TenureYears", "TenureBand",
        "EmploymentStatus", "TermReason", "Attrition", "AttritionFlag", "IsVoluntary",
        "EmpSatisfaction", "EngagementSurvey",
        "PerformanceScore", "PerfScoreID", "HighPerformer", "LowPerformer",
        "SpecialProjectsCount", "DaysLateLast30", "Absences", "AbsenteeismRate",
        "LastPerformanceReview_Date",
    ]
    clean = df[cols].copy()
    out = OUT_DIR / "hr_clean.csv"
    clean.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"\n[6] Export données propres : {out} ({clean.shape[0]}x{clean.shape[1]})")

    pd.DataFrame(list(kpis.items()), columns=["KPI", "Valeur"]).to_csv(
        OUT_DIR / "kpis.csv", index=False, encoding="utf-8-sig")
    print(f"    Export KPI : {OUT_DIR / 'kpis.csv'}")


# --------------------------------------------------------------------------- #
def main():
    raw = load_raw()
    df = clean(raw)
    df = add_features(df)
    detect_outliers(df)
    kpis = compute_kpis(df)
    make_figures(df)
    export(df, kpis)
    print("\nTerminé.")


if __name__ == "__main__":
    main()
