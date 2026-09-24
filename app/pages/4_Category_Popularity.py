"""Page 4: Course Category Popularity Visuals
Performance analysis of course domains using the Category Popularity Index (CPI).
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
from src.analytics import get_category_metrics
from src.visualizations import plot_category_popularity, apply_theme, COLOR_PRIMARY, COLOR_SECONDARY

st.set_page_config(page_title="Category Popularity - EduPro Analytics", layout="wide")
inject_custom_css()

df, user_summary = load_dataset()
filtered_df, filter_state = render_sidebar_filters(df)

st.markdown("""
## Course Category Popularity & Demand Analysis
Evaluation of course catalog demand, category popularity benchmarks, and enrollment volume across subject areas.
""")

if handle_empty_results(filtered_df):
    st.stop()

# Category Metrics
cat_metrics = get_category_metrics(filtered_df)

top_cat = cat_metrics.iloc[0]
least_cat = cat_metrics.iloc[-1]

col1, col2, col3, col4 = st.columns(4)
render_kpi_card("Most Popular Category", f"{top_cat['CourseCategory']}", f"{top_cat['TotalEnrollments']:,} enrollments (CPI: {top_cat['CategoryPopularityIndex']:.1f}).", badge_text="Leader", col=col1)
render_kpi_card("Active Categories", f"{len(cat_metrics)}", "Course categories offered.", badge_text="Catalog", col=col2)
avg_enroll = cat_metrics["TotalEnrollments"].mean()
render_kpi_card("Average per Category", f"{avg_enroll:.0f}", "Mean enrollments per category.", badge_text="Mean", col=col3)
render_kpi_card("Lowest Category", f"{least_cat['CourseCategory']}", f"{least_cat['TotalEnrollments']:,} enrollments (CPI: {least_cat['CategoryPopularityIndex']:.1f}).", badge_text="Lowest", col=col4)

st.markdown("---")

# Visualizations Row 1: CPI Benchmark Chart
st.plotly_chart(
    plot_category_popularity(cat_metrics, title="Category Popularity Index (CPI) vs. Platform Baseline (100)"),
    use_container_width=True
)

st.markdown("---")

# Visualizations Row 2: Ratings vs Enrollments
vcol1, vcol2 = st.columns([3, 2])

with vcol1:
    fig_scatter = px.scatter(
        cat_metrics,
        x="AvgRating",
        y="TotalEnrollments",
        size="UniqueCourses",
        color="CategoryPopularityIndex",
        color_continuous_scale="Blues",
        text="CourseCategory",
        labels={"AvgRating": "Average Course Rating", "TotalEnrollments": "Total Enrollments", "CategoryPopularityIndex": "CPI"},
        hover_data=["UniqueCourses", "EnrollmentPerCourse"]
    )
    fig_scatter.update_traces(textposition="top center", marker=dict(line=dict(width=1, color="#1E293B")))
    fig_scatter = apply_theme(fig_scatter, title="Course Rating vs. Total Enrollments", height=420)
    st.plotly_chart(fig_scatter, use_container_width=True)

with vcol2:
    fig_free_paid = px.bar(
        cat_metrics,
        x=["FreeEnrollments", "PaidEnrollments"],
        y="CourseCategory",
        orientation="h",
        barmode="stack",
        color_discrete_map={"FreeEnrollments": "#10B981", "PaidEnrollments": "#F59E0B"},
        labels={"value": "Enrollments", "variable": "Enrollment Type", "CourseCategory": "Category"}
    )
    fig_free_paid = apply_theme(fig_free_paid, title="Free vs. Paid Enrollments by Category", height=420)
    st.plotly_chart(fig_free_paid, use_container_width=True)

st.markdown("---")

# Category Scorecard Table
st.markdown("### Category Performance Table")
st.dataframe(
    cat_metrics.style.format({
        "TotalEnrollments": "{:,}",
        "UniqueCourses": "{:,}",
        "UniqueLearners": "{:,}",
        "AvgRating": "{:.2f} / 5.0",
        "EnrollmentShare": "{:.2f}%",
        "EnrollmentPerCourse": "{:.1f}",
        "CategoryPopularityIndex": "{:.1f}",
        "TotalRevenue": "${:,.2f}"
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("""
<div class="insight-box">
    <strong>Key Observations:</strong>
    <ul style="margin-top: 8px; margin-bottom: 0;">
        <li><b>Highest Demand:</b> <i>Data Science</i>, <i>Machine Learning</i>, and <i>Programming</i> lead in enrollment density per course.</li>
        <li><b>Course Breadth:</b> All 12 categories maintain steady baseline enrollments (above 750 enrollments each).</li>
        <li><b>Course Satisfaction:</b> Ratings across categories are consistent between 4.3 and 4.6 out of 5.0.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
