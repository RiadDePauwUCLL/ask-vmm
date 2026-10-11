import os
from pathlib import Path

import streamlit as st

from src.qa import VMMQA

st.set_page_config(page_title="Ask VMM", page_icon="🌿", layout="wide")


@st.cache_resource
def build_index() -> VMMQA:
    reports_dir = Path(os.getenv("DATA_DIR", "data/reports"))
    return VMMQA(reports_dir=reports_dir)


index = build_index()

st.title("Ask VMM")
st.caption("Lokale prototypezoeker voor water-, lucht- en klimaatinformatie uit publieke Vlaamse rapporten.")

with st.sidebar:
    st.subheader("Beschikbare documenten")
    for doc in index.list_documents():
        st.write(doc)

question = st.text_area(
    "Stel je vraag (Nederlands of Engels):",
    value="Wat onderzoekt het waterkwaliteitsrapport over de Maas?",
    height=120,
)

if st.button("Antwoord zoeken"):
    answer, sources = index.answer_question(question)

    st.markdown("### Antwoord")
    st.write(answer)

    st.markdown("### Bronvermelding")
    if not sources:
        st.write("Geen bron gevonden in de ingeladen documenten.")
    else:
        for doc_name, page_number in sources:
            st.write(f"- {doc_name} (p. {page_number})")
