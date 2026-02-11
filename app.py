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
                    
            def get_income_dataframe(ticker:str):
                filings = company.get_filings(form="10-K").latest(5)
                xbs = XBRLS.from_filings(filings)
                income_statement = xbs.statements.income_statement()
                income_df = income_statement.to_dataframe()
                return income_df


            def plot_revenue(ticker:str):
                income_df = get_income_dataframe(ticker)

                # Extract financial metrics
                net_income = income_df[income_df.concept == "us-gaap_NetIncomeLoss"][income_statement.periods].iloc[0]
                gross_profit = income_df[income_df.concept == "us-gaap_GrossProfit"][income_statement.periods].iloc[0]
                revenue = income_df[income_df.label == "Revenue"][income_statement.periods].iloc[0]

                # Convert periods to fiscal years for better readability
                periods = [pd.to_datetime(period).strftime('FY%y') for period in income_statement.periods]

                # Reverse the order so most recent years are last (oldest to newest)
                periods = periods[::-1]
                revenue_values = revenue.values[::-1]
                gross_profit_values = gross_profit.values[::-1]
                net_income_values = net_income.values[::-1]

                # Create a DataFrame for plotting
                plot_data = pd.DataFrame({
                    'Revenue': revenue_values,
                    'Gross Profit': gross_profit_values,
                    'Net Income': net_income_values
                }, index=periods)

                # Convert to billions for better readability
                plot_data = plot_data / 1e9

                # Create the figure
                fig, ax = plt.subplots(figsize=(10, 6))

                # Plot the data as lines with markers
                plot_data.plot(kind='line', marker='o', ax=ax, linewidth=2.5)

                # Format the y-axis to show billions with 1 decimal place
                ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x:.1f}B'))

                # Add labels and title
                ax.set_xlabel('Fiscal Year')
                ax.set_ylabel('Billions USD')
                ax.set_title(f'{company.name} ({ticker}) Financial Performance')

                # Add a grid for better readability
                ax.grid(True, linestyle='--', alpha=0.7)

                # Add a source note
                plt.figtext(0.5, 0.01, 'Source: SEC EDGAR via edgartools', ha='center', fontsize=9)

                # Improve layout
                plt.tight_layout(rect=[0, 0.03, 1, 0.97])

                return fig


            # Extract and display the income statement
            income_df = financials.income_statement().to_dataframe()
            st.dataframe(income_df, use_container_width=True)
            
            # Simple Revenue Metric for the header
            balance_df = financials.balance_sheet().to_dataframe()
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