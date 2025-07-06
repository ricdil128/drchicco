# app.py

# === Librerie Standard ===
import sys
import json
import time
from pathlib import Path
from collections import Counter

# === Librerie Esterne ===
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from fpdf import FPDF

# === Configurazione dei percorsi ===
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root / "src"))  # Aggiunge 'src' ai path per importazioni

# === Import locali (da src.agents.*) ===
from agents.utils import expand_autocomplete_terms, filter_by_year_range
from agents.planner import build_pubmed_query
from agents.aggregator import aggregate_patients, aggregate_endpoint_counts
from agents.filter import RelevanceFilter
from agents.miner import DataMiner
from agents.synthesizer import Synthesizer
from agents.retriever_custom import Retriever
from tools.europepmc_wrapper import EuropePMCWrapper

# --- Configurazioni generali ---
project_root = Path(__file__).resolve().parent
output_dir = project_root / "data" / "processed"
report_dir = project_root / "data" / "reports"
output_dir.mkdir(parents=True, exist_ok=True)
report_dir.mkdir(parents=True, exist_ok=True)

# Caricamento chiavi API
with open(project_root / "config" / "api_keys.json") as f:
    api_keys = json.load(f)

openai_key = api_keys.get("openai_api_key")

# --- Inizializzazione agenti ---
retriever = Retriever(api_key=api_keys.get("ncbi_api_key"))
europepmc = EuropePMCWrapper(page_size=10)
filter_agent = RelevanceFilter(api_key=openai_key)
data_miner = DataMiner(api_key=openai_key)
synthesizer = Synthesizer(api_key=openai_key)

# --- UI Streamlit ---
st.set_page_config(page_title="DrChicco AI", layout="wide")
st.title("🔬 DrChicco AI – Ricerca Scientifica Intelligente")

# Layout 3 colonne: sinistra, centrale, destra
col_left, col_center, col_right = st.columns([1, 2, 1])

# --- SINISTRA: Form Ricerca ---
with col_left:
    st.header("Impostazioni Ricerca")
    user_goal = st.text_input("Obiettivo", "vitamin D AND diabetes")
    start_year, end_year = st.slider("Anno pubblicazione", 2000, 2025, (2015, 2024))
    
    # Opzioni di ricerca - posizionate insieme per chiarezza visiva
    col1, col2 = st.columns(2)
    with col1:
        use_mesh = st.checkbox("Usa MeSH", value=True)
    with col2:
        broad_mode = st.checkbox("Modalità ampia", value=False, help="Usa query semplice per massimizzare i risultati")
    
    include_terms = st.text_input("Termini da includere", "glucose metabolism")
    exclude_terms = st.text_input("Termini da escludere", "rat")
    population = st.text_input("Popolazione", "humans")
    outcome = st.text_input("Outcome", "insulin sensitivity")
    study_types = st.multiselect("Tipo studio", ["Randomized Controlled Trial", "Meta-Analysis", "Review", "Cohort"], default=["Randomized Controlled Trial"])
    run = st.button("🚀 Avvia ricerca")

# Placeholder per log
log_box = col_right.empty()

# --- Fase di ricerca ---
if run:
   # Espansione iniziale
    expanded_input = expand_autocomplete_terms(user_goal)

    # Genera la query completa
    query = build_pubmed_query(
        main_topic=expanded_input,
        include_terms=include_terms.split(",") if include_terms else None,
        exclude_terms=exclude_terms.split(",") if exclude_terms else None,
        population=population,
        outcome=outcome,
        date_range=(start_year, end_year),
        study_types=study_types,
        use_mesh=use_mesh,
        strict_title_abstract=not use_mesh,  # forza la ricerca Title/Abstract se MeSH è off
        broad_mode=broad_mode  # aggiungi il nuovo parametro
    )
 
    # Log visuale
    col_left.markdown("#### 🔍 Query generata")
    col_left.code(query)

    # Info su tipo di query
    if broad_mode:
        col_right.markdown("📊 **Modalità ampia attiva**: query semplificata per massimi risultati")
    elif use_mesh:
        col_right.markdown("✅ Query generata con filtri MeSH")
    else:
        col_right.markdown("📘 Query manuale (senza MeSH), con autocomplete attivo")

    # Mostra anche la versione espansa dei termini (solo se cambia)
    if expanded_input != user_goal:
        col_right.markdown("📚 **Espansione autocomplete:**")
        col_right.code(expanded_input)

    # RICERCA ARTICOLI
    log_box.info("🔎 Ricerca articoli in corso...")
    raw_results = retriever.search(query, date_range=(start_year, end_year))
    if not raw_results:
        log_box.warning("⚠️ Nessun risultato da PubMed, passo a EuropePMC...")
        raw_results = europepmc.search(user_goal)

    log_box.success(f"✅ Articoli totali trovati: {len(raw_results)}")

    # --- FILTRO AI ---
    filtered = []
    debug_log = []
    status_msg = col_right.empty()

    with st.spinner("🧠 Filtro AI in corso..."):
        for idx, article in enumerate(raw_results, 1):
            status_msg.info(f"🧠 Filtraggio {idx}/{len(raw_results)}")
            title = article.get("title", "N/D")
            abstract = article.get("abstract") or article.get("abstractText", "N/D")
            pub_year_raw = article.get("pubYear") or article.get("year") or article.get("publicationYear") or article.get("pubdate")

            try:
                pub_year = int(pub_year_raw.strip()[:4]) if isinstance(pub_year_raw, str) else int(pub_year_raw)
            except:
                pub_year = 0

            if filter_agent.is_relevant(title, abstract):
                filtered.append({
                    "pmid": article.get("pmid", article.get("id", "N/A")),
                    "title": title,
                    "abstract": abstract,
                    "year": pub_year,
                    "journal": article.get("journal", "N/A"),
                    "authors": article.get("authors", [])
                })

    status_msg.success(f"✅ Articoli filtrati: {len(filtered)}")

    # --- COLONNA CENTRALE: visualizza articoli e abstract ---
    with col_center:
        st.subheader("📄 Articoli rilevanti")
        for art in filtered:
            with st.expander(f"{art['title']} ({art['year']})"):
                st.markdown(f"**Abstract**: {art['abstract']}")
                st.markdown(f"**Journal**: {art['journal']}")
                st.markdown(f"**Autori**: {', '.join(art['authors'])}")
                st.markdown(f"**PMID**: `{art['pmid']}`")

    # --- ESECUZIONE ESTRAZIONE DATI ---
    mined_data = []
    status_msg = col_right.empty()

    with st.spinner("🔬 Estrazione dati dagli abstract..."):
        for idx, art in enumerate(filtered, 1):
            status_msg.info(f"🧬 Estrazione {idx}/{len(filtered)}")
            extracted = data_miner.extract_data(art["abstract"])
            mined_data.append({
                "pmid": art["pmid"],
                "year": art["year"],
                "extracted": extracted
            })

    status_msg.success("📦 Dati estratti da tutti gli articoli.")

    # --- GRAFICO distribuzione articoli ---
    with col_right:
        if filtered:
            st.markdown("### 📊 Articoli per anno")
            year_counts = Counter([art["year"] for art in filtered])
            years, counts = zip(*sorted(year_counts.items()))
            fig, ax = plt.subplots()
            ax.bar(years, counts)
            ax.set_xlabel("Anno")
            ax.set_ylabel("N. articoli")
            st.pyplot(fig)

    # --- REPORT FINALE ---
    with st.spinner("📘 Generazione report finale..."):
        report = synthesizer.generate_report(user_goal, mined_data)
        st.subheader("📘 Report")
        st.markdown(report)

    # --- Salvataggi ---
    with open(output_dir / "filtered.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2)
    with open(output_dir / "mined.json", "w", encoding="utf-8") as f:
        json.dump(mined_data, f, indent=2)
    with open(report_dir / "report.md", "w", encoding="utf-8") as f:
        f.write(report)

    # PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in report.splitlines():
        pdf.multi_cell(0, 10, line)
    pdf.output(str(report_dir / "report.pdf"))

    st.success("✅ Report salvato e pronto al download.")
    with open(report_dir / "report.md", "rb") as f_md:
        st.download_button("Scarica Report (.md)", f_md, file_name="report.md")
    with open(report_dir / "report.pdf", "rb") as f_pdf:
        st.download_button("Scarica Report (.pdf)", f_pdf, file_name="report.pdf")
