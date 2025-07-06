# src/agents/miner.py

import logging
from autogen import AssistantAgent
from agents.utils import extract_text

logger = logging.getLogger("DataMiner")
logger.setLevel(logging.INFO)

class DataMiner:
    def __init__(self, api_key=None):
        self.agent = AssistantAgent(
            name="Miner",
            system_message=(
                "Estrai i seguenti dati dall'abstract scientifico in formato JSON:\n"
                " - numero_pazienti (int)\n"
                " - tipo_studio (str)\n"
                " - endpoint (str o elenco)\n"
                " - effetto (positivo, negativo, neutro o incerto)\n"
                "Usa solo valori deducibili dal testo. Se mancano, scrivi null."
            ),
            llm_config={
                "temperature": 0,
                "model": "gpt-3.5-turbo",
                "api_key": api_key,
            },
        )

    def extract_data(self, abstract):
        logger.info("⛏️ [Miner] Estrazione dati in corso...")
        query = f"ABSTRACT:\n{abstract}"
        try:
            reply = self.agent.generate_reply(messages=[{"role": "user", "content": query}])
            content = extract_text(reply).strip()

            logger.info(f"✅ [Miner] Risposta ricevuta:\n{content[:200]}...")
            return content
        except Exception as e:
            logger.error(f"❌ [Miner] Errore durante l'estrazione: {str(e)}")
            return "{}"
