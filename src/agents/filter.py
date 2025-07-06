# src/agents/filter.py

from autogen import AssistantAgent
from agents.utils import extract_text
import logging

logger = logging.getLogger("FilterAgent")
logger.setLevel(logging.INFO)

class RelevanceFilter:
    def __init__(self, api_key=None):
        self.agent = AssistantAgent(
            name="Filter",
            system_message=(
                "Leggi titolo e abstract. Rispondi solo con 'sì' o 'no': "
                "l'articolo è rilevante per l'obiettivo?"
            ),
            llm_config={
                "temperature": 0,
                "model": "gpt-3.5-turbo",
                "api_key": api_key,
            },
        )

    def is_relevant(self, title, abstract):
        query = f"TITOLO: {title}\nABSTRACT: {abstract}"
        logger.info("🧠 [Filter] Analisi rilevanza in corso...")
        reply = self.agent.generate_reply(messages=[{"role": "user", "content": query}])
        reply_text = extract_text(reply).strip().lower()

        if "sì" in reply_text:
            logger.info("✅ [Filter] Articolo considerato rilevante.")
            return True
        elif "no" in reply_text:
            logger.info("⛔️ [Filter] Articolo non rilevante.")
            return False
        else:
            logger.warning(f"⚠️ [Filter] Risposta ambigua dal modello: {reply_text}")
            return False
