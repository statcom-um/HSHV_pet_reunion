import streamlit as st
import base64
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(
    page_title="Return-to-Owner Analysis",
    page_icon=":world_map:",
    layout="wide",
)

st.sidebar.success("Select a demo above.")

st.title("HSHV Return-to-Owner Analysis")

st.markdown("### Executive Summary")
st.markdown("Insights from the Return-to-Owner (RTO) analysis conducted for the Humane Society of Huron Valley (HSHV).")

st.markdown("---")

st.title("View Full Report")

with open("Results_final.pdf", "rb") as f:
    base64_pdf = f.read()

pdf_viewer(base64_pdf)


st.markdown("---")

st.download_button(
    label="Download Full Report",
    data=open("Results_final.pdf", "rb"),
    file_name="HSHV_RTO_Report.pdf",
    mime="application/pdf",
)
