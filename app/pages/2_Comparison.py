import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Emissions Comparison | Smart Carbon", 
    page_icon="🌍", 
    layout="wide"
)
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
    .page-subtitle {
        font-family: "Georgia", serif;
        line-height: 1.6;
        color: #4A5568;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)
# --- HEADER SECTION ---
st.title("🌍 Comparative Emissions Analysis")
st.markdown(
    """
    <p class="page-subtitle">
    Understand the global distribution of emissions. 
    This tool allows you to conduct structured, comparative explorations of historical climate data 
    at both the national and continental levels.
    </p>
    """,
    unsafe_allow_html=True
)
st.divider()

# --- DATA LOADING ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/cleaned_co2.csv")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Analysis Parameters")
st.sidebar.markdown("Adjust the parameters to refine the analysis.")

# Define standard continents for mapping and filtering
CONTINENTS = [
    "Africa", "Asia", "Europe", "North America", 
    "South America", "Oceania"
]

# Get valid countries (those with iso_codes usually) and exclude regions/continents
valid_countries = df[df["iso_code"].notna()]["country"].dropna().unique()
country_options = sorted([c for c in valid_countries if c not in CONTINENTS])

countries = st.sidebar.multiselect(
    "Select Countries for Analysis",
    options=country_options,
    default=["United Kingdom", "United States", "China", "India", "Germany"]
)

min_year = int(df["year"].min())
max_year = int(df["year"].max())
year_range = st.sidebar.slider(
    "Select Timeline (Years)",
    min_value=min_year,
    max_value=max_year,
    value=(1990, 2022)
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="font-size: 0.85em; color: gray;">
    <b>Note:</b> Data availability may vary by country, metric, and year.
    </div>
    """, 
    unsafe_allow_html=True
)

# --- SECTION 1: COUNTRY COMPARISON ---
st.subheader("National Emissions Trends")
st.markdown("Analyse localised climate impact by comparing specific nations across different emission metrics.")

metric_mapping = {
    "CO₂ Emissions": {
        "column": "co2",
        "y_label": "CO₂ Emissions (million tonnes)",
        "title": "Annual CO₂ Emissions by Country"
    },
    "CO₂ Per Capita": {
        "column": "co2_per_capita",
        "y_label": "CO₂ Per Capita (tonnes)",
        "title": "Per Capita CO₂ Emissions by Country"
    },
    "Total Greenhouse Gas Emissions": {
        "column": "total_ghg",
        "y_label": "Total GHG (million tonnes of CO₂e)",
        "title": "Total Greenhouse Gas Emissions by Country"
    }
}

if "chart_type" not in st.session_state:
    st.session_state.chart_type = "📈"

def set_chart_type(c_type):
    st.session_state.chart_type = c_type

col_metric, col_spacer, col_toggle = st.columns([1, 1.2, 0.8])
with col_metric:
    metric_choice = st.selectbox(
        "Select Evaluation Metric:",
        options=list(metric_mapping.keys())
    )

with col_toggle:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    t1, t2, t3 = st.columns(3)
    
    with t1:
        st.button("📈", key="btn_line", help="Line Chart", use_container_width=True,
                  type="primary" if st.session_state.chart_type == "📈" else "secondary",
                  on_click=set_chart_type, args=("📈",))
    with t2:
        st.button("📊", key="btn_bar", help="Bar Chart", use_container_width=True,
                  type="primary" if st.session_state.chart_type == "📊" else "secondary",
                  on_click=set_chart_type, args=("📊",))
    with t3:
        st.button("🌍", key="btn_map", help="Map", use_container_width=True,
                  type="primary" if st.session_state.chart_type == "🌍" else "secondary",
                  on_click=set_chart_type, args=("🌍",))

selected_metric_info = metric_mapping[metric_choice]
metric_col = selected_metric_info["column"]

# Filter Data
country_df = df[
    (df["country"].isin(countries)) &
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
]

# Plot Country Chart
if not country_df.empty:
    if st.session_state.chart_type == "📈":
        fig_country = px.line(
            country_df,
            x="year",
            y=metric_col,
            color="country",
            title=selected_metric_info["title"],
            labels={
                metric_col: selected_metric_info["y_label"],
                "year": "Year",
                "country": "Country"
            },
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig_country.update_layout(
            hovermode="x unified",
            legend_title_text="Nation",
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(size=13)
        )
        st.plotly_chart(fig_country, use_container_width=True)
        # --- Key Insight ---
        latest_year_data = country_df[
            country_df["year"] == country_df["year"].max()
        ].dropna(subset=[metric_col])

        if len(latest_year_data) >= 2:
            top_country = latest_year_data.loc[latest_year_data[metric_col].idxmax()]
            bottom_country = latest_year_data.loc[latest_year_data[metric_col].idxmin()]
            ratio = top_country[metric_col] / bottom_country[metric_col] if bottom_country[metric_col] > 0 else 0
            latest_yr = int(latest_year_data["year"].iloc[0])

            st.markdown(f"""
            <div style="border-left: 4px solid #4a7c59; border-radius: 0 6px 6px 0;
            padding: 12px 16px; margin-top: 8px; background: #f0f7f4;">
                <div style="font-size: 11px; font-weight: 600; color: #4a7c59;
                letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 5px;">
                Key Insight</div>
                <p style="font-size: 0.9rem; color: #374151; margin: 0; line-height: 1.6;">
                In <strong>{latest_yr}</strong>, <strong>{top_country['country']}</strong> 
                was the largest emitter at <strong>{top_country[metric_col]:,.1f} {selected_metric_info['y_label'].split('(')[1].replace(')','')}</strong> — 
                approximately <strong>{ratio:.1f}x</strong> more than 
                <strong>{bottom_country['country']}</strong>.
                </p>
            </div>
            """, unsafe_allow_html=True)
    elif st.session_state.chart_type == "📊":
        latest_year = country_df["year"].max()
        bar_df = country_df[country_df["year"] == latest_year]
        
        fig_bar = px.bar(
            bar_df,
            x="country",
            y=metric_col,
            color="country",
            title=f"{selected_metric_info['title']} ({latest_year})",
            labels={
                metric_col: selected_metric_info["y_label"],
                "country": "Country"
            },
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig_bar.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(size=13)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    elif st.session_state.chart_type == "🌍":
        map_year = year_range[1]
        map_df = df[(df["year"] == map_year) & (df["iso_code"].notna())].copy()
        
        # Determine if a country is selected to adjust its border
        map_df['is_selected'] = map_df['country'].isin(countries)
        
        fig_map = px.choropleth(
            map_df,
            locations="iso_code",
            color=metric_col,
            hover_name="country",
            color_continuous_scale="Greens",
            title=f"{selected_metric_info['title']} ({map_year})",
            labels={metric_col: selected_metric_info["y_label"]},
            template="plotly_white"
        )
        
        # Highlight selected countries with thicker and red borders
        fig_map.update_traces(
            marker_line_width=[2 if selected else 0.5 for selected in map_df['is_selected']],
            marker_line_color=["red" if selected else "lightgray" for selected in map_df['is_selected']]
        )
        
        fig_map.update_geos(
            projection_type="natural earth",
            showcountries=True,
            countrycolor="lightgray",
            countrywidth=0.5,
            bgcolor="rgba(0,0,0,0)"
        )
        
        fig_map.update_layout(
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(size=13),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_map, use_container_width=True)

else:
    st.info("No data available for the selected filters. Please adjust the sidebar controls.")

st.markdown("<br>", unsafe_allow_html=True)

# --- SECTION 2: CONTINENT COMPARISON ---
st.divider()
st.subheader("Continental Emissions Overview")
st.markdown("Observe the macroscopic shifts in CO₂ emissions across global regions over time.")

if "continent_chart_type" not in st.session_state:
    st.session_state.continent_chart_type = "📈"

def set_continent_chart(c_type):
    st.session_state.continent_chart_type = c_type

col_empty, col_toggle2 = st.columns([2, 1])
with col_toggle2:
    t1, t2 = st.columns(2)
    with t1:
        st.button("📈", key="btn_cont_line", help="Line Chart", use_container_width=True,
                  type="primary" if st.session_state.continent_chart_type == "📈" else "secondary",
                  on_click=set_continent_chart, args=("📈",))
    with t2:
        st.button("📊", key="btn_cont_bar", help="Bar Chart", use_container_width=True,
                  type="primary" if st.session_state.continent_chart_type == "📊" else "secondary",
                  on_click=set_continent_chart, args=("📊",))

# Continent-level filtering using simple maintanable mapping mapped to the dataset's native continent rows
continent_df = df[
    (df["country"].isin(CONTINENTS)) &
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
]

if not continent_df.empty:
    if st.session_state.continent_chart_type == "📈":
        fig_continent = px.line(
            continent_df,
            x="year",
            y="co2",
            color="country",
            title="Historical CO₂ Emissions by Continent",
            labels={
                "co2": "CO₂ Emissions (million tonnes)",
                "year": "Year",
                "country": "Continent"
            },
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        
        fig_continent.update_layout(
            hovermode="x unified",
            legend_title_text="Continent",
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(size=13)
        )
        st.plotly_chart(fig_continent, use_container_width=True)
    elif st.session_state.continent_chart_type == "📊":
        latest_year = continent_df["year"].max()
        bar_df = continent_df[continent_df["year"] == latest_year]
        fig_continent_bar = px.bar(
            bar_df,
            x="country",
            y="co2",
            color="country",
            title=f"CO₂ Emissions by Continent ({latest_year})",
            labels={
                "co2": "CO₂ Emissions (million tonnes)",
                "country": "Continent"
            },
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_continent_bar.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=50, b=0),
            font=dict(size=13)
        )
        st.plotly_chart(fig_continent_bar, use_container_width=True)
else:
    st.info("Continent data is not available for the selected time range.")

# --- SECTION 3: HIGH POPULATION COUNTRIES COMPARISON ---
st.divider()
st.subheader("High Population Countries Comparison")

if "population_chart_type" not in st.session_state:
    st.session_state.population_chart_type = "📈"

def set_population_chart(c_type):
    st.session_state.population_chart_type = c_type

col_empty, col_toggle3 = st.columns([2, 1])
with col_toggle3:
    t1, t2 = st.columns(2)
    with t1:
        st.button("📈", key="btn_pop_line", help="Line Chart", use_container_width=True,
                  type="primary" if st.session_state.population_chart_type == "📈" else "secondary",
                  on_click=set_population_chart, args=("📈",))
    with t2:
        st.button("📊", key="btn_pop_bar", help="Bar Chart", use_container_width=True,
                  type="primary" if st.session_state.population_chart_type == "📊" else "secondary",
                  on_click=set_population_chart, args=("📊",))

high_pop_countries = ["China", "India", "United States", "Indonesia", "Pakistan"]
high_pop_df = df[
    (df["country"].isin(high_pop_countries)) &
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
]

if not high_pop_df.empty:
    if st.session_state.population_chart_type == "📈":
        fig_co2 = px.line(
            high_pop_df,
            x="year",
            y="co2",
            color="country",
            title="Total CO₂ Emissions",
            labels={"co2": "Total CO₂ Emissions", "year": "Year", "country": "Country"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_co2.update_layout(hovermode="x unified", margin=dict(l=0, r=0, t=50, b=0), font=dict(size=13))
        st.plotly_chart(fig_co2, use_container_width=True)

        fig_per_capita = px.line(
            high_pop_df,
            x="year",
            y="co2_per_capita",
            color="country",
            title="CO₂ Emissions Per Capita",
            labels={"co2_per_capita": "CO₂ Emissions Per Capita", "year": "Year", "country": "Country"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_per_capita.update_layout(hovermode="x unified", margin=dict(l=0, r=0, t=50, b=0), font=dict(size=13))
        st.plotly_chart(fig_per_capita, use_container_width=True)
    elif st.session_state.population_chart_type == "📊":
        latest_year = high_pop_df["year"].max()
        bar_df = high_pop_df[high_pop_df["year"] == latest_year]
        
        fig_co2_bar = px.bar(
            bar_df,
            x="country",
            y="co2",
            color="country",
            title=f"Total CO₂ Emissions ({latest_year})",
            labels={"co2": "Total CO₂ Emissions", "country": "Country"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_co2_bar.update_layout(showlegend=False, margin=dict(l=0, r=0, t=50, b=0), font=dict(size=13))
        st.plotly_chart(fig_co2_bar, use_container_width=True)

        fig_per_capita_bar = px.bar(
            bar_df,
            x="country",
            y="co2_per_capita",
            color="country",
            title=f"CO₂ Emissions Per Capita ({latest_year})",
            labels={"co2_per_capita": "CO₂ Emissions Per Capita", "country": "Country"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_per_capita_bar.update_layout(showlegend=False, margin=dict(l=0, r=0, t=50, b=0), font=dict(size=13))
        st.plotly_chart(fig_per_capita_bar, use_container_width=True)
else:
    st.info("Data not available for High Population Countries in the selected time range.")

# --- SECTION 4: ECONOMIC BLOC COMPARISON ---
st.divider()
st.subheader("BRICS vs OECD vs Scandinavia Emissions Comparison")

if "bloc_chart_type" not in st.session_state:
    st.session_state.bloc_chart_type = "📈"

def set_bloc_chart(c_type):
    st.session_state.bloc_chart_type = c_type

col_empty, col_toggle4 = st.columns([2, 1])
with col_toggle4:
    t1, t2 = st.columns(2)
    with t1:
        st.button("📈", key="btn_bloc_line", help="Line Chart", use_container_width=True,
                  type="primary" if st.session_state.bloc_chart_type == "📈" else "secondary",
                  on_click=set_bloc_chart, args=("📈",))
    with t2:
        st.button("📊", key="btn_bloc_bar", help="Bar Chart", use_container_width=True,
                  type="primary" if st.session_state.bloc_chart_type == "📊" else "secondary",
                  on_click=set_bloc_chart, args=("📊",))

brics = ["Brazil", "Russia", "India", "China", "South Africa"]
oecd = ["United States", "Germany", "France", "United Kingdom", "Japan", "Canada", "Australia", "Italy"]
scandinavia = ["Sweden", "Norway", "Denmark"]

def assign_bloc(country):
    if country in brics:
        return "BRICS"
    elif country in oecd:
        return "OECD"
    elif country in scandinavia:
        return "Scandinavia"
    return None

bloc_df = df.copy()
bloc_df["bloc"] = bloc_df["country"].apply(assign_bloc)
bloc_df = bloc_df[
    (bloc_df["bloc"].notna()) &
    (bloc_df["year"] >= year_range[0]) &
    (bloc_df["year"] <= year_range[1])
]

if not bloc_df.empty:
    if st.session_state.bloc_chart_type == "📈":
        bloc_agg = bloc_df.groupby(["year", "bloc"])["co2"].sum().reset_index()

        fig_bloc = px.line(
            bloc_agg,
            x="year",
            y="co2",
            color="bloc",
            title="Total CO₂ Emissions by Economic Bloc",
            labels={"co2": "Total CO₂", "year": "Year", "bloc": "Bloc"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_bloc.update_layout(hovermode="x unified", margin=dict(l=0, r=0, t=50, b=0), font=dict(size=13))
        st.plotly_chart(fig_bloc, use_container_width=True)
        st.markdown("""
        <div style="border-left: 4px solid #4a7c59; border-radius: 0 6px 6px 0;
        padding: 12px 16px; margin-top: 8px; background: #f0f7f4;">
            <div style="font-size: 11px; font-weight: 600; color: #4a7c59;
            letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 5px;">
            Key Insight</div>
            <p style="font-size: 0.9rem; color: #374151; margin: 0; line-height: 1.6;">
            <strong>BRICS emissions surpassed the OECD subset around 2007</strong>, 
            driven by rapid industrial expansion in China and India. The OECD subset 
            produced <strong>5,215 Mt</strong> in 1960 compared to BRICS at 
            <strong>1,939 Mt</strong> — a structural shift consistent with 
            Global Carbon Budget findings.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.bloc_chart_type == "📊":
        latest_year = bloc_df["year"].max()
        bar_df = bloc_df[bloc_df["year"] == latest_year]
        bloc_bar_agg = bar_df.groupby(["bloc"])["co2"].sum().reset_index()
        
        fig_bloc_bar = px.bar(
            bloc_bar_agg,
            x="bloc",
            y="co2",
            color="bloc",
            title=f"Total CO₂ Emissions by Economic Bloc ({latest_year})",
            labels={"co2": "Total CO₂", "bloc": "Bloc"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_bloc_bar.update_layout(showlegend=False, margin=dict(l=0, r=0, t=50, b=0), font=dict(size=13))
        st.plotly_chart(fig_bloc_bar, use_container_width=True)
else:
    st.info("Data not available for Economic Blocs in the selected time range.")