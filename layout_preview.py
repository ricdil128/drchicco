import streamlit as st

st.set_page_config(page_title="DrChicco AI", layout="wide")

# HEADER
st.markdown("<h1 style='font-size: 2.5rem; margin-bottom: 0;'>DrChicco AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: gray; margin-top: 0;'>Scientific Evidence Workflow Assistant</p>", unsafe_allow_html=True)
st.markdown("---")

# TABS
tab1, tab2, tab3 = st.tabs(["1. Screening", "2. Data Extraction", "3. Synthesis & Report"])

# --- TAB 1 ---
with tab1:
    col1, col2, col3 = st.columns([1, 3, 1], gap="large")

    with col1:
        st.markdown("#### Search Parameters")
        st.text_input("Research Objective")
        st.text_input("Keywords / MeSH terms")
        st.date_input("Date Range")
        st.button("Run Search")

    with col2:
        st.markdown("#### Retrieved Articles")
        st.info("Here the titles, abstracts, years, and metadata will be displayed.")

    with col3:
        st.markdown("#### Summary")
        st.info("Graphs and stats from current query.")

# --- TAB 2 ---
with tab2:
    col1, col2, col3 = st.columns([1, 3, 1], gap="large")

    with col1:
        st.markdown("#### Extraction Settings")
        st.checkbox("Show full abstracts")
        st.checkbox("Only studies with N > 50")
        st.button("Extract Data")

    with col2:
        st.markdown("#### Structured Data Table")
        st.info("Extracted numeric and categorical data from articles will be shown here.")

    with col3:
        st.markdown("#### Review Tools")
        st.info("Outliers, alerts, consistency checks.")

# --- TAB 3 ---
with tab3:
    col1, col2, col3 = st.columns([1, 3, 1], gap="large")

    with col1:
        st.markdown("#### Report Settings")
        st.checkbox("Include bias assessment")
        st.checkbox("Limit to RCTs")
        st.button("Generate Report")

    with col2:
        st.markdown("#### Final Scientific Report")
        st.info("Final summary with extracted evidence, charts, and narrative synthesis.")

    with col3:
        st.markdown("#### Notes and Annotations")
        st.text_area("Comments, hypotheses, or limitations...", height=300)
