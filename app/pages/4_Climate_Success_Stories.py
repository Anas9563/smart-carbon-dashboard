import streamlit as st
import pandas as pd
import plotly.express as px
from case_studies.norway import get_case_study as norway_case
from case_studies.germany import get_case_study as germany_case
from case_studies.denmark import get_case_study as denmark_case

st.set_page_config(page_title="Climate Success Stories", layout="wide")

# --- Global Styles ---
st.markdown("""
<style>
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

case_studies = {
    "Norway – Clean Energy Transition": norway_case(),
    "Germany – Energy Transition (Energiewende)": germany_case(),
    "Denmark – Wind Energy Transition": denmark_case()
}

# -----------------------------
# Page Title
# -----------------------------
st.title("Climate Success Stories")

st.markdown(
    '<p class="page-subtitle">Explore real-world country case studies showing how CO₂ emissions can be reduced through policy, energy transition, and long-term planning.</p>',
    unsafe_allow_html=True
)

# -----------------------------
# Case Study Selector
# -----------------------------
if 'selected_case' not in st.session_state:
    st.session_state.selected_case = 'Norway – Clean Energy Transition'

def get_card_html(flag, name, label, value, badge, badge_bg, badge_color, source, is_selected):
    border = "2px solid #7F77DD" if is_selected else "0.5px solid #E0E0E0"
    return f"""
        <div style="background-color: #FFFFFF; border: {border}; border-radius: 12px; padding: 16px; margin-bottom: 8px; font-family: sans-serif; min-height: 220px;">
        <div style="font-size: 22px; margin-bottom: 10px;">{flag}</div>
        <div style="font-size: 14px; font-weight: 500; color: #1a1a1a; margin-bottom: 12px;">{name}</div>
        <div style="font-size: 11px; color: #888888; margin-bottom: 3px;">{label}</div>
        <div style="font-size: 22px; font-weight: 500; color: #1a1a1a; margin-bottom: 10px;">{value}</div>
        <div style="font-size: 11px; font-weight: 500; padding: 3px 10px; border-radius: 99px; display: inline-block; margin-bottom: 10px; background-color: {badge_bg}; color: {badge_color};">{badge}</div>
        <div style="font-size: 11px; color: #888888;">Source: {source}</div>
    </div>
    """

col1, col2, col3 = st.columns(3)

with col1:
    k_norway = 'Norway – Clean Energy Transition'
    st.markdown(get_card_html("🇳🇴", "Norway", "EV share of new car sales (2024)", "88.9%", "Transport focus", "#EEEDFE", "#534AB7", "Norwegian Road Federation (OFV)", st.session_state.selected_case == k_norway), unsafe_allow_html=True)
    if st.button("Explore Norway", key="btn_norway", use_container_width=True):
        st.session_state.selected_case = k_norway

with col2:
    k_germany = 'Germany – Energy Transition (Energiewende)'
    st.markdown(get_card_html("🇩🇪", "Germany", "Emissions reduction since 1990", "-46%", "Energy transition", "#E1F5EE", "#0F6E56", "Umweltbundesamt", st.session_state.selected_case == k_germany), unsafe_allow_html=True)
    if st.button("Explore Germany", key="btn_germany", use_container_width=True):
        st.session_state.selected_case = k_germany

with col3:
    k_denmark = 'Denmark – Wind Energy Transition'
    st.markdown(get_card_html("🇩🇰", "Denmark", "Emissions reduction since 1990", "-51%", "Wind pioneer", "#E6F1FB", "#185FA5", "European Environment Agency", st.session_state.selected_case == k_denmark), unsafe_allow_html=True)
    if st.button("Explore Denmark", key="btn_denmark", use_container_width=True):
        st.session_state.selected_case = k_denmark

st.divider()
# -----------------------------
# DISPLAY SELECTED CASE STUDY
# -----------------------------
data = case_studies[st.session_state.selected_case]

st.header(f" {data['title']}")

if "stats" in data:
    cols = st.columns(3)
    for i, stat in enumerate(data["stats"]):
        with cols[i % 3]:
            st.metric(label=stat["label"], value=stat["value"])
            st.caption(f"Source: {stat['source']}")
    st.divider()

st.markdown("<br>", unsafe_allow_html=True)

# Overview
st.subheader(" Overview")
st.write(data["overview"])
st.divider()

# Strategies
st.subheader(" Key Strategies")
for s in data["strategies"]:
    st.markdown(f"""
    <div style="
        background-color: #F8F7FF;
        border-left: 4px solid #7F77DD;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 14px;
        color: #1a1a1a;
    ">{s}</div>
    """, unsafe_allow_html=True)
st.divider()

# Impact
st.subheader(" Impact on Emissions")
st.write(data["impact"])
st.divider()

# Policy
if "policy" in data:
    st.subheader(" Policy & Governance")
    st.write(data["policy"])
    st.divider()

# Evaluation
if "evaluation" in data:
    st.subheader(" Critical Evaluation")
    st.write(data["evaluation"])
    st.divider()

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------
# CO2 Chart
# -----------------------------
df = pd.read_csv("data/owid-co2-data.csv")
country_data = df[
    (df["country"] == data["country"]) &
    (df["year"] >= 1990)
]

fig = px.line(
    country_data,
    x="year",
    y="co2",
    title=f"{data['country']} CO₂ Emissions (1990–Present)",
    labels={
        "year": "Year",
        "co2": "CO₂ Emissions (million tonnes)"
    },
    template="plotly_white",
    color_discrete_sequence=px.colors.qualitative.Bold
)

fig.update_layout(
    hovermode="x unified",
    margin=dict(l=0, r=0, t=50, b=0),
    font=dict(size=13)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Insight
st.subheader("💡 Key Insight")
st.markdown(f"""
<div style="
    background-color: #EEEDFE;
    border-left: 4px solid #7F77DD;
    border-radius: 0px;
    padding: 14px 18px;
    margin-bottom: 16px;
">
<p style="
    font-size: 11px;
    font-weight: 600;
    color: #534AB7;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
    margin-top: 0px;
">KEY INSIGHT</p>
<p style="
    font-size: 14px;
    color: #3C3489;
    margin: 0px;
">{data["insight"].strip()}</p>
</div>
""", unsafe_allow_html=True)
st.divider()

# Lessons
st.subheader(" Lessons Learned")
lesson_cols = st.columns(2)
for i, l in enumerate(data["lessons"]):
    with lesson_cols[i % 2]:
        st.markdown(f"""
        <div style="
            background-color: #F5F5F5;
            border-radius: 6px;
            padding: 10px 14px;
            margin-bottom: 8px;
            font-size: 14px;
            color: #1a1a1a;
        ">{l}</div>
        """, unsafe_allow_html=True)
st.divider()

st.markdown("<br>", unsafe_allow_html=True)

# Sources
st.markdown("#####  Sources")
for src in data["sources"]:
    st.caption(f"- {src}")
st.divider()
# -----------------------------
# Discussion Section
# -----------------------------
st.divider()
st.header("Discussion")
st.markdown("Share your thoughts on this case study.")

import os
from datetime import datetime
COMMENTS_FILE = "data/comments.csv"

def load_comments():
    if os.path.exists(COMMENTS_FILE):
        try:
            return pd.read_csv(COMMENTS_FILE)
        except:
            return pd.DataFrame(columns=["name", "country", "comment", "timestamp"])
    return pd.DataFrame(columns=["name", "country", "comment", "timestamp"])

def save_comment(name, country, comment):
    df = load_comments()
    new_row = pd.DataFrame([{
        "name": name,
        "country": country,
        "comment": comment,
        "timestamp": datetime.now().strftime("%d %b %Y, %H:%M")
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(COMMENTS_FILE, index=False)

current_country = data["country"]

with st.form("comment_form", clear_on_submit=True):
    col_name, col_country = st.columns(2)
    with col_name:
        user_name = st.text_input("Your name")
    with col_country:
        st.text_input("Case study", value=current_country, disabled=True)
    
    user_comment = st.text_area(
        "Your comment",
        placeholder="What did you find most interesting about this case study?"
    )
    submitted = st.form_submit_button("Post Comment", type="primary")

    if submitted:
        if user_name.strip() and user_comment.strip():
            save_comment(user_name.strip(), current_country, user_comment.strip())
            st.success("Comment posted successfully!")
        else:
            st.warning("Please enter both your name and a comment.")

comments_df = load_comments()

if not comments_df.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Recent Comments")
    for _, row in comments_df.iloc[::-1].iterrows():
        initials = "".join([n[0].upper() for n in str(row["name"]).split()[:2]])
        st.markdown(f"""
        <div style="background: white; border: 0.5px solid #e2e8f0; border-radius: 12px;
        padding: 1rem 1.25rem; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: #f0f7f4;
                display: flex; align-items: center; justify-content: center; font-size: 12px;
                font-weight: 600; color: #4a7c59;">{initials}</div>
                <div>
                    <p style="font-size: 13px; font-weight: 600; color: #1a1a2e; margin: 0;">{row['name']}</p>
                    <p style="font-size: 11px; color: #9ca3af; margin: 0;">{row['country']} · {row['timestamp']}</p>
                </div>
            </div>
            <p style="font-size: 13px; color: #374151; margin: 0; line-height: 1.6;">{row['comment']}</p>
        </div>
        """, unsafe_allow_html=True)