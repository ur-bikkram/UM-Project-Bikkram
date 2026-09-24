"""Page 2: Age-Wise Enrollment Patterns
Course preferences across age bands, including the Age vs. Category Heatmap.
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
from src.analytics import get_age_category_heatmap_matrix, get_age_group_summary
from src.visualizations import plot_age_category_heatmap, plot_level_distribution, apply_theme, COLOR_PRIMARY

st.set_page_config(page_title="Age Enrollment Patterns - EduPro Analytics", layout="wide")
inject_custom_css()

df, user_summary = load_dataset()
filtered_df, filter_state = render_sidebar_filters(df)

st.markdown("""
## Age-Wise Enrollment Patterns & Preferences
How course selections, category choices, and difficulty levels differ across age groups.
""")

if handle_empty_results(filtered_df):
    st.stop()

# Interactive Heatmap Section
st.markdown("### Age Group vs. Course Category Heatmap")
st.caption("Subject choices across demographic age bands.")

hcol1, hcol2 = st.columns([1, 3])
with hcol1:
    norm_option = st.radio(
        "Display Mode:",
        options=["Raw Enrollment Counts", "Row Percentage (% of Age Group)", "Column Percentage (% of Category)"],
        index=0,
        help="Switch between raw counts and percentage distributions."
    )
    
norm_param = False
if norm_option == "Row Percentage (% of Age Group)":
    norm_param = "index"
elif norm_option == "Column Percentage (% of Category)":
    norm_param = "columns"

heatmap_matrix = get_age_category_heatmap_matrix(filtered_df, normalize=norm_param)

with hcol2:
    fig_heatmap = plot_age_category_heatmap(
        heatmap_matrix,
        title=f"Age Group vs. Course Category ({norm_option})"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# Visualizations Row 2: Skill Level and Per-Capita Intensity by Age
vcol1, vcol2 = st.columns(2)

with vcol1:
    fig_lvl_age = plot_level_distribution(
        filtered_df,
        group_col="AgeGroup",
        title="Course Difficulty Level by Age Group (%)"
    )
    st.plotly_chart(fig_lvl_age, use_container_width=True)

with vcol2:
    age_sum = get_age_group_summary(filtered_df)
    fig_intensity = go.Figure()
    fig_intensity.add_trace(go.Bar(
        x=age_sum["AgeGroup"].astype(str),
        y=age_sum["TotalEnrollments"],
        name="Total Enrollments",
        marker_color=COLOR_PRIMARY,
        yaxis="y"
    ))
    fig_intensity.add_trace(go.Scatter(
        x=age_sum["AgeGroup"].astype(str),
        y=age_sum["CoursesPerLearner"],
        name="Courses / Learner",
        mode="lines+markers",
        line=dict(color="#EF4444", width=3),
        marker=dict(size=8),
        yaxis="y2"
    ))
    fig_intensity.update_layout(
        yaxis=dict(title="Total Enrollments"),
        yaxis2=dict(title="Courses Per Learner", overlaying="y", side="right", range=[2.0, 4.5])
    )
    fig_intensity = apply_theme(fig_intensity, title="Enrollment Volume and Intensity by Age Band")
    st.plotly_chart(fig_intensity, use_container_width=True)

st.markdown("""
<div class="insight-box">
    <strong>Key Observations:</strong>
    <ul style="margin-top: 8px; margin-bottom: 0;">
        <li><b>Under 18 Cohort:</b> Shows higher relative interest in <i>Web Development</i>, <i>Design</i>, and <i>Programming</i>.</li>
        <li><b>18 to 25 Cohort:</b> Highest enrollment volume overall, leading in <i>Data Science</i>, <i>Machine Learning</i>, and <i>AI</i>.</li>
        <li><b>26 to 35 Cohort:</b> Higher engagement with career management subjects including <i>Project Management</i>, <i>Finance</i>, and <i>Business</i>.</li>
        <li><b>Course Levels:</b> Each age band enrolls in roughly 35% Beginner, 30% Intermediate, and 35% Advanced courses.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
