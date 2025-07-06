# test_search.py
import sys
import os
import json

# Aggiungi src/ al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools.pubmed_api import PubMedClient

# Carica chiave API
with open("config/api_keys.json") as f:
    api_keys = json.load(f)

# Inizializza client
pubmed = PubMedClient(api_key=api_keys.get("ncbi_api_key"))

# Esegui ricerca
user_goal = "vitamin D AND diabetes"
results = pubmed.search(user_goal, max_results=5)

# Salva risultati
pubmed.save_results(results, "data/raw/test_results.json")