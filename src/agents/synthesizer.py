# src/agents/synthesizer.py

import json
import logging
from autogen import AssistantAgent
from agents.utils import extract_text

logger = logging.getLogger("Synthesizer")
logger.setLevel(logging.INFO)

class Synthesizer:
    def __init__(self, api_key=None):
        self.agent = AssistantAgent(
            name="Synth",
            system_message=(
                "Riceverai un obiettivo di ricerca scientifica e una serie di dati JSON estratti dagli abstract.\n"
                "Scrivi un report tecnico e sintetico per ricercatori e professionisti. Includi:\n"
                "- Introduzione all’obiettivo\n"
                "- Metodologia (come sono stati scelti e analizzati gli studi)\n"
                "- Risultati aggregati\n"
                "- Conclusioni con vantaggi/limiti\n"
                "Stile chiaro, tecnico e ordinato. Niente invenzioni, solo ciò che emerge dai dati."
            ),
            llm_config={
                "temperature": 0,
                "model": "gpt-3.5-turbo",
                "api_key": api_key,
            },
        )

    def generate_report(self, goal, mined_data):
        logger.info("📝 [Synthesizer] Generazione report iniziata...")
        if not mined_data:
            logger.warning("⚠️ [Synthesizer] Nessun dato da sintetizzare.")
            return "Nessun dato disponibile per il report."

        input_text = (
            f"OBIETTIVO: {goal}\n\n"
            f"DATI:\n{json.dumps(mined_data, indent=2)}"
        )

        try:
            reply = self.agent.generate_reply(messages=[{"role": "user", "content": input_text}])
            report = extract_text(reply).strip()
            logger.info("✅ [Synthesizer] Report generato correttamente.")
            return report
        except Exception as e:
            logger.error(f"❌ [Synthesizer] Errore nella generazione del report: {str(e)}")
            return "Errore nella generazione del report."
