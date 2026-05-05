import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Explore Emissions Data", layout="wide")

# --- Global Styles ---
st.markdown("""
<style>
            /* Global Font Match - Dashboard Consistency */
    h1, h2, h3, h4 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-weight: 800;
        color: #1A1A1A;
    }
    p, div, span, label {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #2c3e50;
        padding-bottom: 6px;
        border-bottom: 3px solid #4a7c59;
        margin-bottom: 16px;
        margin-top: 8px;
    }
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        text-align: center;
        border-top: 4px solid #4a7c59;
    }
    .kpi-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1a1a2e;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 4px;
    }
    .kpi-up { color: #dc2626; }
    .kpi-down { color: #16a34a; }
    .kpi-neutral { color: #64748b; }
    .stat-box {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        height: 100%;
    }
    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #f1f5f9;
        font-size: 0.88rem;
    }
    .stat-row:last-child { border-bottom: none; }
    .stat-name { color: #6b7280; }
    .stat-val { font-weight: 700; color: #1a1a2e; }
    .trend-down { color: #16a34a; font-weight: 700; }
    .trend-up { color: #dc2626; font-weight: 700; }
    .trend-stable { color: #64748b; font-weight: 700; }
    .sidebar-card {
        background: #f0f7f4;
        border-left: 4px solid #4a7c59;
        border-radius: 0 6px 6px 0;
        padding: 12px 14px;
        font-size: 0.82rem;
        color: #374151;
        margin-top: 8px;
        line-height: 1.6;
    }
    .page-subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-top: -12px;
        margin-bottom: 20px;
        font-family: "Georgia", serif;
        line-height: 1.6;
            
    }
</style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv("data/cleaned_co2.csv")

df = load_data()
df_analysis = df[
    (df["iso_code"].notna()) &
    (df["iso_code"].str.len() == 3)
].copy()

# --- Gas Type Mapping ---
gas_options = {
    "CO₂ Emissions": {"column": "co2", "unit": "Mt", "label": "CO₂ Emissions (million tonnes)"},
    "CO₂ Per Capita": {"column": "co2_per_capita", "unit": "t/person", "label": "CO₂ Per Capita (tonnes per person)"},
    "Total Greenhouse Gases": {"column": "total_ghg", "unit": "Mt CO₂e", "label": "Total GHG Emissions (million tonnes CO₂e)"},
    "Methane": {"column": "methane", "unit": "Mt CO₂e", "label": "Methane Emissions (million tonnes CO₂e)"},
    "Nitrous Oxide": {"column": "nitrous_oxide", "unit": "Mt CO₂e", "label": "Nitrous Oxide Emissions (million tonnes CO₂e)"}
}

# --- Sidebar ---
st.sidebar.header("Filters")

country = st.sidebar.selectbox(
    "Select Country",
    sorted(df_analysis["country"].dropna().unique())
)

gas_choice = st.sidebar.selectbox(
    "Select Emission Type",
    list(gas_options.keys())
)

year_range = st.sidebar.slider(
    "Select Year Range",
    int(df_analysis["year"].min()),
    int(df_analysis["year"].max()),
    (1960, 2022)
)

# --- Get selected gas config ---
selected_gas = gas_options[gas_choice]
gas_col = selected_gas["column"]
gas_unit = selected_gas["unit"]
gas_label = selected_gas["label"]

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="sidebar-card">
    <strong>About this page</strong><br>
    Explore historical emissions for any country from 1960 onwards.
    Select different emission types to explore CO₂, greenhouse gases,
    methane and more. Data sourced from Our World in Data.
</div>
""", unsafe_allow_html=True)

# --- Filter Data ---
country_df = df_analysis[
    (df_analysis["country"] == country) &
    (df_analysis["year"] >= year_range[0]) &
    (df_analysis["year"] <= year_range[1])
].copy()

country_df_co2 = country_df.dropna(subset=[gas_col]).sort_values("year")

# --- Page Header ---
st.title("Explore Emissions Data")
st.markdown(
    '<p class="page-subtitle">Explore historical emissions trends for a single country across time. Select from CO₂, greenhouse gases, methane and more.</p>',
    unsafe_allow_html=True
)
st.caption("This page uses data from 1960 onwards to align with the exploratory data analysis stage.")

if country_df_co2.empty:
    st.warning(f"No data available for **{country}** — **{gas_choice}** in the selected year range.")
else:
    # --- Compute Stats ---
    latest_value = country_df_co2[gas_col].iloc[-1]
    latest_year = int(country_df_co2["year"].iloc[-1])
    start_value = country_df_co2[gas_col].iloc[0]
    start_year = int(country_df_co2["year"].iloc[0])

    peak_value = country_df_co2[gas_col].max()
    peak_year = int(country_df_co2.loc[country_df_co2[gas_col].idxmax(), "year"])

    lowest_value = country_df_co2[gas_col].min()
    lowest_year = int(country_df_co2.loc[country_df_co2[gas_col].idxmin(), "year"])

    avg_value = country_df_co2[gas_col].mean()
    years_of_data = country_df_co2["year"].nunique()

    total_change = latest_value - start_value
    change_class = "kpi-down" if total_change < 0 else "kpi-up"
    change_arrow = "↓" if total_change < 0 else "↑"

    # Overall trend based on total change across selected range
    if total_change > 0:
        trend_label = "Rising"
        trend_class = "kpi-up"
        trend_arrow = "↑"
        trend_stat_class = "trend-up"
    elif total_change < 0:
        trend_label = "Declining"
        trend_class = "kpi-down"
        trend_arrow = "↓"
        trend_stat_class = "trend-down"
    else:
        trend_label = "Stable"
        trend_class = "kpi-neutral"
        trend_arrow = "→"
        trend_stat_class = "trend-stable"

    # --- KPI Cards ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Latest Emissions</div>
            <div class="kpi-value">{latest_value:.1f} {gas_unit}</div>
            <div class="kpi-sub">{latest_year}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Peak Emissions</div>
            <div class="kpi-value">{peak_value:.1f} {gas_unit}</div>
            <div class="kpi-sub">{peak_year}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Change</div>
            <div class="kpi-value {change_class}">{change_arrow} {abs(total_change):.1f} {gas_unit}</div>
            <div class="kpi-sub">since {start_year}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Overall Trend</div>
            <div class="kpi-value {trend_class}">{trend_arrow} {trend_label}</div>
            <div class="kpi-sub">since {start_year}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Chart + Stats ---
    st.markdown(f'<div class="section-header">{gas_choice} Over Time</div>', unsafe_allow_html=True)

    chart_type = st.radio(
        "Chart type",
        ["Line Chart", "Bar Chart"],
        horizontal=True,
        label_visibility="collapsed"
    )

    col_chart, col_stats = st.columns([3, 1])

    with col_chart:
        fig = go.Figure()

        if chart_type == "Line Chart":
            fig.add_trace(go.Scatter(
                x=country_df_co2["year"],
                y=country_df_co2[gas_col],
                mode="lines",
                name=gas_choice,
                line=dict(color="#4a7c59", width=2.5),
                fill="tozeroy",
                fillcolor="rgba(74,124,89,0.08)"
            ))

            fig.add_trace(go.Scatter(
                x=[peak_year],
                y=[peak_value],
                mode="markers+text",
                name=f"Peak ({peak_year})",
                marker=dict(color="#dc2626", size=9),
                text=[f"Peak {peak_year}"],
                textposition="top center",
                textfont=dict(size=11, color="#dc2626")
            ))

        else:
            fig.add_trace(go.Bar(
                x=country_df_co2["year"],
                y=country_df_co2[gas_col],
                name=gas_choice,
                marker_color="#4a7c59",
                marker_opacity=0.8
            ))

            fig.add_trace(go.Scatter(
                x=[peak_year],
                y=[peak_value],
                mode="markers+text",
                name=f"Peak ({peak_year})",
                marker=dict(color="#dc2626", size=9),
                text=[f"Peak {peak_year}"],
                textposition="top center",
                textfont=dict(size=11, color="#dc2626")
            ))

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title=gas_label,
            height=400,
            plot_bgcolor="#fafafa",
            paper_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#e2e8f0",
                borderwidth=1
            ),
            xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0"),
            yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0"),
            margin=dict(t=20, b=40),
            bargap=0.1
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_stats:
        st.markdown(f"""
        <div class="stat-box">
            <div class="section-header">Summary Statistics</div>
            <div class="stat-row">
                <span class="stat-name">Average</span>
                <span class="stat-val">{avg_value:.1f} {gas_unit}</span>
            </div>
            <div class="stat-row">
                <span class="stat-name">Peak year</span>
                <span class="stat-val">{peak_year}</span>
            </div>
            <div class="stat-row">
                <span class="stat-name">Lowest year</span>
                <span class="stat-val">{lowest_year}</span>
            </div>
            <div class="stat-row">
                <span class="stat-name">Years of data</span>
                <span class="stat-val">{years_of_data}</span>
            </div>
            <div class="stat-row">
                <span class="stat-name">Overall trend</span>
                <span class="{trend_stat_class}">{trend_arrow} {trend_label}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Download ---
    st.markdown('<div class="section-header">Download Data</div>', unsafe_allow_html=True)

    csv = country_df_co2[["year", gas_col]].to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"⬇️ Download {gas_choice} Data (CSV)",
        data=csv,
        file_name=f"{country}_{gas_col}_{year_range[0]}_{year_range[1]}.csv",
        mime="text/csv"
    )