import streamlit as st
import pandas as pd
import plotly.express as px
from edgar import Company, set_identity
from fpdf import FPDF
import io

# 1. REQUIRED: Tell the SEC who you are
if "SEC_EMAIL" in st.secrets:
    set_identity(st.secrets["SEC_EMAIL"])
else:
    print("Email failed.")

st.set_page_config(page_title="Donnie's Stock Analysis", layout="wide")

# --- Sidebar ---
st.sidebar.header("Stock")
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
            # 1. Define the Data Fetching (Keep this as is)
            def get_income_dataframe(ticker:str):
                from edgar import XBRLS # Ensure XBRLS is available
                filings = company.get_filings(form="10-K").latest(5)
                xbs = XBRLS.from_filings(filings)
                income_stmt = xbs.statements.income_statement()
                return income_stmt, income_stmt.to_dataframe()

            # 2. Define the Plotting Function (Fixed Streamlit Integration)
            def plot_revenue(ticker:str):
                import matplotlib.pyplot as plt
                import matplotlib.ticker as mtick
                
                income_stmt, income_df = get_income_dataframe(ticker)
                periods_list = income_stmt.periods
                
                # Extract metrics using the labels/concepts
                net_income = income_df[income_df.concept == "us-gaap_NetIncomeLoss"][periods_list].iloc[0]
                revenue = income_df[income_df.label == "Revenue"][periods_list].iloc[0]

                # Formatting data
                periods = [pd.to_datetime(p).strftime('FY%y') for p in periods_list][::-1]
                rev_vals = revenue.values[::-1] / 1e9 # Billions
                ni_vals = net_income.values[::-1] / 1e9

                # CREATE THE FIGURE
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(periods, rev_vals, marker='o', label='Revenue', linewidth=2)
                ax.plot(periods, ni_vals, marker='s', label='Net Income', linestyle='--')
                
                ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:.1f}B'))
                ax.set_title(f"{ticker} Financial Performance")
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                return fig

            # 3. ACTUALLY CALL AND SHOW THE STUFF
            # Show the table
            income_stmt_obj, income_df_table = get_income_dataframe(ticker)
            st.dataframe(income_df_table, use_container_width=True)
            
            # SHOW THE GRAPH
            st.markdown("### Performance Visual")
            financial_fig = plot_revenue(ticker)
            st.pyplot(financial_fig) # <--- THIS IS WHAT MAKES IT POP UP

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