# src/tools/europepmc_wrapper.py

import requests

class EuropePMCWrapper:
    def __init__(self, page_size=20):
        self.base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        self.page_size = page_size

    def search(self, query):
        """Cerca articoli su Europe PMC e restituisce una lista di dict"""
        params = {
            "query": query,
            "format": "json",
            "pageSize": self.page_size
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            print(f"[EuropePMC] Errore: {response.status_code}")
            return []

        return response.json().get("resultList", {}).get("result", [])

    def get_fulltext_links(self, result):
        """Estrae i link al full-text (se disponibili) da un record EuropePMC"""
        links = []
        fulltext_data = result.get("fullTextUrlList", {}).get("fullTextUrl", [])
        for item in fulltext_data:
            url = item.get("url")
            if url:
                links.append(url)
        return links
