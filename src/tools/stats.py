# src/tools/stats.py
import statsmodels.api as sm
import numpy as np

def calculate_rr(data):
    """Calcola Risk Ratio da dati estratti"""
    # Esempio: input = [{"n": 100, "events": 20}, {"n": 100, "events": 30}]
    # Codice per RR = (20/100) / (30/100) = 0.67
    return np.mean([item["rr"] for item in data])