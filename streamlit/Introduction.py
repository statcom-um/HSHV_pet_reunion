import streamlit as st

st.set_page_config(
    page_title="Return-to-Owner Analysis",
    page_icon=":world_map:️",
    layout="wide",
)

st.sidebar.success("Select a demo above.")

"# HSHV streamlit-app"

"""Intros"""
import streamlit as st
from PyPDF2 import PdfReader

st.set_page_config(
    page_title="Return-to-Owner Analysis",
    page_icon="🌎",
    layout="wide",
)

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.success("Select a section above.")

# Header
st.title("HSHV Return-to-Owner Analysis")
st.markdown("##### Humane Society of Huron Valley (HSHV) | Data Insights")

# Intro Section
st.markdown("""
Welcome to the Return-to-Owner Analysis dashboard.

This interactive app presents insights derived from our recent analysis, aimed at understanding patterns and opportunities related to animal returns to their owners.

""")

# PDF Viewer Section
st.subheader("Results Report")

# Load PDF
with open("Results (final).pdf", "rb") as f:
    reader = PdfReader(f)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

# Expandable view
with st.expander("View Full Report"):
    st.text(text)

# Optional: Download button for client
with open("Results (final).pdf", "rb") as f:
    st.download_button("Download Full PDF Report", f, file_name="Results_Report.pdf")

# Footer
st.markdown("---")
st.markdown("App developed by [Your Name or Org]")

