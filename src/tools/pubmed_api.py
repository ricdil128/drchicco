# src/tools/pubmed_api.py
import requests
import time
import logging
import xml.etree.ElementTree as ET
import re

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PubMedClient:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.rate_limit = 10 if api_key else 3  # 10 req/s con chiave API
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def _add_api_key(self, url):
        """Aggiungi la chiave API all'URL se disponibile"""
        if self.api_key and "api_key=" not in url:
            if "?" in url:
                url += f"&api_key={self.api_key}"
            else:
                url += f"?api_key={self.api_key}"
        return url

    def _esearch(self, query):
        """Chiamata a ESearch per ottenere PMIDs"""
        url = f"{self.base_url}esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": 5
        }
        url = self._add_api_key(url + "?" + "&".join([f"{k}={v}" for k, v in params.items()]))
        
        logger.info(f"Chiamata a ESearch: {url}")
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        id_list = data.get("esearchresult", {}).get("idlist", [])
        logger.info(f"Trovati {len(id_list)} PMIDs")
        return id_list

    def _efetch(self, pmid):
        """Chiamata a EFetch per ottenere dettagli articolo"""
        url = f"{self.base_url}efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml"
        }
        url = self._add_api_key(url + "?" + "&".join([f"{k}={v}" for k, v in params.items()]))
        
        logger.info(f"Chiamata a EFetch: {url}")
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def _parse_xml(self, xml_data):
        """Parsing XML da EFetch per estrarre titolo, abstract, ecc."""
        try:
            root = ET.fromstring(xml_data)
            article = root.find(".//PubmedArticle")
            
            title = article.findtext(".//ArticleTitle", default="N/D")
            abstract_element = article.find(".//AbstractText")
            abstract = abstract_element.text if abstract_element is not None else "N/D"
            
            pmid = article.findtext(".//PMID", default="N/D")
            return {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            }
        except Exception as e:
            logger.warning(f"Errore nel parsing XML: {str(e)}")
            return {"pmid": "N/D", "title": "N/D", "abstract": "N/D", "link": "N/D"}

    def search(self, query, max_results=5):
        """Cerca articoli su PubMed usando E-Utilities direttamente"""
        logger.info(f"Eseguo ricerca: {query} (max {max_results} risultati)")
        
        try:
            # Passo 1: Cerca PMIDs con ESearch
            id_list = self._esearch(query)
            
            # Passo 2: Scarica dettagli con EFetch
            results = []
            for i, pmid in enumerate(id_list[:max_results]):
                xml_data = self._efetch(pmid)
                article_data = self._parse_xml(xml_data)
                results.append(article_data)
                time.sleep(1 / self.rate_limit)
            
            logger.info(f"Ricerca completata: {len(results)} risultati validi")
            return results
            
        except Exception as e:
            logger.error(f"Errore durante la ricerca: {str(e)}")
            return []

    def save_results(self, results, output_path):
        """Salva risultati in CSV e JSON"""
        try:
            import pandas as pd
            df = pd.DataFrame(results)
            
            # Assicurati che le colonne essenziali siano presenti
            required_columns = ["pmid", "title", "abstract", "link"]
            for col in required_columns:
                if col not in df.columns:
                    df[col] = "N/D"
            
            # Salva CSV
            csv_path = output_path.replace(".json", ".csv")
            df.to_csv(csv_path, index=False)
            logger.info(f"Risultati salvati in CSV: {csv_path}")
            
            # Salva JSON
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Risultati salvati in JSON: {output_path}")
            
        except Exception as e:
            logger.error(f"Errore durante salvataggio: {str(e)}")
            raise