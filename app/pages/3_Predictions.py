import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np
 
st.set_page_config(page_title="CO₂ Emissions Prediction", layout="wide")
 
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
        font-size: 1.2rem;
        font-weight: 700;
        color: #2c3e50;
        padding-bottom: 6px;
        border-bottom: 3px solid #4a7c59;
        margin-bottom: 16px;
        margin-top: 24px;
    }
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 20px 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        border-top: 4px solid #4a7c59;
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #1a1a2e;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #9ca3af;
        margin-top: 4px;
    }
    .kpi-up { color: #dc2626; }
    .kpi-down { color: #16a34a; }
    .model-badge-good {
        background: #f0fdf4;
        border: 1.5px solid #16a34a;
        border-left: 5px solid #16a34a;
        border-radius: 8px;
        padding: 12px 18px;
        color: #15803d;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 16px;
    }
    .model-badge-warn {
        background: #fffbeb;
        border: 1.5px solid #d97706;
        border-left: 5px solid #d97706;
        border-radius: 8px;
        padding: 12px 18px;
        color: #92400e;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 16px;
    }
    .r2-guide {
        background: #f8fafc;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 8px;
        border: 1px solid #e2e8f0;
    }
    .forecast-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 4px;
        font-size: 0.9rem;
        background: white;
        border: 1px solid #f1f5f9;
    }
    .prediction-note {
        background: #f8fafc;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 0.82rem;
        color: #64748b;
        border: 1px solid #e2e8f0;
        margin-top: 8px;
    }
    .sidebar-card {
        background: #f0f7f4;
        border-left: 4px solid #4a7c59;
        border-radius: 6px;
        padding: 12px 14px;
        font-size: 0.82rem;
        color: #374151;
        margin-top: 8px;
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
    df = pd.read_csv("data/cleaned_co2.csv")
    return df
 
df = load_data()

# Keep only real countries (ISO-3 codes)
prediction_df = df[df["iso_code"].notna() & (df["iso_code"].str.len() == 3)].copy()
 
# --- Prediction Function ---
def predict_co2(country, forecast_years=5):

    country_data = prediction_df[prediction_df["country"] == country].copy()
    country_data = country_data[country_data["year"] >= 2000]
    country_data = country_data.dropna(subset=["co2"])
    country_data = country_data[country_data["year"] != 2020]

    if len(country_data) < 10:
        country_data = prediction_df[prediction_df["country"] == country].copy()
        country_data = country_data[country_data["year"] >= 1990]
        country_data = country_data.dropna(subset=["co2"])
        country_data = country_data[country_data["year"] != 2020]

    if len(country_data) < 10:
        return None

    country_data = country_data.sort_values("year").reset_index(drop=True)
    min_year = country_data["year"].min()
    country_data["year_norm"] = country_data["year"] - min_year

    X = country_data[["year_norm"]]
    y = country_data["co2"]

    split_index = int(len(country_data) * 0.8)
    X_train = X.iloc[:split_index]
    y_train = y.iloc[:split_index]
    X_test = X.iloc[split_index:]
    y_test = y.iloc[split_index:]

    # Linear model
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)
    y_test_pred_linear = linear_model.predict(X_test)
    r2_linear = r2_score(y_test, y_test_pred_linear)
    rmse_linear = np.sqrt(mean_squared_error(y_test, y_test_pred_linear))

    # Polynomial optimisation
    best_rmse_poly = float("inf")
    best_degree = None
    best_poly_model = None
    best_poly = None
    best_r2_poly = None
    best_y_pred_poly = None
    degree_results = {}

    for d in [1, 2, 3]:
        poly = PolynomialFeatures(degree=d)
        X_poly = poly.fit_transform(X)
        X_train_poly = X_poly[:split_index]
        X_test_poly = X_poly[split_index:]

        temp_model = LinearRegression()
        temp_model.fit(X_train_poly, y_train)
        temp_pred = temp_model.predict(X_test_poly)
        temp_rmse = np.sqrt(mean_squared_error(y_test, temp_pred))
        temp_r2 = r2_score(y_test, temp_pred)

        label = "Linear" if d == 1 else f"Polynomial (degree {d})"
        degree_results[label] = {"r2": temp_r2, "rmse": temp_rmse}

        if temp_rmse < best_rmse_poly:
            best_rmse_poly = temp_rmse
            best_degree = d
            best_poly_model = temp_model
            best_poly = poly
            best_r2_poly = temp_r2
            best_y_pred_poly = temp_pred

    # Baseline
    last_train_value = y_train.iloc[-1]
    baseline_pred = np.full(len(y_test), last_train_value)
    baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_pred))

    # Future years
    last_year = country_data["year"].max()
    future_years_raw = np.arange(last_year + 1, last_year + forecast_years + 1)
    future_years_norm = future_years_raw - min_year
    future_df_norm = pd.DataFrame({"year_norm": future_years_norm})

    # Future predictions
    future_pred_linear = linear_model.predict(future_df_norm)
    future_poly = best_poly.transform(future_df_norm)
    future_pred_poly = best_poly_model.predict(future_poly)

    # Choose best regression model
    if best_rmse_poly < rmse_linear:
        best_model_name = "Linear" if best_degree == 1 else f"Polynomial (degree {best_degree})"
        best_r2 = best_r2_poly
        best_rmse = best_rmse_poly
        best_test_pred = best_y_pred_poly
        best_future_pred = future_pred_poly
    else:
        best_model_name = "Linear"
        best_r2 = r2_linear
        best_rmse = rmse_linear
        best_test_pred = y_test_pred_linear
        best_future_pred = future_pred_linear

    # Compare best regression model with baseline
    if best_rmse < baseline_rmse:
        final_model_name = best_model_name
        final_r2 = best_r2
        final_rmse = best_rmse
        final_test_pred = best_test_pred
        final_future_pred = best_future_pred
    else:
        final_model_name = "Naive Baseline"
        final_r2 = None
        final_rmse = baseline_rmse
        final_test_pred = baseline_pred
        final_future_pred = np.full(forecast_years, last_train_value)

    # Prevent negative predictions
    final_future_pred = np.maximum(final_future_pred, 0)

    # Reliability classification
    if final_model_name == "Naive Baseline":
        reliability = "Unreliable"
    elif final_r2 is None:
        reliability = "Unreliable"
    elif final_r2 < 0:
        reliability = "Unreliable"
    elif final_r2 < 0.5:
        reliability = "Weak"
    else:
        reliability = "Moderate/Strong"

    return {
        "country_data": country_data,
        "X_test_years": country_data["year"].iloc[split_index:].values,
        "y_test_pred": final_test_pred,
        "baseline_pred": baseline_pred,
        "future_years": future_years_raw,
        "future_pred": final_future_pred,
        "best_model_name": final_model_name,
        "best_degree": best_degree,
        "best_r2": final_r2,
        "best_rmse": final_rmse,
        "baseline_rmse": baseline_rmse,
        "degree_results": degree_results,
        "last_year": last_year,
        "min_year": min_year,
        "reliability": reliability,
    }
 
 
# --- Page Header ---
st.title("CO₂ Emissions Prediction")
st.markdown('<p class="page-subtitle">Forecast short-term CO₂ emissions using an optimised regression model trained on historical data.</p>', unsafe_allow_html=True)
 
# --- Sidebar ---
st.sidebar.header("Prediction Controls")
 
country = st.sidebar.selectbox(
    "Select Country",
    sorted(prediction_df["country"].dropna().unique())
)
 
forecast_years = st.sidebar.slider(
    "Forecast Years",
    min_value=1,
    max_value=10,
    value=5
)
 
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="sidebar-card">
    <strong>About this model</strong><br><br>
    Automatically compares Linear and Polynomial regression models (degrees 1–3), then benchmarks the best regression result against a naive baseline before selecting the final forecast.
    • 2020 excluded — COVID-19 anomaly<br>
    • Years normalised for numerical stability<br>
    • Forecasts are exploratory only
</div>
""", unsafe_allow_html=True)
 
# --- Run Prediction ---
result = predict_co2(country, forecast_years)
 
if result is None:
    st.warning(f"Not enough data available for **{country}** to generate a reliable prediction.")
else:
    country_data = result["country_data"]
    current_value = country_data["co2"].iloc[-1]
    future_value = result["future_pred"][-1]
    change = future_value - current_value
    avg_change = change / forecast_years
 
    # --- Model Badge ---

    if result["best_model_name"] == "Naive Baseline":
        st.markdown(f"""
        <div class="model-badge-warn">
            ⚠️ Model selected: <strong>{result['best_model_name']}</strong> &nbsp;|&nbsp;
            R² = N/A &nbsp;|&nbsp;
            RMSE = {result['best_rmse']:.2f} Mt &nbsp;|&nbsp;
            Baseline used because it outperformed regression models
        </div>
        """, unsafe_allow_html=True)
    elif result["best_r2"] >= 0.5:
        st.markdown(f"""
        <div class="model-badge-good">
            ✅ Model selected: <strong>{result['best_model_name']}</strong> &nbsp;|&nbsp;
            R² = {result['best_r2']:.4f} &nbsp;|&nbsp;
            RMSE = {result['best_rmse']:.2f} Mt &nbsp;|&nbsp;
            Baseline RMSE = {result['baseline_rmse']:.2f} Mt
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="model-badge-warn">
            ⚠️ Model selected: <strong>{result['best_model_name']}</strong> &nbsp;|&nbsp;
            R² = {result['best_r2']:.4f} (low explanatory power) &nbsp;|&nbsp;
            RMSE = {result['best_rmse']:.2f} Mt &nbsp;|&nbsp;
            Treat this forecast with caution
        </div>
        """, unsafe_allow_html=True)
 
    # --- Chart ---
    st.markdown('<div class="section-header">CO₂ Emissions Forecast</div>', unsafe_allow_html=True)
 
    fig = go.Figure()
 
    fig.add_trace(go.Scatter(
        x=country_data["year"],
        y=country_data["co2"],
        mode="lines",
        name="Historical",
        line=dict(color="#4a7c59", width=2.5)
    ))
 
    fig.add_trace(go.Scatter(
        x=result["X_test_years"],
        y=result["y_test_pred"],
        mode="lines",
        name="Test Fit",
        line=dict(color="#f59e0b", dash="dash", width=1.5)
    ))
 
    fig.add_trace(go.Scatter(
        x=result["X_test_years"],
        y=result["baseline_pred"],
        mode="lines",
        name="Naive Baseline",
        line=dict(color="#94a3b8", dash="dot", width=1.5)
    ))
 
    fig.add_trace(go.Scatter(
        x=result["future_years"],
        y=result["future_pred"],
        mode="lines",
        name=f"Forecast ({result['best_model_name']})",
        line=dict(color="#dc2626", dash="dash", width=2.5)
    ))
 
    split_year = result["X_test_years"][0]
    fig.add_vline(
        x=split_year,
        line_dash="dot",
        line_color="#94a3b8",
        annotation_text="Train/Test Split",
        annotation_position="top left",
        annotation_font_color="#64748b"
    )
 
    fig.update_layout(
        title=dict(text=f"CO₂ Emissions Forecast — {country}", font=dict(size=16, color="#1a1a2e")),
        xaxis_title="Year",
        yaxis_title="CO₂ Emissions (million tonnes)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(255,255,255,0.8)", bordercolor="#e2e8f0", borderwidth=1
        ),
        hovermode="x unified",
        height=520,
        plot_bgcolor="#fafafa",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0"),
        yaxis=dict(gridcolor="#f1f5f9", linecolor="#e2e8f0"),
    )
 
    st.plotly_chart(fig, use_container_width=True)
 
    st.markdown("""
    <div class="prediction-note">
        ⚠️ <strong>Prediction Note:</strong> These forecasts are based on historical trend extrapolation only.
        They are exploratory and indicative — not definitive forecasts. Results may not account for future
        policy changes, economic shifts, or external events.
    </div>
    """, unsafe_allow_html=True)
 
    # --- KPI Cards ---
    st.markdown('<div class="section-header">Forecast Summary</div>', unsafe_allow_html=True)
 
    change_class = "kpi-up" if change > 0 else "kpi-down"
    change_arrow = "↑" if change > 0 else "↓"
    avg_class = "kpi-up" if avg_change > 0 else "kpi-down"
 
    col1, col2, col3, col4 = st.columns(4)
 
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Current Emissions</div>
            <div class="kpi-value">{current_value:.1f} Mt</div>
            <div class="kpi-sub">{int(country_data['year'].iloc[-1])}</div>
        </div>
        """, unsafe_allow_html=True)
 
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Predicted ({int(result['last_year'] + forecast_years)})</div>
            <div class="kpi-value">{future_value:.1f} Mt</div>
            <div class="kpi-sub">{forecast_years}-year forecast</div>
        </div>
        """, unsafe_allow_html=True)
 
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Change</div>
            <div class="kpi-value {change_class}">{change_arrow} {abs(change):.1f} Mt</div>
            <div class="kpi-sub">vs current</div>
        </div>
        """, unsafe_allow_html=True)
 
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Avg Yearly Change</div>
            <div class="kpi-value {avg_class}">{avg_change:+.1f} Mt/yr</div>
            <div class="kpi-sub">per year</div>
        </div>
        """, unsafe_allow_html=True)
 
    st.markdown("<br>", unsafe_allow_html=True)
 
    # --- Two column layout ---
    col_left, col_right = st.columns([3, 2])
 
    with col_left:
        st.markdown('<div class="section-header">Model Evaluation (Test Set)</div>', unsafe_allow_html=True)
        st.caption("Regression models are compared using RMSE, then benchmarked against a naive baseline before the final forecast is selected.")
 
        eval_data = []
        for model_name, metrics in result["degree_results"].items():
            is_selected = model_name == result["best_model_name"]
            eval_data.append({
                "Model": model_name,
                "R²": round(metrics["r2"], 4),
                "RMSE (Mt)": round(metrics["rmse"], 2),
                "Selected": "✅" if is_selected else ""
            })

        eval_data.append({
            "Model": "Naive Baseline",
            "R²": "N/A",
            "RMSE (Mt)": round(result["baseline_rmse"], 2),
            "Selected": "✅" if result["best_model_name"] == "Naive Baseline" else ""
        })
 
        eval_df = pd.DataFrame(eval_data)
 
        def style_eval_table(row):
            if row["Selected"] == "✅":
                return ["background-color: #f0fdf4; font-weight: bold"] * len(row)
            elif row["R²"] != "N/A" and row["R²"] < 0:
                return ["background-color: #fff5f5; color: #dc2626"] * len(row)
            return [""] * len(row)
 
        styled_df = eval_df.style.apply(style_eval_table, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
 
        st.markdown(f"""
        <div class="r2-guide">
            📊 <strong>R² Guide:</strong>
            <span style="color:#16a34a">≥ 0.7 Strong</span> &nbsp;|&nbsp;
            <span style="color:#d97706">0.5–0.7 Moderate</span> &nbsp;|&nbsp;
            <span style="color:#dc2626">< 0.5 Weak — treat with caution</span>
            &nbsp;&nbsp; Naive Baseline RMSE: <strong>{result['baseline_rmse']:.2f} Mt</strong>
        </div>
        """, unsafe_allow_html=True)
 
    with col_right:
        st.markdown('<div class="section-header">Year-by-Year Forecast</div>', unsafe_allow_html=True)
 
        prev = current_value
        for yr, val in zip(result["future_years"], result["future_pred"]):
            arrow = "↑" if val > prev else "↓"
            colour = "#dc2626" if val > prev else "#16a34a"
            st.markdown(f"""
            <div class="forecast-row">
                <span style="font-weight:600; color:#374151">{int(yr)}</span>
                <span style="color:{colour}; font-weight:700">{arrow} {val:.2f} Mt</span>
            </div>
            """, unsafe_allow_html=True)
            prev = val
 
    st.markdown("<br>", unsafe_allow_html=True)
 
    # --- Download ---
    st.markdown('<div class="section-header">Download Data</div>', unsafe_allow_html=True)
 
    csv = country_data[["year", "co2"]].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Historical Data (CSV)",
        data=csv,
        file_name=f"{country}_co2_historical.csv",
        mime="text/csv"
    )