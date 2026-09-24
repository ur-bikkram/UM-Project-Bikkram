"""Page 5: Behavioral Insights & Pareto Analysis
Enrollment concentration, repeat learning habits, and activity tiers.
"""

import os
import sys

# Ensure app and project root are in sys.path
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
from src.analytics import compute_pareto_analysis, calculate_kpis
from src.visualizations import plot_pareto_curve, plot_activity_tiers, apply_theme, COLOR_PRIMARY

st.set_page_config(page_title="Behavioral Insights - EduPro Analytics", layout="wide")
inject_custom_css()

df, user_summary = load_dataset()
filtered_df, filter_state = render_sidebar_filters(df)

st.markdown("""
## Learner Behavioral Insights & Pareto Analysis
Analysis of enrollment concentration, multi-course progression, and user activity tiers.
""")

if handle_empty_results(filtered_df):
    st.stop()

# Behavioral Metrics & Pareto
pareto_data = compute_pareto_analysis(filtered_df)
kpis = calculate_kpis(filtered_df)

col1, col2, col3, col4 = st.columns(4)
render_kpi_card("Top 20% Learner Share", f"{pareto_data['top_20_share']}%", "Share of enrollments from top 20% active learners.", badge_text="Pareto 80/20", col=col1)
render_kpi_card("Top 10% Learner Share", f"{pareto_data['top_10_share']}%", "Share of enrollments from top 10% active learners.", badge_text="Top Decile", col=col2)
render_kpi_card("Gini Coefficient", f"{pareto_data['gini_coefficient']}", "Enrollment dispersion index (0 = equal, 1 = concentrated).", badge_text="Gini", col=col3)
render_kpi_card("Average Courses / User", f"{kpis['avg_courses_per_learner']['value']}", "Mean courses taken per active user.", badge_text="Mean", col=col4)

st.markdown("---")

# Visualizations Row 1: Pareto Curve & Activity Tiers
vcol1, vcol2 = st.columns([3, 2])

with vcol1:
    fig_pareto = plot_pareto_curve(pareto_data, title="Pareto Concentration Curve (Lorenz Curve)")
    st.plotly_chart(fig_pareto, use_container_width=True)

with vcol2:
    fig_tiers = plot_activity_tiers(filtered_df, title="Learner Activity Tiers")
    st.plotly_chart(fig_tiers, use_container_width=True)

st.markdown("---")

# Visualizations Row 2: Courses Per Learner Distribution Histogram
vcol3, vcol4 = st.columns(2)

with vcol3:
    user_counts = filtered_df.groupby("UserID").size().reset_index(name="CoursesEnrolled")
    fig_hist = px.histogram(
        user_counts,
        x="CoursesEnrolled",
        nbins=16,
        color_discrete_sequence=[COLOR_PRIMARY],
        labels={"CoursesEnrolled": "Courses Taken Per Learner", "count": "Learners"}
    )
    fig_hist = apply_theme(fig_hist, title="Distribution of Courses Taken per Learner")
    st.plotly_chart(fig_hist, use_container_width=True)

with vcol4:
    level_counts = filtered_df.groupby(["LearnerActivityTier", "CourseLevel"], observed=False).size().reset_index(name="Enrollments")
    fig_tier_level = px.bar(
        level_counts,
        x="LearnerActivityTier",
        y="Enrollments",
        color="CourseLevel",
        barmode="stack",
        color_discrete_map={"Beginner": "#10B981", "Intermediate": "#0284C7", "Advanced": "#8B5CF6"},
        labels={"LearnerActivityTier": "Activity Tier", "Enrollments": "Total Enrollments"}
    )
    fig_tier_level = apply_theme(fig_tier_level, title="Course Level Preferences by Activity Tier")
    st.plotly_chart(fig_tier_level, use_container_width=True)

st.markdown("""
<div class="insight-box" style="border-left-color: #F59E0B;">
    <strong>Key Observations:</strong>
    <ul style="margin-top: 8px; margin-bottom: 0;">
        <li><b>High Concentration:</b> The top 20% of users account for <b>66.5% of total enrollments</b>, showing that a dedicated core drives most platform activity.</li>
        <li><b>Single-Course Drop-Off:</b> Over half (54.3%) of learners have taken only one course. Encouraging this group to take a second course is the primary growth lever.</li>
        <li><b>Skill Maturation:</b> Repeat learners (4+ courses) take higher proportions of Intermediate and Advanced courses compared to new users.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
