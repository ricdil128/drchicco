import json
import sys
import subprocess
from pathlib import Path

# Imposta la root del progetto
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root / "src"))

# Importa moduli interni (se vuoi ancora usare il backend in CLI oltre a Streamlit)
from agents.filter import RelevanceFilter
from agents.miner import DataMiner
from agents.synthesizer import Synthesizer
from agents.retriever_custom import Retriever as APIRetriever
from tools.europepmc_wrapper import EuropePMCWrapper

# 1. Carica chiavi API
with open(project_root / "config" / "api_keys.json") as f:
    api_keys = json.load(f)

openai_key = api_keys.get("openai_api_key")
ncbi_key = api_keys.get("ncbi_api_key")

# 2. Inizializza componenti (opzionale se usi solo interfaccia)
retriever = APIRetriever(api_key=ncbi_key)
europepmc = EuropePMCWrapper(page_size=5)
filter_agent = RelevanceFilter(api_key=openai_key)
data_miner = DataMiner(api_key=openai_key)
synthesizer = Synthesizer(api_key=openai_key)

# 3. Avvia interfaccia Streamlit
streamlit_script = project_root / "app.py"  # cambia se è in un'altra cartella
print(f"[main.py] Avvio interfaccia Streamlit → {streamlit_script}")
subprocess.run([sys.executable, "-m", "streamlit", "run", str(streamlit_script)])
