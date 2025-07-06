# src/tools/autocomplete_builder.py

import json
from pathlib import Path

# 1. Crea la cartella /data se non esiste
data_dir = Path("data")
data_dir.mkdir(parents=True, exist_ok=True)

# 2. Dizionario di abbreviazioni medico-scientifiche → espansioni
autocomplete_dict = {
    # Endocrinologia / Metabolismo
    "T2DM": "Type 2 Diabetes Mellitus",
    "T1DM": "Type 1 Diabetes Mellitus",
    "PCOS": "Polycystic Ovary Syndrome",
    "CIMT": "Carotid Intima-Media Thickness",
    "HOMA-IR": "Homeostasis Model Assessment of Insulin Resistance",
    "OGTT": "Oral Glucose Tolerance Test",
    "HbA1c": "Hemoglobin A1c",
    "BMI": "Body Mass Index",
    "NAFLD": "Non-alcoholic Fatty Liver Disease",

    # Cardiologia
    "MI": "Myocardial Infarction",
    "CAD": "Coronary Artery Disease",
    "CHF": "Congestive Heart Failure",
    "HTN": "Hypertension",
    "BP": "Blood Pressure",
    "LDL": "Low-Density Lipoprotein",
    "HDL": "High-Density Lipoprotein",
    "ECG": "Electrocardiogram",

    # Oncologia
    "CRC": "Colorectal Cancer",
    "NSCLC": "Non-Small Cell Lung Cancer",
    "BRCA": "Breast Cancer",
    "PSA": "Prostate Specific Antigen",
    "HER2": "Human Epidermal Growth Factor Receptor 2",
    "TNBC": "Triple Negative Breast Cancer",

    # Neurologia / Psichiatria
    "AD": "Alzheimer's Disease",
    "PD": "Parkinson's Disease",
    "MS": "Multiple Sclerosis",
    "MCI": "Mild Cognitive Impairment",
    "SSRIs": "Selective Serotonin Reuptake Inhibitors",
    "GAD": "Generalized Anxiety Disorder",

    # Immunologia / Infettive
    "RA": "Rheumatoid Arthritis",
    "SLE": "Systemic Lupus Erythematosus",
    "HIV": "Human Immunodeficiency Virus",
    "HBV": "Hepatitis B Virus",
    "HCV": "Hepatitis C Virus",
    "TB": "Tuberculosis",

    # Gastroenterologia
    "IBS": "Irritable Bowel Syndrome",
    "IBD": "Inflammatory Bowel Disease",
    "UC": "Ulcerative Colitis",
    "CD": "Crohn's Disease",

    # Misc
    "QoL": "Quality of Life",
    "RCT": "Randomized Controlled Trial",
    "AE": "Adverse Event",
    "HRQoL": "Health-Related Quality of Life",
    "CRP": "C-Reactive Protein",
    "CI": "Confidence Interval",
    "OR": "Odds Ratio",
    "RR": "Risk Ratio",
    "SD": "Standard Deviation"
}

# 3. Salvataggio in JSON
output_path = data_dir / "autocomplete_dict.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(autocomplete_dict, f, indent=2)

print(f"✅ Dizionario autocomplete salvato in: {output_path}")
