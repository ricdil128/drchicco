import logging
from agents.utils import expand_autocomplete_terms

logger = logging.getLogger(__name__)

def build_pubmed_query(
    main_topic,
    include_terms=None,
    exclude_terms=None,
    population=None,
    outcome=None,
    date_range=None,
    study_types=None,
    use_mesh=True,
    strict_title_abstract=False,
    broad_mode=False  # nuovo parametro
):
    """
    Costruisce una query avanzata per PubMed.
    
    - Se broad_mode=True: usa la sintassi più semplice possibile per massimizzare i risultati
    - Se use_mesh=True: usa [MeSH Terms], [Publication Type], ecc.
    - Se use_mesh=False:
        - strict_title_abstract=True: costruisce query esplicita con [Title/Abstract]
        - strict_title_abstract=False: restituisce direttamente la query espansa
    """

    # Autocomplete sul main topic
    main_topic_exp = expand_autocomplete_terms(main_topic)
    if main_topic != main_topic_exp:
        logger.info(f"[Planner] Autocomplete main_topic: '{main_topic}' → '{main_topic_exp}'")

    # MODALITÀ AMPIA: prioritaria su tutto, usa la query più semplice possibile
    if broad_mode:
        logger.info("[Planner] Modalità ampia attiva: query semplificata")
        query = main_topic_exp.strip()
        
        # Aggiungi solo il filtro per data, se presente
        if date_range:
            start, end = date_range
            query += f" AND ({start}:{end}[dp])"
        
        return query
        
    # Se non vogliamo query strutturata, restituisci il testo espanso
    if not use_mesh and not strict_title_abstract:
        return main_topic_exp.strip()

    query_parts = []

    # === MAIN TOPIC ===
    if use_mesh:
        # Divide il main topic in parti separate
        main_terms = [term.strip() for term in main_topic_exp.split("AND")]
        main_topic_parts = []
        
        for term in main_terms:
            if term:
                # Mappa termini specifici a MeSH appropriati
                if "vitamin d" in term.lower() or "cholecalciferol" in term.lower():
                    main_topic_parts.append('"Vitamin D"[MeSH Terms]')
                elif "diabetes" in term.lower():
                    main_topic_parts.append('"Diabetes Mellitus"[MeSH Terms]')
                else:
                    # Per altri termini, usa la ricerca in Title/Abstract
                    main_topic_parts.append(f'"{term}"[Title/Abstract]')
        
        query_parts.append("(" + " AND ".join(main_topic_parts) + ")")
    else:
        # Spezza su operatori logici o virgole
        keywords = [kw.strip() for kw in main_topic_exp.replace("AND", ",").replace("OR", ",").split(",")]
        for kw in keywords:
            if kw:
                query_parts.append(f'"{kw}"[Title/Abstract]')

    # === INCLUDE TERMS ===
    if include_terms:
        for term in include_terms:
            term_exp = expand_autocomplete_terms(term)
            if term != term_exp:
                logger.info(f"[Planner] Autocomplete include_term: '{term}' → '{term_exp}'")
            query_parts.append(f'"{term_exp}"[Title/Abstract]')

    # === POPULATION ===
    if population:
        pop_exp = expand_autocomplete_terms(population)
        if population != pop_exp:
            logger.info(f"[Planner] Autocomplete population: '{population}' → '{pop_exp}'")
        # MODIFICA QUI: Gestione speciale per 'humans'
        if pop_exp.lower() == "humans" and use_mesh:
            query_parts.append('"humans"[MeSH Terms]')
        else:
            field = "MeSH Terms" if use_mesh else "Title/Abstract"
            query_parts.append(f'"{pop_exp}"[{field}]')

    # === OUTCOME ===
    if outcome:
        out_exp = expand_autocomplete_terms(outcome)
        if outcome != out_exp:
            logger.info(f"[Planner] Autocomplete outcome: '{outcome}' → '{out_exp}'")
        field = "MeSH Terms" if use_mesh else "Title/Abstract"
        query_parts.append(f'"{out_exp}"[{field}]')

    # === STUDY TYPES ===
    if study_types:
        type_clauses = []
        for stype in study_types:
            stype_exp = expand_autocomplete_terms(stype)
            if stype != stype_exp:
                logger.info(f"[Planner] Autocomplete study_type: '{stype}' → '{stype_exp}'")
            type_clauses.append(f'"{stype_exp}"[Publication Type]')
        query_parts.append("(" + " OR ".join(type_clauses) + ")")

    # === DATE RANGE ===
    if date_range:
        start, end = date_range
        query_parts.append(f"({start}:{end}[dp])")

    # === EXCLUDE TERMS ===
    if exclude_terms:
        for term in exclude_terms:
            term_exp = expand_autocomplete_terms(term)
            if term != term_exp:
                logger.info(f"[Planner] Autocomplete exclude_term: '{term}' → '{term_exp}'")
            query_parts.append(f'NOT "{term_exp}"[Title/Abstract]')

    return " AND ".join(query_parts)