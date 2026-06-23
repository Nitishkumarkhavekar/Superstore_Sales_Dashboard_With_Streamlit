import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import io

# 1. Page Configuration
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS Injection (Outfit Google Font, custom cards, hover effects)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Main fonts */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif;
}

/* Page title custom styling */
.main-title {
    color: #241341;
    font-weight: 800;
    font-size: 2.5rem;
    margin-bottom: 5px;
    letter-spacing: -1px;
}
.sub-title {
    color: #999999;
    font-size: 1rem;
    margin-bottom: 25px;
    font-weight: 400;
}

/* KPI Card Styles */
.kpi-container {
    display: flex;
    gap: 15px;
    margin-bottom: 25px;
    flex-wrap: wrap;
}

.kpi-card {
    flex: 1;
    min-width: 190px;
    background: linear-gradient(135deg, #241341 0%, #3a1e67 100%);
    color: #EFF1E6;
    padding: 22px 18px;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(36, 19, 65, 0.12);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.kpi-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 30px rgba(36, 19, 65, 0.25);
    border-color: rgba(255, 255, 255, 0.15);
}

.kpi-title {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    opacity: 0.8;
    font-weight: 500;
}

.kpi-value {
    font-size: 26px;
    font-weight: 700;
    margin: 8px 0 4px 0;
    letter-spacing: -0.5px;
}

.kpi-badge {
    font-size: 11px;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    border-radius: 6px;
    padding: 3px 8px;
}

.badge-positive {
    background-color: rgba(16, 185, 129, 0.2);
    color: #10B981;
}

.badge-negative {
    background-color: rgba(239, 68, 68, 0.2);
    color: #EF4444;
}

.badge-neutral {
    background-color: rgba(153, 153, 153, 0.2);
    color: #999999;
}

/* Styled containers for charts */
.chart-container {
    background-color: #ffffff;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    border: 1px solid rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}

/* Subheaders */
h3 {
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    color: #241341 !important;
    margin-bottom: 15px !important;
}

/* Block style adjustments */
div[data-testid="stMetricValue"] > div {
    font-size: 2rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# State name to state code mapping for Choropleth Map
state_to_code = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
    'District of Columbia': 'DC'
}

# 3. Data Loading & Cleaning
@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), 'src', 'data', 'Superstore.csv')
    if not os.path.exists(csv_path):
        # Fallback if csv path is slightly different
        csv_path = 'Superstore.csv'
        
    df = pd.read_csv(csv_path)
    
    # Parse dates explicitly (DD/MM/YYYY)
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d/%m/%Y', errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%d/%m/%Y', errors='coerce')
    
    # Calculate additional metrics
    df['Shipping Delay'] = (df['Ship Date'] - df['Order Date']).dt.days
    df['Order Month'] = df['Order Date'].dt.to_period('M')
    df['Order Month Year'] = df['Order Date'].dt.strftime('%Y-%m')
    df['Order Year'] = df['Order Date'].dt.year
    df['Profit Margin'] = (df['Profit'] / df['Sales']).fillna(0) * 100
    df['State Code'] = df['State'].map(state_to_code)
    
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error(f"Error loading CSV dataset: {e}")
    st.stop()

# 4. Sidebar Branding & Navigation Menu
st.sidebar.markdown("""
<div style="text-align: center; padding: 12px 0; background: linear-gradient(135deg, #241341 0%, #3a1e67 100%); border-radius: 12px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(36, 19, 65, 0.15);">
    <h2 style="color: #EFF1E6; font-weight: 800; margin: 0; font-size: 1.4rem; letter-spacing: -0.5px;">🛒 Superstore Sales</h2>
    <p style="color: #B6B7B2; font-size: 0.75rem; margin: 4px 0 0 0; font-weight: 500;">Nitishkumar Khavekar Edition</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

from streamlit_option_menu import option_menu
with st.sidebar:
    selected_page = option_menu(
        menu_title="Dashboard Menu",
        options=["Overview", "Sales & Profit", "Product Performance", "Geographic & Shipping", "Customer Insights", "Data Explorer"],
        icons=["house", "graph-up", "cart", "globe", "people", "database"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#241341", "font-size": "16px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"2px 0px", "color": "#241341", "font-family": "Outfit"},
            "nav-link-selected": {"background-color": "#241341", "color": "#EFF1E6", "font-weight": "600"},
        }
    )

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filter Panel")

# 5. Filter Controls
# Date range setup
min_date = df_raw['Order Date'].min().to_pydatetime()
max_date = df_raw['Order Date'].max().to_pydatetime()

selected_dates = st.sidebar.date_input(
    "Select Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date = selected_dates[0] if isinstance(selected_dates, (tuple, list)) else selected_dates
    end_date = max_date

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Regional Filters
all_regions = sorted(df_raw['Region'].dropna().unique())
selected_regions = st.sidebar.multiselect("Select Region", all_regions, default=all_regions)

# Dynamic State Filter
filtered_states_df = df_raw[df_raw['Region'].isin(selected_regions)]
all_states = sorted(filtered_states_df['State'].dropna().unique())
selected_states = st.sidebar.multiselect("Select State", all_states, default=all_states)

# Dynamic City Filter
filtered_cities_df = filtered_states_df[filtered_states_df['State'].isin(selected_states)]
all_cities = sorted(filtered_cities_df['City'].dropna().unique())
selected_cities = st.sidebar.multiselect("Select City (Optional - Blank for All)", all_cities, default=[])

# Product Filters
all_categories = sorted(df_raw['Category'].dropna().unique())
selected_categories = st.sidebar.multiselect("Select Category", all_categories, default=all_categories)

filtered_subcats_df = df_raw[df_raw['Category'].isin(selected_categories)]
all_subcats = sorted(filtered_subcats_df['Sub-Category'].dropna().unique())
selected_subcats = st.sidebar.multiselect("Select Sub-Category", all_subcats, default=all_subcats)

# Segment & Ship Mode Filters
all_segments = sorted(df_raw['Segment'].dropna().unique())
selected_segments = st.sidebar.multiselect("Select Customer Segment", all_segments, default=all_segments)

all_ship_modes = sorted(df_raw['Ship Mode'].dropna().unique())
selected_ship_modes = st.sidebar.multiselect("Select Shipping Mode", all_ship_modes, default=all_ship_modes)

# Apply Filter logic
filtered_df = df_raw[
    (df_raw['Order Date'] >= start_date) &
    (df_raw['Order Date'] <= end_date) &
    (df_raw['Region'].isin(selected_regions)) &
    (df_raw['Category'].isin(selected_categories)) &
    (df_raw['Segment'].isin(selected_segments)) &
    (df_raw['Ship Mode'].isin(selected_ship_modes))
]

if selected_states:
    filtered_df = filtered_df[filtered_df['State'].isin(selected_states)]
if selected_cities:
    filtered_df = filtered_df[filtered_df['City'].isin(selected_cities)]
if selected_subcats:
    filtered_df = filtered_df[filtered_df['Sub-Category'].isin(selected_subcats)]

# 6. Global KPI Calculator
def get_kpis(df_curr, df_full, start, end):
    total_sales = df_curr['Sales'].sum()
    total_profit = df_curr['Profit'].sum()
    profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    total_orders = df_curr['Order ID'].nunique()
    avg_discount = df_curr['Discount'].mean() * 100 if len(df_curr) > 0 else 0
    
    # Calculate for previous period of same duration
    days = (end - start).days
    prior_start = start - pd.Timedelta(days=days)
    prior_end = start - pd.Timedelta(days=1)
    
    df_prior = df_full[
        (df_full['Order Date'] >= prior_start) &
        (df_full['Order Date'] <= prior_end)
    ]
    
    prior_sales = df_prior['Sales'].sum()
    prior_profit = df_prior['Profit'].sum()
    prior_margin = (prior_profit / prior_sales * 100) if prior_sales > 0 else 0
    prior_orders = df_prior['Order ID'].nunique()
    prior_discount = df_prior['Discount'].mean() * 100 if len(df_prior) > 0 else 0
    
    # Deltas
    sales_delta = ((total_sales - prior_sales) / prior_sales * 100) if prior_sales > 0 else 0
    profit_delta = ((total_profit - prior_profit) / prior_profit * 100) if prior_profit > 0 else 0
    margin_delta = profit_margin - prior_margin
    orders_delta = ((total_orders - prior_orders) / prior_orders * 100) if prior_orders > 0 else 0
    discount_delta = avg_discount - prior_discount
    
    return {
        "sales": total_sales, "sales_delta": sales_delta,
        "profit": total_profit, "profit_delta": profit_delta,
        "margin": profit_margin, "margin_delta": margin_delta,
        "orders": total_orders, "orders_delta": orders_delta,
        "discount": avg_discount, "discount_delta": discount_delta
    }

kpis = get_kpis(filtered_df, df_raw, start_date, end_date)

# Display KPI cards
def draw_kpi_card_html(title, value, delta, is_percentage=False, is_currency=False, is_margin=False):
    if delta > 0:
        badge_class = "badge-positive"
        symbol = "▲"
        delta_str = f"+{delta:.1f}%" if not is_margin else f"+{delta:.1f}% pts"
    elif delta < 0:
        badge_class = "badge-negative"
        symbol = "▼"
        delta_str = f"{delta:.1f}%" if not is_margin else f"{delta:.1f}% pts"
    else:
        badge_class = "badge-neutral"
        symbol = "▬"
        delta_str = "0.0%"
        
    if is_currency:
        val_str = f"${value:,.2f}" if value < 10000 else f"${value:,.0f}"
    elif is_percentage:
        val_str = f"{value:.1f}%"
    else:
        val_str = f"{value:,}"
        
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{val_str}</div>
        <div class="kpi-badge {badge_class}">
            <span style="margin-right: 4px;">{symbol}</span> {delta_str}
        </div>
    </div>
    """

# 7. Rendering Selected Menu Page
if len(filtered_df) == 0:
    st.warning("⚠️ No data matches current filters. Please relax your criteria in the sidebar filter panel.")
else:
    # App Title Header
    st.markdown(f"<div class='main-title'>Superstore Sales Analysis</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-title'>Analyzing sales from {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}</div>", unsafe_allow_html=True)
    
    # KPI metrics panel (Render on all dashboard pages except Explorer)
    if selected_page != "Data Explorer":
        kpi_cols = st.columns(5)
        with kpi_cols[0]:
            st.markdown(draw_kpi_card_html("Total Sales", kpis["sales"], kpis["sales_delta"], is_currency=True), unsafe_allow_html=True)
        with kpi_cols[1]:
            st.markdown(draw_kpi_card_html("Total Profit", kpis["profit"], kpis["profit_delta"], is_currency=True), unsafe_allow_html=True)
        with kpi_cols[2]:
            st.markdown(draw_kpi_card_html("Profit Margin", kpis["margin"], kpis["margin_delta"], is_percentage=True, is_margin=True), unsafe_allow_html=True)
        with kpi_cols[3]:
            st.markdown(draw_kpi_card_html("Total Orders", kpis["orders"], kpis["orders_delta"]), unsafe_allow_html=True)
        with kpi_cols[4]:
            st.markdown(draw_kpi_card_html("Avg Discount", kpis["discount"], kpis["discount_delta"], is_percentage=True), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

    # ---------------- PAGE 1: OVERVIEW ----------------
    if selected_page == "Overview":
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Monthly Sales & Profit Performance")
            
            # Aggregate by month
            monthly_data = filtered_df.groupby('Order Month Year').agg({'Sales':'sum', 'Profit':'sum'}).reset_index()
            monthly_data = monthly_data.sort_values('Order Month Year')
            
            fig = go.Figure()
            # Sales bars
            fig.add_trace(go.Bar(
                x=monthly_data['Order Month Year'],
                y=monthly_data['Sales'],
                name='Sales',
                marker_color='#3498db',
                opacity=0.85
            ))
            # Profit line
            fig.add_trace(go.Scatter(
                x=monthly_data['Order Month Year'],
                y=monthly_data['Profit'],
                name='Profit',
                line=dict(color='#e74c3c', width=3),
                mode='lines+markers'
            ))
            
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=10, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor='#F0F0F0', title="Amount ($)"),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Sales by Customer Segment")
            
            segment_sales = filtered_df.groupby('Segment')['Sales'].sum().reset_index()
            fig_pie = px.pie(
                segment_sales,
                values='Sales',
                names='Segment',
                hole=0.5,
                color_discrete_sequence=['#3498db', '#2ecc71', '#e74c3c']
            )
            fig_pie.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=350,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        col3, col4 = st.columns([1, 1])
        
        with col3:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Sales by Product Category")
            
            cat_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=True)
            fig_cat = px.bar(
                cat_sales,
                x='Sales',
                y='Category',
                orientation='h',
                color='Category',
                color_discrete_sequence=['#9b59b6', '#f39c12', '#1abc9c'],
                text_auto='.2s'
            )
            fig_cat.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=10, b=20),
                xaxis=dict(gridcolor='#F0F0F0'),
                yaxis=dict(showgrid=False),
                showlegend=False,
                height=300
            )
            st.plotly_chart(fig_cat, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col4:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Top 5 States by Sales Volume")
            
            state_sales = filtered_df.groupby('State')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(5)
            # sort ascending for horizontal bar chart
            state_sales = state_sales.sort_values('Sales', ascending=True)
            fig_state = px.bar(
                state_sales,
                x='Sales',
                y='State',
                orientation='h',
                color='State',
                color_discrete_sequence=px.colors.qualitative.Vivid,
                text_auto='.2s'
            )
            fig_state.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=10, b=20),
                xaxis=dict(gridcolor='#F0F0F0'),
                yaxis=dict(showgrid=False),
                showlegend=False,
                height=300
            )
            st.plotly_chart(fig_state, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Raw Data Preview
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("📋 Filtered Raw Data Preview")
        st.write("Below is a quick preview of the first 50 rows matching your current filters. For full details, column customisations, search, and CSV/Excel downloads, navigate to the **Data Explorer** tab.")
        
        preview_df = filtered_df.head(50).copy()
        for col in preview_df.columns:
            if pd.api.types.is_datetime64_any_dtype(preview_df[col]):
                preview_df[col] = preview_df[col].dt.strftime('%Y-%m-%d')
                
        st.dataframe(preview_df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- PAGE 2: SALES & PROFIT ----------------
    elif selected_page == "Sales & Profit":
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Month-over-Month Sales Growth (%)")
            
            monthly_growth = filtered_df.groupby('Order Month Year')['Sales'].sum().reset_index()
            monthly_growth = monthly_growth.sort_values('Order Month Year')
            monthly_growth['Growth Rate'] = monthly_growth['Sales'].pct_change() * 100
            monthly_growth = monthly_growth.dropna()
            
            fig_growth = px.line(
                monthly_growth,
                x='Order Month Year',
                y='Growth Rate',
                markers=True,
                color_discrete_sequence=['#241341']
            )
            fig_growth.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=10, b=20),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor='#F0F0F0', title="Growth Rate (%)"),
                height=320
            )
            st.plotly_chart(fig_growth, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Category Profit Margins (%)")
            
            cat_profit = filtered_df.groupby('Category').agg({'Sales':'sum', 'Profit':'sum'}).reset_index()
            cat_profit['Margin'] = (cat_profit['Profit'] / cat_profit['Sales']) * 100
            cat_profit = cat_profit.sort_values('Margin', ascending=False)
            
            fig_margin = px.bar(
                cat_profit,
                x='Category',
                y='Margin',
                color='Category',
                color_discrete_sequence=['#241341', '#B6B7B2', '#999999'],
                text_auto='.1f'
            )
            fig_margin.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=10, b=20),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor='#F0F0F0', title="Margin (%)"),
                showlegend=False,
                height=320
            )
            st.plotly_chart(fig_margin, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Detailed Sub-Category Profitability Matrix")
        
        # Matrix: Segment vs Sub-Category Profit Margin
        pivot_df = filtered_df.groupby(['Sub-Category', 'Segment']).agg({'Sales':'sum', 'Profit':'sum'}).reset_index()
        pivot_df['Margin'] = (pivot_df['Profit'] / pivot_df['Sales']) * 100
        
        pivot_table = pivot_df.pivot(index='Sub-Category', columns='Segment', values='Margin').round(1)
        
        fig_heat = px.imshow(
            pivot_table,
            labels=dict(x="Customer Segment", y="Product Sub-Category", color="Profit Margin (%)"),
            color_continuous_scale=[[0, '#EF4444'], [0.4, '#FCA5A5'], [0.5, '#EFF1E6'], [0.6, '#A7F3D0'], [1, '#10B981']],
            color_continuous_midpoint=0
        )
        fig_heat.update_layout(
            margin=dict(l=20, r=20, t=10, b=20),
            height=400
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- PAGE 3: PRODUCT PERFORMANCE ----------------
    elif selected_page == "Product Performance":
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Sales vs Profit Correlation by Sub-Category")
        
        subcat_summary = filtered_df.groupby(['Sub-Category', 'Category']).agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Discount': 'mean',
            'Quantity': 'sum'
        }).reset_index()
        subcat_summary['Discount %'] = subcat_summary['Discount'] * 100
        
        fig_scatter = px.scatter(
            subcat_summary,
            x='Sales',
            y='Profit',
            size='Quantity',
            color='Category',
            hover_name='Sub-Category',
            text='Sub-Category',
            size_max=45,
            color_discrete_sequence=['#241341', '#999999', '#B6B7B2'],
            hover_data={'Discount %': ':.1f'}
        )
        fig_scatter.update_traces(textposition='top center')
        fig_scatter.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=20, r=20, t=10, b=20),
            xaxis=dict(gridcolor='#F0F0F0', title="Total Sales ($)"),
            yaxis=dict(gridcolor='#F0F0F0', title="Total Profit ($)", zeroline=True, zerolinecolor='#999999'),
            height=400
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Top 10 Most Profitable Products")
            
            top_prod_profit = filtered_df.groupby('Product Name')['Profit'].sum().reset_index().sort_values('Profit', ascending=False).head(10)
            top_prod_profit = top_prod_profit.sort_values('Profit', ascending=True)
            
            fig_prod_profit = px.bar(
                top_prod_profit,
                x='Profit',
                y='Product Name',
                orientation='h',
                color_discrete_sequence=['#10B981']
            )
            # Cleanup names for visual clarity
            fig_prod_profit.update_yaxes(tickmode='array', tickvals=top_prod_profit['Product Name'], 
                                        ticktext=[name[:35]+'...' if len(name)>35 else name for name in top_prod_profit['Product Name']])
            fig_prod_profit.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=10, b=20),
                xaxis=dict(gridcolor='#F0F0F0'),
                yaxis=dict(showgrid=False, title=None),
                height=350
            )
            st.plotly_chart(fig_prod_profit, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Top 10 Loss-Making Products")
            
            bottom_prod_profit = filtered_df.groupby('Product Name')['Profit'].sum().reset_index().sort_values('Profit', ascending=True).head(10)
            # Sort descending negative values to show biggest losses first in graph
            bottom_prod_profit = bottom_prod_profit.sort_values('Profit', ascending=False)
            
            fig_bottom_profit = px.bar(
                bottom_prod_profit,
                x='Profit',
                y='Product Name',
                orientation='h',
                color_discrete_sequence=['#EF4444']
            )
            fig_bottom_profit.update_yaxes(tickmode='array', tickvals=bottom_prod_profit['Product Name'], 
                                           ticktext=[name[:35]+'...' if len(name)>35 else name for name in bottom_prod_profit['Product Name']])
            fig_bottom_profit.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=10, b=20),
                xaxis=dict(gridcolor='#F0F0F0'),
                yaxis=dict(showgrid=False, title=None),
                height=350
            )
            st.plotly_chart(fig_bottom_profit, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- PAGE 4: GEOGRAPHIC & SHIPPING ----------------
    elif selected_page == "Geographic & Shipping":
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Geographical Distribution of Sales by State")
            
            state_data = filtered_df.groupby(['State', 'State Code'])[['Sales', 'Profit']].sum().reset_index()
            
            fig_map = px.choropleth(
                state_data,
                locations='State Code',
                locationmode='USA-states',
                color='Sales',
                scope='usa',
                color_continuous_scale='Viridis',
                hover_data=['State', 'Profit']
            )
            fig_map.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='rgb(255, 255, 255)'),
                height=380
            )
            st.plotly_chart(fig_map, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Average Shipping Delay (Days) by Shipping Mode")
            
            ship_delay = filtered_df.groupby('Ship Mode')['Shipping Delay'].mean().reset_index().sort_values('Shipping Delay')
            
            fig_ship = px.bar(
                ship_delay,
                x='Ship Mode',
                y='Shipping Delay',
                color='Ship Mode',
                color_discrete_sequence=['#241341', '#999999', '#B6B7B2', '#d2d3d0'],
                text_auto='.1f'
            )
            fig_ship.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=10, b=20),
                xaxis=dict(showgrid=False, title="Shipping Mode"),
                yaxis=dict(gridcolor='#F0F0F0', title="Average Delay (Days)"),
                showlegend=False,
                height=380
            )
            st.plotly_chart(fig_ship, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Shipping Delay Trend over Time")
        
        # Calculate shipping delay trend
        ship_trend = filtered_df.groupby('Order Month Year')['Shipping Delay'].mean().reset_index().sort_values('Order Month Year')
        
        fig_ship_trend = px.line(
            ship_trend,
            x='Order Month Year',
            y='Shipping Delay',
            markers=True,
            color_discrete_sequence=['#241341']
        )
        fig_ship_trend.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=20, r=20, t=10, b=20),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor='#F0F0F0', title="Average Delay (Days)"),
            height=300
        )
        st.plotly_chart(fig_ship_trend, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- PAGE 5: CUSTOMER INSIGHTS ----------------
    elif selected_page == "Customer Insights":
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Top 10 Customers by Sales Value")
            
            top_cust_sales = filtered_df.groupby('Customer Name')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(10)
            top_cust_sales = top_cust_sales.sort_values('Sales', ascending=True)
            
            fig_cust_sales = px.bar(
                top_cust_sales,
                x='Sales',
                y='Customer Name',
                orientation='h',
                color_discrete_sequence=['#241341'],
                text_auto='.2s'
            )
            fig_cust_sales.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=10, b=20),
                xaxis=dict(gridcolor='#F0F0F0'),
                yaxis=dict(showgrid=False, title=None),
                height=380
            )
            st.plotly_chart(fig_cust_sales, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.subheader("Top 10 Customers by Net Profit")
            
            top_cust_profit = filtered_df.groupby('Customer Name')['Profit'].sum().reset_index().sort_values('Profit', ascending=False).head(10)
            top_cust_profit = top_cust_profit.sort_values('Profit', ascending=True)
            
            fig_cust_profit = px.bar(
                top_cust_profit,
                x='Profit',
                y='Customer Name',
                orientation='h',
                color_discrete_sequence=['#10B981'],
                text_auto='.2s'
            )
            fig_cust_profit.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=20, r=20, t=10, b=20),
                xaxis=dict(gridcolor='#F0F0F0'),
                yaxis=dict(showgrid=False, title=None),
                height=380
            )
            st.plotly_chart(fig_cust_profit, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Purchase Frequency Distribution per Customer")
        
        # Calculate orders per customer
        cust_orders = filtered_df.groupby('Customer Name')['Order ID'].nunique().reset_index()
        
        fig_dist = px.histogram(
            cust_orders,
            x='Order ID',
            nbins=15,
            color_discrete_sequence=['#999999'],
            labels={'Order ID': 'Number of Orders Placed'}
        )
        fig_dist.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=20, r=20, t=10, b=20),
            xaxis=dict(gridcolor='#F0F0F0', title="Orders Count"),
            yaxis=dict(gridcolor='#F0F0F0', title="Customers Count"),
            height=300
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- PAGE 6: DATA EXPLORER ----------------
    elif selected_page == "Data Explorer":
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Interactive Dataset Explorer")
        st.write("Browse, query, and analyze the metadata of the filtered transaction-level Superstore dataset.")
        
        # Tabs
        tab_table, tab_diag = st.tabs(["🔍 Browse & Export Data", "📊 Metadata & Data Diagnostics"])
        
        explorer_df = filtered_df.copy()
        
        with tab_table:
            # Search input
            search_query = st.text_input("🔍 Search Product Name or Customer Name", "")
            
            table_df = explorer_df.copy()
            if search_query:
                table_df = table_df[
                    table_df['Product Name'].str.contains(search_query, case=False, na=False) |
                    table_df['Customer Name'].str.contains(search_query, case=False, na=False)
                ]
            
            # Column selections
            all_cols = list(table_df.columns)
            default_cols = ['Order ID', 'Order Date', 'Customer Name', 'Segment', 'State', 'Category', 'Sub-Category', 'Product Name', 'Sales', 'Profit']
            selected_cols = st.multiselect("Display Columns", all_cols, default=default_cols)
            
            # Format dates for table display
            display_df = table_df[selected_cols].copy()
            for col in display_df.columns:
                if pd.api.types.is_datetime64_any_dtype(display_df[col]):
                    display_df[col] = display_df[col].dt.strftime('%Y-%m-%d')
                    
            st.dataframe(display_df, use_container_width=True, height=450)
            
            # Export Data Buttons
            col_btn1, col_btn2, _ = st.columns([1, 1, 3])
            
            with col_btn1:
                # CSV Download
                csv_buffer = io.StringIO()
                table_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📥 Download Data as CSV",
                    data=csv_buffer.getvalue(),
                    file_name="superstore_filtered_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            with col_btn2:
                # Excel Download
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    table_df.to_excel(writer, index=False, sheet_name='Superstore Data')
                st.download_button(
                    label="📥 Download Data as Excel",
                    data=excel_buffer.getvalue(),
                    file_name="superstore_filtered_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
        with tab_diag:
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("### Dataset Health & Information")
            
            # Diagnostic Metrics
            col_d1, col_d2, col_d3, col_d4 = st.columns(4)
            with col_d1:
                st.metric("Total Rows", f"{len(explorer_df):,}")
            with col_d2:
                st.metric("Total Columns", f"{len(explorer_df.columns)}")
            with col_d3:
                st.metric("Duplicate Rows", f"{explorer_df.duplicated().sum()}")
            with col_d4:
                mem_bytes = explorer_df.memory_usage(deep=True).sum()
                mem_str = f"{mem_bytes / 1024:.1f} KB" if mem_bytes < 1024*1024 else f"{mem_bytes / (1024*1024):.2f} MB"
                st.metric("Memory Footprint", mem_str)
                
            st.markdown("---")
            
            # Sub-columns for Data Info and Missing Values
            col_info, col_missing = st.columns(2)
            
            with col_info:
                st.markdown("#### 📋 Column Dtypes & Unique Counts")
                info_data = []
                for col in explorer_df.columns:
                    info_data.append({
                        "Column": col,
                        "Data Type": str(explorer_df[col].dtype),
                        "Unique Values": explorer_df[col].nunique()
                    })
                st.dataframe(pd.DataFrame(info_data), use_container_width=True, hide_index=True)
                
            with col_missing:
                st.markdown("#### ⚠️ Missing Values Analysis")
                missing_count = explorer_df.isna().sum()
                missing_pct = (explorer_df.isna().sum() / len(explorer_df)) * 100
                missing_df = pd.DataFrame({
                    "Column": explorer_df.columns,
                    "Missing Count": missing_count,
                    "Missing Percentage": missing_pct
                }).reset_index(drop=True)
                
                if missing_count.sum() == 0:
                    st.success("🎉 Excellent! No missing values detected in the current filtered dataset.")
                else:
                    st.warning(f"⚠️ Found {missing_count.sum()} missing values across columns.")
                st.dataframe(missing_df.style.format({"Missing Percentage": "{:.1f}%"}), use_container_width=True, hide_index=True)
                
            st.markdown("---")
            st.markdown("#### 🔢 Numerical Columns Summary Statistics")
            num_stats = explorer_df.describe().T.reset_index().rename(columns={"index": "Column"})
            st.dataframe(num_stats.style.format({
                "mean": "{:,.2f}", "std": "{:,.2f}", "min": "{:,.2f}", 
                "25%": "{:,.2f}", "50%": "{:,.2f}", "75%": "{:,.2f}", "max": "{:,.2f}"
            }), use_container_width=True, hide_index=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

# 8. Dashboard Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #999999; font-size: 12px; margin-top: 20px;'>"
    "© 2026 Nitishkumar Khavekar. All rights reserved."
    "</div>",
    unsafe_allow_html=True
)
