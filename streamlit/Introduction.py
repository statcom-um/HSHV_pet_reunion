import streamlit as st
import base64
import streamlit.components.v1 as components

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

st.markdown("## View Full Report")

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000px" type="application/pdf"></iframe>'
    components.html(pdf_display, height=1000)

show_pdf("Results_final.pdf")

st.markdown("---")

st.download_button(
    label="Download Full Report",
    data=open("Results_final.pdf", "rb"),
    file_name="HSHV_RTO_Report.pdf",
    mime="application/pdf",
)
