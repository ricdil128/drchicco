import logging

# Setup logging
logger = logging.getLogger("Aggregator")
logger.setLevel(logging.INFO)

def aggregate_patients(mined_data):
    """
    Somma i pazienti da tutti gli articoli che riportano un campo 'patients'.
    """
    logger.info("📊 [Aggregator] Inizio aggregazione del numero totale di pazienti...")
    total_patients = 0
    articles_counted = 0

    for item in mined_data:
        try:
            data = item.get("extracted", {})
            patients = data.get("patients")
            if isinstance(patients, int):
                total_patients += patients
                articles_counted += 1
            else:
                logger.debug(f"⚠️ [Aggregator] Dato 'patients' non valido per PMID {item.get('pmid')}: {patients}")
        except Exception as e:
            logger.error(f"❌ [Aggregator] Errore durante l'aggregazione pazienti per PMID {item.get('pmid')}: {e}")

    logger.info(f"✅ [Aggregator] Totale pazienti aggregati: {total_patients} da {articles_counted} articoli.")
    return total_patients

def aggregate_endpoint_counts(mined_data):
    """
    Conta la frequenza di ciascun endpoint menzionato nei dati estratti.
    """
    logger.info("📈 [Aggregator] Inizio conteggio degli endpoint...")
    endpoint_counts = {}

    for item in mined_data:
        try:
            data = item.get("extracted", {})
            endpoints = data.get("endpoints", [])
            if isinstance(endpoints, list):
                for endpoint in endpoints:
                    endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
            else:
                logger.debug(f"⚠️ [Aggregator] Dato 'endpoints' non valido per PMID {item.get('pmid')}: {endpoints}")
        except Exception as e:
            logger.error(f"❌ [Aggregator] Errore durante il conteggio endpoint per PMID {item.get('pmid')}: {e}")

    logger.info(f"✅ [Aggregator] Conteggio completato. Endpoint distinti trovati: {len(endpoint_counts)}.")
    return endpoint_counts
