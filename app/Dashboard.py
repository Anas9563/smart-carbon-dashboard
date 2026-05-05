import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Smart Carbon Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the clean, professional look
st.markdown("""
<style>
    /* Hero Section */
    .hero-container {
        padding: 3rem 0 2rem 0;
        border-bottom: 1px solid #E9ECEF;
        margin-bottom: 2rem;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: #1A1A1A;
        margin-bottom: 0.5rem;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 1.25rem;
        color: #4A5568;
        max-width: 800px;
        line-height: 1.6;
        font-family: "Georgia", serif; /* Academic touch */
        margin-top: 1rem;
    }
    
    /* Metrics Styling */
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2F6F4F; /* Earth-tone primary green */
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #6C757D;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Card Styling */
    div[data-testid="column"] {
        background-color: #F5F7F5;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s, border-color 0.2s;
        margin-bottom: 1rem;
    }
    div[data-testid="column"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 12px -3px rgba(0, 0, 0, 0.1);
        border-color: #4C9A74;
    }
    .card-title {
        color: #1A1A1A;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #8C6A43;
        padding-bottom: 0.5rem;
        display: inline-block;
        font-weight: 700;
    }
    .card-text {
        color: #4A5568;
        font-size: 1.05rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
        flex-grow: 1;
    }

</style>
""", unsafe_allow_html=True)

# Data Loading function
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/owid-co2-data.csv")
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# Sidebar
with st.sidebar:
    st.markdown("## 🌍 Smart Carbon")
    st.markdown("An interactive platform for exploring historical and projected greenhouse gas emissions worldwide, built with open data.")
    st.markdown("---")
    st.markdown("**Data Source:**")
    st.markdown("[Our World in Data CO₂ dataset](https://github.com/owid/co2-data)")
    
    st.markdown("<br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #6C757D; font-size: 0.8rem;'>Smart Carbon Dashboard v1.0</div>", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-container">
    <div class="hero-title">Global CO₂ & Greenhouse Gas Emissions</div>
    <div class="hero-subtitle">
        Understanding the scale and distribution of global emissions is essential for tracking progress against climate goals. 
        Explore historical trends, compare national footprints, and view short-term projections based on the latest available open data.
    </div>
</div>
""", unsafe_allow_html=True)

# Key Metrics
if not df.empty and 'country' in df.columns:
    # Latest Year
    latest_year = df['year'].max()
    
    # Global Emissions for Latest Year
    world_data = df[(df['country'] == 'World') & (df['year'] == latest_year)]
    if not world_data.empty and pd.notna(world_data['co2'].values[0]):
        global_emissions = world_data['co2'].values[0] / 1000  # Convert to billion tonnes
        global_growth = world_data['co2_growth_prct'].values[0] if 'co2_growth_prct' in world_data.columns else 0
        if pd.isna(global_growth): global_growth = 0
    else:
        global_emissions = 0
        global_growth = 0
        
    # Top Emitter for Latest Year (excluding aggregates)
    countries_df = df[(df['year'] == latest_year) & (df['iso_code'].notna())]
    if not countries_df.empty:
        # Check if co2 is available, else maybe total_ghg
        if 'co2' in countries_df.columns:
            top_idx = countries_df['co2'].idxmax()
            top_emitter = countries_df.loc[top_idx]
            top_name = top_emitter['country']
            top_val = top_emitter['co2'] / 1000
        else:
            top_name = "N/A"
            top_val = 0
    else:
        top_name = "N/A"
        top_val = 0

    st.markdown(f"<h3 style='color: #1A1A1A; font-weight: 600; font-size: 1.5rem; margin-bottom: 1rem;'>Key Metrics ({int(latest_year)})</h3>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.metric(label="Global CO₂ Emissions", value=f"{global_emissions:.1f} Gt", delta=f"{global_growth:.2f}% vs previous yr", delta_color="inverse")
    
    with m2:
        st.metric(label="Largest Emitter", value=top_name, delta=f"{top_val:.1f} Gt")
        
    with m3:
        st.metric(label="Data Coverage", value=f"{len(df['country'].unique())} Regions", delta=f"Since {int(df['year'].min())}", delta_color="off")

st.markdown("<br><br>", unsafe_allow_html=True)

# Feature Navigation
st.markdown("<h3 style='color: #1A1A1A; font-weight: 600; font-size: 1.5rem; margin-bottom: 1.5rem;'>Dashboard Features</h3>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="card-title">🔍 Explorer</div>
        <div class="card-text">Dive deep into the historical emissions trajectory of individual countries. Analyze the breakdown by sector and per capita contributions over time.</div>
    """, unsafe_allow_html=True)
    if st.button("Launch Explorer", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Explorer.py")

with col2:
    st.markdown("""
        <div class="card-title">⚖️ Comparison</div>
        <div class="card-text">Benchmark regions and nations against each other. Visualize emission disparities and historical responsibility across the globe.</div>
    """, unsafe_allow_html=True)
    if st.button("Launch Comparison", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Comparison.py")

with col3:
    st.markdown("""
        <div class="card-title">📈 Predictions</div>
        <div class="card-text">View statistical short-term forecasts for country emissions using linear regression models to understand potential future trajectories.</div>
    """, unsafe_allow_html=True)
    if st.button("Launch Predictions", use_container_width=True, type="primary"):
        st.switch_page("pages/3_Predictions.py")