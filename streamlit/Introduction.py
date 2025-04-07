import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(
    page_title="Return-to-Owner Analysis",
    page_icon=":world_map:",
    layout="wide",
)

# Header
st.title("HSHV Return-to-Owner Analysis")
st.markdown("##### Humane Society of Huron Valley (HSHV) | Data Insights")

# Intro Section
st.markdown("""

This interactive app presents insights derived from our data analysis, aimed at understanding patterns and implementing interventions focused on increasing animal return rates to their owners.

""")

st.download_button(
    label="Download Full Report",
    data=open("Results_final.pdf", "rb"),
    file_name="HSHV_RTO_FinalReport.pdf",
    mime="application/pdf",
)

st.markdown("---")

with open("Results_final.pdf", "rb") as f:
    base64_pdf = f.read()

pdf_viewer(base64_pdf)
