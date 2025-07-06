import json
import sys
from pathlib import Path

# Aggiunge il path a src per permettere gli import
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root / "src"))

# Ora puoi importare correttamente
from agents.retriever_custom import Retriever
from tools.europepmc_wrapper import EuropePMCWrapper

# --- Configurazione ---
goal = "vitamin D AND diabetes"
project_root = Path(__file__).resolve().parent
output_dir = project_root / "debug"
output_dir.mkdir(parents=True, exist_ok=True)

# --- Inizializza retriever ---
retriever = Retriever()
europepmc = EuropePMCWrapper(page_size=20)

# --- Ricerca ---
print("[test_inspect_articles] Cerco articoli su PubMed...")
raw_results = retriever.search(goal, max_results=20)

if not raw_results:
    print("[test_inspect_articles] Nessun risultato da PubMed. Provo Europe PMC...")
    raw_results = europepmc.search(goal)

# --- Salva i risultati raw per ispezione manuale ---
debug_path = output_dir / "raw_results_debug.json"
with open(debug_path, "w", encoding="utf-8") as f:
    json.dump(raw_results, f, indent=2)

print(f"[test_inspect_articles] Salvato JSON di debug in: {debug_path}")
print(f"[test_inspect_articles] Numero articoli: {len(raw_results)}")