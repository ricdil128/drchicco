# test_metapub.py
from metapub import PubMedFetcher
import time
import json

# Configura fetcher
fetcher = PubMedFetcher()

# 1. Cerca PMIDs con search_by_term()
query = "vitamin D AND diabetes"
pmids = fetcher.search_by_term(query, retmax=5)  # Usa search_by_term(), non esearch
print(f"PMIDs trovati: {pmids}")

# 2. Recupera articoli con article_with_pmid()
results = []
for pmid in pmids[:5]:
    try:
        article = fetcher.article_with_pmid(pmid)
        results.append({
            "pmid": pmid,
            "title": getattr(article, "title", "N/D"),
            "abstract": getattr(article, "abstract", "N/D"),
            "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        })
        time.sleep(1 / 3)  # Rispetta il rate limit
    except Exception as e:
        print(f"Errore con PMID {pmid}: {str(e)}")
        continue

# Salva risultati
with open("data/raw/test_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))