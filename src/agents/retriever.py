# src/agents/retriever.py

from pymed import PubMed
import time

class Retriever:
    def __init__(self, email="you@example.com", tool="DrChiccoTool", rate_limit=3):
        self.pubmed = PubMed(tool=tool, email=email)
        self.rate_limit = rate_limit
    
    def search(self, query, max_results=100):
        results = self.pubmed.query(query, max_results=max_results)
        output = []

        for article in results:
            data = {
                "pmid": article.pubmed_id,
                "title": article.title,
                "abstract": article.abstract,
                "keywords": article.keywords,
                "publication_date": str(article.publication_date),
                "authors": [a["lastname"] for a in article.authors if "lastname" in a],
                "journal": article.journal
            }
            output.append(data)
            time.sleep(1 / self.rate_limit)

        return output
