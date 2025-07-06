import re
import json
import logging
from pathlib import Path
from dateutil.parser import parse

logger = logging.getLogger(__name__)

def extract_text(reply):
    """
    Estrae il contenuto testuale da una risposta LLM.
    Supporta sia stringa semplice che oggetti con attributo .content
    """
    return reply if isinstance(reply, str) else getattr(reply, "content", "")

def filter_by_year_range(articles, year_range):
    """
    Filtra gli articoli in base a un range di anni, es. (1980, 2020).
    Aggiorna anche art["year"] con l'anno estratto se valido.
    """
    if not year_range:
        return articles

    start_year, end_year = year_range
    filtered = []

    for art in articles:
        pubdate = art.get("pubdate", "")
        try:
            dt = parse(pubdate, fuzzy=True)
            year = dt.year
            art["year"] = year  # Salva l'anno utile
            if start_year <= year <= end_year:
                filtered.append(art)
        except Exception:
            continue  # salta se non riesce a fare il parse

    return filtered

def expand_autocomplete_terms(text, log=False):
    """
    Espande abbreviazioni usando un dizionario JSON.
    Restituisce la stringa espansa. Se log=True, logga i cambiamenti.
    """
    dict_path = Path("data") / "autocomplete_dict.json"
    if not dict_path.exists():
        if log:
            logger.warning("⚠️ Nessun dizionario di autocomplete trovato.")
        return text

    with open(dict_path, "r", encoding="utf-8") as f:
        abbrev_map = json.load(f)

    substitutions = 0
    original = text

    for abbrev, full_term in abbrev_map.items():
        pattern = r'\b' + re.escape(abbrev) + r'\b'
        if re.search(pattern, text):
            text = re.sub(pattern, f"{full_term} ({abbrev})", text)
            substitutions += 1

    if log:
        logger.info(f"🔤 Autocomplete: {substitutions} abbreviazioni espanse.")
        if substitutions > 0:
            logger.debug(f"🔎 Input: {original}")
            logger.debug(f"✅ Output: {text}")

    return text
