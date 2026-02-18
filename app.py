import streamlit as st
import pandas as pd
import plotly.express as px
from edgar import Company, set_identity
from fpdf import FPDF
import io
import datetime

# SETUP
set_identity("hhuang5@zagmail.gonzaga.edu")

# GENERAL WEBPAGE
st.set_page_config(page_title="Audit Workbench", layout="wide", page_icon="📊")

# SIDEBAR
st.sidebar.header("🛡️")
ticker = st.sidebar.text_input("Enter Ticker", value="AAPL").upper()

# 10-K Page
st.title(f"10-K Analysis: {ticker}")

if ticker:
    try:
        # Load Company & Financials
        company = Company(ticker)
        st.subheader(f"{company.name} | CIK: {company.cik} | Industry: {company.industry}")
        
        # Get latest 10-K financials
        filing = company.get_filings(form="10-K").latest()
        latest_ten_k = filing.obj()
        financials = latest_ten_k.financials
        
        # --------------------------------- #
        
        # Commands

        income_statement = financials.income_statement
        balance_sheet = financials.balance_sheet
        cash_flow = financials.cash_flow_statement
        
        curr_assets = financials.get('income', 0)
        curr_liabs = financials.get('current_liabilities', 1)
        current_ratio = curr_assets / curr_liabs
        
        # Main Page

        st.markdown("### Risk Factors")
        st.info("Reading Item 1A is critical for assessing 'Going Concern' risk.")
            # Show first 3000 characters for quick review
        risk_factors = latest_ten_j.risk_factors
        st.write(filing.risk_factors[:3000] + "...")

        # Tabs
        tab1, tab2, tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])

        with tab1:
            st.markdown("### Income Statement")
            income_df = financials.income_statement.to_dataframe()
            st.dataframe(income_df, use_container_width=True)
            
            # Simple visualization
            st.markdown("#### Trends")
            fig = px.bar(income_df.head(10), x='label', y='value', color='value', 
                         title="Top Income Statement Line Items")
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown("### Balance Sheet")
            balance_df = financials.balance_sheet.to_dataframe()
            st.dataframe(balance_df, use_container_width=True)

        with tab3:
            st.markdown("### Cash Flow")
            cash_df = financials.cash_flow_statement.to_dataframe()
            st.dataframe(cash_df, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading {ticker}. Please ensure it is a valid US public company ticker.")
        st.exception(e) # Useful for debugging during development

else:
    st.info("Enter a valid ticker in the sidebar.")




