# src/agents/retriever_custom.py

import requests
import time
import logging
import json
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Retriever:
    def __init__(self, api_key=None, tool="DrChiccoTool", email="you@example.com", rate_limit=3):
        self.api_key = api_key
        self.tool = tool
        self.email = email
        self.rate_limit = rate_limit
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def search(self, query, date_range=None):
        logger.info("🔍 [Retriever] Avvio ricerca su PubMed...")

        esearch_url = self.base_url + "esearch.fcgi"
        efetch_url = self.base_url + "efetch.fcgi"

        # if date_range:
        #     start, end = date_range
        #     query = f"{query} AND ({start}:{end}[dp])"
        #     logger.info(f"📅 [Retriever] Filtro temporale attivo: {start}–{end}")

        logger.info(f"📡 [Retriever] Query finale inviata: {query}")
        all_pmids = []
        retstart = 0
        batch_size = 500

        while True:
            params = {
                "db": "pubmed",
                "term": query,
                "retstart": retstart,
                "retmax": batch_size,
                "retmode": "json",
                "tool": self.tool,
                "email": self.email
            }
            if self.api_key:
                params["api_key"] = self.api_key

            try:
                response = requests.get(esearch_url, params=params)
                response.raise_for_status()
                ids = response.json().get("esearchresult", {}).get("idlist", [])
                if not ids:
                    logger.warning("⚠️ [Retriever] Nessun ID trovato. Dump della risposta:")
                    logger.warning(json.dumps(response.json(), indent=2))
                    break

                all_pmids.extend(ids)
                logger.info(f"🔹 PMIDs {retstart}–{retstart + len(ids)}: {len(ids)} trovati")
                retstart += batch_size
                if len(ids) < batch_size:
                    break
                time.sleep(1 / self.rate_limit)

            except Exception as e:
                logger.error(f"❌ [Retriever] Errore durante ESearch: {e}")
                break

        logger.info(f"✅ [Retriever] Totale PMIDs raccolti: {len(all_pmids)}")

        if not all_pmids:
            logger.warning("⚠️ [Retriever] Nessun articolo trovato.")
            return []

        # === EFetch XML ===
        output = []
        fetch_batch = 100
        total_batches = (len(all_pmids) + fetch_batch - 1) // fetch_batch
        logger.info(f"📦 [Retriever] Scarico dettagli in {total_batches} batch da {fetch_batch}...")

        for i in range(0, len(all_pmids), fetch_batch):
            batch_ids = all_pmids[i:i + fetch_batch]
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(batch_ids),
                "retmode": "xml",
                "tool": self.tool,
                "email": self.email
            }
            if self.api_key:
                fetch_params["api_key"] = self.api_key

            logger.info(f"🔄 [Retriever] Batch {i // fetch_batch + 1}/{total_batches} (PMID {i + 1}–{i + len(batch_ids)})")

            try:
                fetch_response = requests.get(efetch_url, params=fetch_params)
                fetch_response.raise_for_status()
                root = ET.fromstring(fetch_response.content)

                for article in root.findall(".//PubmedArticle"):
                    pmid = article.findtext(".//PMID")
                    title = article.findtext(".//ArticleTitle") or ""
                    journal = article.findtext(".//Journal/Title") or ""
                    pubdate_elem = article.find(".//PubDate")
                    pub_year = pubdate_elem.findtext("Year") if pubdate_elem is not None else ""
                    abstract_text = " ".join([abst.text for abst in article.findall(".//AbstractText") if abst.text])
                    if not abstract_text.strip():
                        logger.warning(f"⚠️ [Retriever] Articolo senza abstract. PMID: {pmid}")

                    authors = [
                        f"{a.findtext('LastName', '')} {a.findtext('Initials', '')}".strip()
                        for a in article.findall(".//Author") if a.find("LastName") is not None
                    ]

                    output.append({
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract_text or "[abstract mancante]",
                        "journal": journal,
                        "authors": authors,
                        "pubdate": pub_year,
                        "source": "pubmed"
                    })

                time.sleep(1 / self.rate_limit)

            except Exception as e:
                logger.error(f"❌ [Retriever] Errore batch {i // fetch_batch + 1}: {e}")

        logger.info(f"🏁 [Retriever] Articoli totali recuperati: {len(output)}")
        return output
