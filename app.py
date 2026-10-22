import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Nassau Candy - Profitability & Margin Performance",
    page_icon="🍬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# CUSTOM CSS: Full-Width Stretch, Tab Gaps, Clean Spacing, Big Fonts
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Main body padding - full screen use */
    .block-container {
        padding-top: 3.2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }
    
    body {
        overflow-x: hidden !important;
    }

    /* 1. SIDEBAR: Compact to remove vertical scrollbar */
    section[data-testid="stSidebar"] {
        overflow: hidden !important;
    }
    section[data-testid="stSidebar"] > div {
        overflow: hidden !important;
        padding-top: 1.2rem !important;
        padding-bottom: 0.5rem !important;
    }
    section[data-testid="stSidebar"] .stMultiSelect,
    section[data-testid="stSidebar"] .stDateInput,
    section[data-testid="stSidebar"] .stSlider,
    section[data-testid="stSidebar"] .stTextInput {
        margin-bottom: -4px !important;
    }
    section[data-testid="stSidebar"] label {
        font-size: 0.86rem !important;
        font-weight: 600 !important;
        margin-bottom: 2px !important;
    }

    /* 2. HEADER: Line-height & Padding Fix (Akshare cut honar nahit) */
    .main-distributor-title {
        font-size: 2.4rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        line-height: 1.5 !important;
        padding: 6px 0px !important;
        margin-top: 0.2rem !important;
        margin-bottom: 0.4rem !important;
        display: block !important;
    }
    
    .sub-distributor-title {
        font-size: 1.15rem !important;
        font-weight: 500 !important;
        color: #475569 !important;
        line-height: 1.4 !important;
        margin-bottom: 1.8rem !important;
        display: block !important;
    }

    /* 3. METRIC CARDS: Big Headings, Full Uncut Numbers */
    div[data-testid="stMetric"] {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        padding: 14px 16px !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        min-height: 105px !important;
    }

    div[data-testid="stMetricLabel"] p {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        margin-bottom: 6px !important;
        text-transform: capitalize !important;
    }

    div[data-testid="stMetricValue"] > div {
        font-size: 1.55rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        line-height: 1.25 !important;
    }

    /* 4. TABS: Spread evenly across screen with good distance */
    .stTabs [data-baseweb="tab-list"] {
        display: flex !important;
        justify-content: space-between !important;
        width: 100% !important;
        margin-top: 1.2rem !important;
        margin-bottom: 1.6rem !important;
        border-bottom: 2px solid #e2e8f0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1 !important;
        text-align: center !important;
        font-size: 1.02rem !important;
        font-weight: 600 !important;
        padding: 12px 18px !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 1. DATA CACHING & PREPARATION
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    csv_candidates = [
        'Nassau Candy Distributor.csv',
        '/content/Nassau Candy Distributor.csv'
    ]
    target_csv = next((f for f in csv_candidates if os.path.exists(f)), None)

    if not target_csv:
        st.error("Error: 'Nassau Candy Distributor.csv' file not found.")
        st.stop()

    df = pd.read_csv(target_csv)

    str_cols = ['Division', 'Region', 'Country/Region', 'City', 'State/Province', 'Product ID', 'Product Name', 'Ship Mode']
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
    df['Gross Margin (%)'] = (df['Gross Profit'] / df['Sales']) * 100
    df['Profit per Unit'] = df['Gross Profit'] / df['Units']

    return df

df_raw = load_data()

# -----------------------------------------------------------------------------
# 2. SIDEBAR USER CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.markdown("### 🍬 User Controls")

min_date = df_raw['Order Date'].min().date()
max_date = df_raw['Order Date'].max().date()
date_range = st.sidebar.date_input("Date Range Selector", (min_date, max_date), min_value=min_date, max_value=max_date)

all_divisions = sorted(df_raw['Division'].unique().tolist())
selected_divisions = st.sidebar.multiselect("Division Filter", options=all_divisions, default=all_divisions)

margin_threshold = st.sidebar.slider("Margin Threshold Slider (%)", min_value=0.0, max_value=100.0, value=50.0, step=1.0)
search_query = st.sidebar.text_input("Product Search", placeholder="e.g. Wonka, Kazookles...")

# Apply Filters
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_d, end_d = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    fdf = df_raw[(df_raw['Order Date'] >= start_d) & (df_raw['Order Date'] <= end_d)].copy()
else:
    fdf = df_raw.copy()

fdf = fdf[fdf['Division'].isin(selected_divisions)]

if search_query.strip():
    fdf = fdf[fdf['Product Name'].str.contains(search_query, case=False, na=False)]

# -----------------------------------------------------------------------------
# 3. HEADER & METRIC CARDS
# -----------------------------------------------------------------------------
st.markdown('<div class="main-distributor-title">🍬 Nassau Candy Distributor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-distributor-title">Product Line Profitability & Margin Performance Analysis</div>', unsafe_allow_html=True)

kpi_sales = fdf['Sales'].sum()
kpi_profit = fdf['Gross Profit'].sum()
kpi_cogs = fdf['Cost'].sum()
kpi_units = fdf['Units'].sum()
kpi_margin = (kpi_profit / kpi_sales * 100) if kpi_sales > 0 else 0

# 5 Balanced KPI cards with spacing
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Gross Revenue", f"${kpi_sales:,.2f}")
k2.metric("Gross Profit", f"${kpi_profit:,.2f}")
k3.metric("Total COGS", f"${kpi_cogs:,.2f}")
k4.metric("Average Gross Margin", f"{kpi_margin:.2f}%")
k5.metric("Total Units Sold", f"{kpi_units:,}")

st.write("") 

# -----------------------------------------------------------------------------
# 4. DASHBOARD MODULES (FULL SPREAD & PROPER GAP)
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Product Profitability Overview",
    "🏢 Division Performance Dashboard",
    "🔬 Cost vs Margin Diagnostics",
    "🎯 Profit Concentration Analysis"
])

# Product Aggregation
prod_kpi = fdf.groupby(['Product ID', 'Product Name', 'Division']).agg(
    Revenue=('Sales', 'sum'),
    Cost=('Cost', 'sum'),
    Gross_Profit=('Gross Profit', 'sum'),
    Units=('Units', 'sum')
).reset_index()

prod_kpi['Gross Margin (%)'] = (prod_kpi['Gross_Profit'] / prod_kpi['Revenue']) * 100
prod_kpi['Profit per Unit'] = prod_kpi['Gross_Profit'] / prod_kpi['Units']
prod_kpi['Profit Contribution (%)'] = (prod_kpi['Gross_Profit'] / kpi_profit * 100) if kpi_profit > 0 else 0

# -----------------------------------------------------------------------------
# MODULE 1: Product Profitability Overview
# -----------------------------------------------------------------------------
with tab1:
    # 2 Columns with full width and clear margin
    c_p1, c_p2 = st.columns([1.1, 1], gap="large")
    with c_p1:
        st.markdown("#### Product-Level Margin Leaderboard")
        fig_leaderboard = px.bar(
            prod_kpi.sort_values(by='Gross Margin (%)', ascending=True),
            x='Gross Margin (%)', y='Product Name', orientation='h',
            color='Gross Margin (%)', color_continuous_scale='Blues',
            text=prod_kpi.sort_values(by='Gross Margin (%)', ascending=True)['Gross Margin (%)'].apply(lambda x: f"{x:.1f}%")
        )
        # l=190 ensures product names are never cut off or overlapping the chart
        fig_leaderboard.update_layout(
            height=480,
            margin=dict(l=190, r=20, t=10, b=20),
            xaxis_title="Gross Margin (%)",
            yaxis_title="",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_leaderboard, use_container_width=True)
    with c_p2:
        st.markdown("#### Profit Contribution Charts")
        fig_pie = px.pie(
            prod_kpi, names='Product Name', values='Gross_Profit',
            hole=0.45, color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            height=480,
            margin=dict(l=10, r=10, t=10, b=20),
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------------------------------------------------
# MODULE 2: Division Performance Dashboard
# -----------------------------------------------------------------------------
with tab2:
    div_summary = fdf.groupby('Division').agg(
        Revenue=('Sales', 'sum'), Cost=('Cost', 'sum'),
        Gross_Profit=('Gross Profit', 'sum'), Units=('Units', 'sum')
    ).reset_index()
    div_summary['Gross Margin (%)'] = (div_summary['Gross_Profit'] / div_summary['Revenue']) * 100
    div_summary['Revenue Share (%)'] = (div_summary['Revenue'] / kpi_sales * 100) if kpi_sales > 0 else 0
    div_summary['Profit Share (%)'] = (div_summary['Gross_Profit'] / kpi_profit * 100) if kpi_profit > 0 else 0

    c_d1, c_d2 = st.columns(2, gap="large")
    with c_d1:
        st.markdown("#### Revenue vs Profit Comparison")
        fig_div_bar = go.Figure(data=[
            go.Bar(name='Revenue ($)', x=div_summary['Division'], y=div_summary['Revenue'], marker_color='#1f77b4'),
            go.Bar(name='Gross Profit ($)', x=div_summary['Division'], y=div_summary['Gross_Profit'], marker_color='#2ca02c')
        ])
        fig_div_bar.update_layout(barmode='group', height=450, margin=dict(l=20, r=20, t=20, b=20), yaxis_title="USD ($)")
        st.plotly_chart(fig_div_bar, use_container_width=True)
    with c_d2:
        st.markdown("#### Margin Distribution by Division")
        fig_box = px.box(fdf, x='Division', y='Gross Margin (%)', color='Division', points='outliers')
        fig_box.update_layout(height=450, margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

# -----------------------------------------------------------------------------
# MODULE 3: Cost vs Margin Diagnostics
# -----------------------------------------------------------------------------
with tab3:
    prod_kpi['Risk Flag'] = np.where(
        prod_kpi['Gross Margin (%)'] < margin_threshold,
        f'Margin Risk (< {margin_threshold:.0f}%)',
        'Healthy Margin'
    )
    st.markdown("#### Cost-Sales Scatter Plots")
    fig_scatter = px.scatter(
        prod_kpi, x='Cost', y='Revenue', size='Units', color='Risk Flag',
        hover_name='Product Name',
        hover_data=['Division', 'Gross Margin (%)', 'Profit per Unit'],
        color_discrete_map={'Healthy Margin': '#22c55e', f'Margin Risk (< {margin_threshold:.0f}%)': '#ef4444'},
        title=f"Cost vs. Revenue Scatter Plot (Risk Threshold: {margin_threshold:.0f}%)"
    )
    fig_scatter.update_layout(height=460, margin=dict(l=20, r=20, t=35, b=20), xaxis_title="Total Cost ($)", yaxis_title="Total Revenue ($)")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("#### Margin Risk Flags")
    risk_products = prod_kpi[prod_kpi['Gross Margin (%)'] < margin_threshold].sort_values(by='Gross Margin (%)')
    if not risk_products.empty:
        st.dataframe(
            risk_products[['Product Name', 'Division', 'Revenue', 'Cost', 'Gross_Profit', 'Gross Margin (%)', 'Profit per Unit']]
            .style.format({
                'Revenue': '${:,.2f}',
                'Cost': '${:,.2f}',
                'Gross_Profit': '${:,.2f}',
                'Gross Margin (%)': '{:.2f}%',
                'Profit per Unit': '${:,.2f}'
            }),
            use_container_width=True
        )
    else:
        st.success(f"No products found below the {margin_threshold:.0f}% margin threshold.")

# -----------------------------------------------------------------------------
# MODULE 4: Profit Concentration Analysis
# -----------------------------------------------------------------------------
with tab4:
    pareto_df = prod_kpi.sort_values(by='Gross_Profit', ascending=False).reset_index(drop=True)
    pareto_df['Cumulative_Profit_%'] = (pareto_df['Gross_Profit'].cumsum() / kpi_profit * 100) if kpi_profit > 0 else 0
    
    st.markdown("#### Pareto Charts")
    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(x=pareto_df['Product Name'], y=pareto_df['Gross_Profit'], name='Gross Profit ($)', marker_color='#2563eb'))
    fig_pareto.add_trace(go.Scatter(x=pareto_df['Product Name'], y=pareto_df['Cumulative_Profit_%'], name='Cumulative Profit %', yaxis='y2', mode='lines+markers', line=dict(color='#f97316', width=2.5)))
    fig_pareto.add_hline(y=80, line_dash="dash", line_color="red", yref='y2', annotation_text="80% Threshold")
    fig_pareto.update_layout(
        height=450, margin=dict(l=20, r=20, t=30, b=20),
        yaxis=dict(title="Gross Profit ($)"),
        yaxis2=dict(title="Cumulative %", overlaying='y', side='right', range=[0, 105]),
        xaxis_tickangle=-30
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    st.markdown("#### Dependency Indicators")
    top_80_count = (pareto_df['Cumulative_Profit_%'] <= 80).sum() + 1
    total_skus = len(pareto_df)
    st.info(
        f"**Profit Concentration Finding:** Exactly **{top_80_count} of {total_skus} products** "
        f"({top_80_count / total_skus * 100:.1f}% of catalog) drive **80%** of Nassau Candy Distributor's total gross profit."
    )
