def build_pubmed_query(
    main_topic,
    include_terms=None,
    exclude_terms=None,
    population=None,
    outcome=None,
    date_range=None,
    study_types=None,
    use_mesh=True
):
    """
    Costruisce una query avanzata per PubMed.

    Args:
        main_topic (str): Argomento principale della ricerca.
        include_terms (list): Termini da includere (in Title/Abstract).
        exclude_terms (list): Termini da escludere.
        population (str): Popolazione target (es. "humans", "children").
        outcome (str): Esito d'interesse (opzionale).
        date_range (tuple): Range temporale, es. (2010, 2024).
        study_types (list): Tipi di studio da filtrare (es. "randomized controlled trial").
        use_mesh (bool): Se True, population e outcome usano MeSH Terms.

    Returns:
        str: Query pronta da usare per PubMed.
    """
    query_parts = []

    # Argomento principale (usiamo Title/Abstract per ampiezza)
    query_parts.append(f"{main_topic}[Title/Abstract]")

    # Termini da includere
    if include_terms:
        for term in include_terms:
            query_parts.append(f"{term}[Title/Abstract]")

    # Popolazione con MeSH se attivato
    if population:
        if use_mesh:
            query_parts.append(f"{population}[MeSH Terms]")
        else:
            query_parts.append(population)

    # Esito con MeSH se attivato
    if outcome:
        if use_mesh:
            query_parts.append(f"{outcome}[MeSH Terms]")
        else:
            query_parts.append(outcome)

    # Tipi di studio
    if study_types:
        type_clauses = [f"{stype}[Publication Type]" for stype in study_types]
        query_parts.append("(" + " OR ".join(type_clauses) + ")")

    # Range temporale
    if date_range:
        start, end = date_range
        query_parts.append(f"({start}:{end}[dp])")

    # Termini da escludere
    if exclude_terms:
        for term in exclude_terms:
            query_parts.append(f"NOT {term}[Title/Abstract]")

    return " AND ".join(query_parts)


# Esempio d'uso
if __name__ == "__main__":
    query = build_pubmed_query(
        main_topic="vitamin D",
        include_terms=["diabetes", "kidney"],
        exclude_terms=["rat", "mouse"],
        population="humans",
        outcome="kidney failure",
        date_range=(2015, 2024),
        study_types=["randomized controlled trial", "meta-analysis"],
        use_mesh=False
    )
    print(query)
