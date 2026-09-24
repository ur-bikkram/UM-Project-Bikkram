"""EduPro Learner Demographics & Course Enrollment Behavior Analysis
Main Analytics Dashboard.
"""

import os
import sys

# Ensure app and project root are in sys.path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(APP_DIR)
for p in (APP_DIR, ROOT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import (
    load_dataset,
    inject_custom_css,
    render_kpi_card,
    render_sidebar_filters,
    handle_empty_results
)
from src.analytics import calculate_kpis
from src.visualizations import apply_theme, COLOR_PRIMARY

# 1. Page Configuration
st.set_page_config(
    page_title="EduPro Analytics - Learner Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom Styling
inject_custom_css()

# 3. Load Datasets
df, user_summary = load_dataset()

# 4. Render Sidebar Live Filters
filtered_df, filter_state = render_sidebar_filters(df)

# 5. Executive Header
st.markdown("""
<div style="margin-bottom: 24px;">
    <h1 style="margin-bottom: 6px; color: #F8FAFC; font-size: 2.1rem; font-weight: 700;">
        EduPro Learner Demographics & Enrollment Analytics
    </h1>
    <p style="color: #94A3B8; font-size: 1rem; margin-top: 0;">
        Descriptive analysis of learner age, gender distributions, and course selection behavior.
    </p>
</div>
""", unsafe_allow_html=True)

# 6. Check Empty State
if handle_empty_results(filtered_df):
    st.stop()

# 7. Compute Reactive KPIs
kpis = calculate_kpis(filtered_df)

# 8. Render Top KPI Metric Cards (5 Core Platform Indicators)
st.markdown("### Platform Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

render_kpi_card(
    label="Total Enrollments",
    value=f"{kpis['total_enrollments']['value']:,}",
    definition="Total course enrollments recorded across the platform.",
    badge_text="Volume",
    col=col1
)

render_kpi_card(
    label="Active Learners",
    value=f"{kpis['unique_learners']['value']:,}",
    definition="Unique users with at least one course registration.",
    badge_text="Users",
    col=col2
)

render_kpi_card(
    label="Gender Ratio (F:M)",
    value=f"{kpis['gender_participation_ratio']['value']}",
    definition=f"Female share: {kpis['gender_participation_ratio']['female_pct']}%. Balanced enrollment.",
    badge_text="Equity",
    col=col3
)

top_cat = kpis['top_category']['value']
top_cpi = kpis['top_category']['index']
render_kpi_card(
    label="Top Category",
    value=f"{top_cat}",
    definition=f"CPI: {top_cpi:.1f} vs 100 baseline demand.",
    badge_text="Demand Leader",
    col=col4
)

beg_pct = kpis['level_distribution']['percentages'].get('Beginner', 0)
render_kpi_card(
    label="Beginner Share",
    value=f"{beg_pct:.1f}%",
    definition="Proportion of enrollments in beginner courses.",
    badge_text="Skill Level",
    col=col5
)

st.markdown("---")

# 9. Quick Insights Narrative
with st.expander("Key Findings Summary", expanded=True):
    st.markdown("""
    - **Age Demographics**: 85.3% of learners are between 18 and 35 years old. Younger learners (<18) make up 14.7%.
    - **Gender Balance**: Participation is evenly split at 50.7% female and 49.3% male, with balanced representation across technical subjects.
    - **Category Demand**: Data Science (CPI: 109.9), Machine Learning (CPI: 106.8), and Programming (CPI: 105.1) have the highest enrollments per course.
    - **User Activity**: Top 20% of learners generate 66.5% of total enrollments. 54.3% of users have enrolled in only one course so far.
    """)

# 10. Platform Overview Visualizations
st.markdown("### Enrollment Overview")

vcol1, vcol2 = st.columns([3, 2])

with vcol1:
    monthly_counts = filtered_df.groupby("TransactionMonthName", sort=False).size().reset_index(name="Enrollments")
    fig_month = px.area(
        monthly_counts,
        x="TransactionMonthName",
        y="Enrollments",
        markers=True,
        color_discrete_sequence=[COLOR_PRIMARY],
        labels={"TransactionMonthName": "Month", "Enrollments": "Course Enrollments"}
    )
    fig_month = apply_theme(fig_month, title="Monthly Enrollments (2025)", height=360)
    fig_month.update_traces(fillcolor="rgba(59, 130, 246, 0.15)", line=dict(width=2.5))
    st.plotly_chart(fig_month, use_container_width=True)

with vcol2:
    lvl_counts = filtered_df["CourseLevel"].value_counts().reset_index()
    lvl_counts.columns = ["Level", "Count"]
    fig_lvl = go.Figure(data=[go.Pie(
        labels=lvl_counts["Level"],
        values=lvl_counts["Count"],
        hole=0.55,
        marker=dict(colors=["#10B981", "#0284C7", "#8B5CF6"]),
        textinfo="label+percent",
        textfont=dict(size=12, color="#FFFFFF")
    )])
    fig_lvl = apply_theme(fig_lvl, title="Enrollments by Course Level", height=360)
    st.plotly_chart(fig_lvl, use_container_width=True)

st.markdown("---")

# 11. Multipage Exploration Guide
st.markdown("### Analytical Sections")
st.caption("Use the sidebar on the left to navigate to detailed analyses:")

mcol1, mcol2, mcol3 = st.columns(3)
with mcol1:
    st.markdown("""
    **[1. Demographic Overview](Demographic_Overview)**
    Age distribution, gender split, and cohort metrics.
    """)
    
with mcol2:
    st.markdown("""
    **[2. Age Enrollment Patterns](Age_Enrollment_Patterns)**
    Age group vs category heatmap and learning intensity.
    """)
    
with mcol3:
    st.markdown("""
    **[3. Gender Preferences](Gender_Preferences)**
    Category choices, difficulty levels, and free vs paid courses by gender.
    """)

mcol4, mcol5, _ = st.columns(3)
with mcol4:
    st.markdown("""
    **[4. Category Popularity](Category_Popularity)**
    Category Popularity Index (CPI) and course performance table.
    """)
    
with mcol5:
    st.markdown("""
    **[5. Behavioral Insights](Behavioral_Insights)**
    Pareto 80/20 concentration, learner activity tiers, and retention data.
    """)
