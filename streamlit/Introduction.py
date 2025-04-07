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
Welcome to the Return-to-Owner Analysis dashboard.

This interactive app presents insights derived from our recent analysis, aimed at understanding patterns and opportunities related to animal returns to their owners.

""")
st.markdown("---")

st.download_button(
    label="Download Full Report",
    data=open("Results_final.pdf", "rb"),
    file_name="HSHV_RTO_Report.pdf",
    mime="application/pdf",
)

st.markdown("---")

st.title("View Full Report")

with open("Results_final.pdf", "rb") as f:
    base64_pdf = f.read()

pdf_viewer(base64_pdf)
