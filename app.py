import streamlit as st
import pandas as pd
import plotly.express as px
from edgar import Company, set_identity
from fpdf import FPDF
import io

import streamlit as st
import pandas as pd
import plotly.express as px
from edgar import Company, set_identity
from fpdf import FPDF
import io

# 1. REQUIRED: Tell the SEC who you are
set_identity("hhuang5@zagmail.gonzaga.edu") # Use your real email

st.set_page_config(page_title="Audit Workbench", layout="wide")

# --- Sidebar ---
st.sidebar.header("Audit Controls")
ticker = st.sidebar.text_input("Enter Ticker", value="AAPL").upper()

# --- Main App ---
st.title(f"10-K Analysis Tool: {ticker}")

if ticker:
    try:
        # Load Company & Financials
        company = Company(ticker)
        st.subheader(f"{company.name} | CIK: {company.cik}")
        
        # Get latest 10-K financials
        financials = company.get_financials()
        
        # Organize with Tabs
        tab1, tab2, tab3 = st.tabs(["Income Statement", "Balance Sheet", "Risk Factors"])

        with tab1:
            # Extract and display the income statement
            income_df = financials.income_statement.to_dataframe()
            st.dataframe(income_df, use_container_width=True)
            
            # Simple Revenue Metric for the header
            revenue = financials.get_revenue()
            st.metric("Latest Annual Revenue", f"${revenue:,.0f}")

        with tab2:
            balance_df = financials.balance_sheet.to_dataframe()
            st.dataframe(balance_df, use_container_width=True)

        with tab3:
            # Extracting text directly from the 10-K for risk analysis
            latest_10k = company.get_filings(form="10-K").latest().obj()
            st.markdown("### Item 1A: Risk Factors (First 3000 chars)")
            st.write(latest_10k.risk_factors[:3000] + "...")

    except Exception as e:
        st.error(f"Error loading {ticker}: {e}")

def create_audit_pdf(company_name, ticker, rev, ni):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Preliminary Audit Memo: {company_name}", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Ticker: {ticker}", ln=True)
    pdf.cell(200, 10, txt=f"Reported Revenue: ${rev:,.0f}", ln=True)
    pdf.cell(200, 10, txt=f"Reported Net Income: ${ni:,.0f}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# Add this to the sidebar:
if st.sidebar.button("Export Audit Workpaper"):
    pdf_output = create_audit_pdf(company.name, ticker, financials.get_revenue(), financials.get_net_income())
    st.sidebar.download_button(
        label="Download PDF",
        data=pdf_output,
        file_name=f"{ticker}_audit_memo.pdf",
        mime="application/pdf"
    )