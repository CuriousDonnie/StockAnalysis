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
        cash_flow = financials.cashflow_statement
        
        # Main Page

        st.markdown("### Risk Factors")
        st.info("Reading Item 1A is critical for assessing 'Going Concern' risk.")
            # Show first 3000 characters for quick review
        risk_factors_text = latest_ten_k.risk_factors

        with st.expander("Risk Factors"):
            if risk_factors_text:
                st.write(risk_factors_text[:10000] + "...")
            else:
                st.warning("Risk Factors text not found in this filing.")

        # Tabs
        tab1, tab2, tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])

        with tab1:
            st.markdown("### Income Statement")
            # 1. Reset index and ensure the first column is named 'Account' to avoid duplicates
            df = income_statement(view="standard").to_dataframe().reset_index()
            df.columns.values[0] = "Account" # Force the first column to be "Account"
            
            # 2. Select the first column (Account) + any columns with dates
            cols = [df.columns[0]] + [c for c in df.columns if "-" in str(c)]
            st.dataframe(df[cols], use_container_width=True)
        
        with tab2:
            st.markdown("### Balance Sheet")
            df = balance_sheet(view="standard").to_dataframe().reset_index()
            df.columns.values[0] = "Account"
            cols = [df.columns[0]] + [c for c in df.columns if "-" in str(c)]
            st.dataframe(df[cols], use_container_width=True)
        
        with tab3:
            st.markdown("### Cash Flow")
            df = cash_flow(view="standard").to_dataframe().reset_index()
            df.columns.values[0] = "Account"
            cols = [df.columns[0]] + [c for c in df.columns if "-" in str(c)]
            st.dataframe(df[cols], use_container_width=True)
            
    except Exception as e:
        st.error(f"Error loading {ticker}. Please ensure it is a valid US public company ticker.")
        st.exception(e) # Useful for debugging during development

else:
    st.info("Enter a valid ticker in the sidebar.")




















