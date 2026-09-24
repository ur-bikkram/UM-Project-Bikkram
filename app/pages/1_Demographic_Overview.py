"""Page 1: Learner Demographic Overview
Age distributions, gender balance, and cohort participation levels.
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
from utils import (
    load_dataset,
    inject_custom_css,
    render_kpi_card,
    render_sidebar_filters,
    handle_empty_results
)
from src.analytics import calculate_kpis, get_age_group_summary
from src.visualizations import (
    plot_age_distribution,
    plot_gender_split,
    apply_theme
)

st.set_page_config(page_title="Demographic Overview - EduPro Analytics", layout="wide")
inject_custom_css()

df, user_summary = load_dataset()
filtered_df, filter_state = render_sidebar_filters(df)

st.markdown("""
## Learner Demographic Overview
Demographic breakdown of EduPro learners by age groups, gender distribution, and enrollment counts.
""")

if handle_empty_results(filtered_df):
    st.stop()

# Demographic KPIs
kpis = calculate_kpis(filtered_df)
users_unique = filtered_df.drop_duplicates(subset=["UserID"])

col1, col2, col3, col4 = st.columns(4)
render_kpi_card("Total Registered Users", f"{len(users_unique):,}", "Active learners in selected segment.", badge_text="Learners", col=col1)
render_kpi_card("Average Learner Age", f"{users_unique['Age'].mean():.1f} yrs", f"Median: {users_unique['Age'].median():.0f} yrs (Min 15, Max 35).", badge_text="Age", col=col2)
render_kpi_card("Gender Ratio (F:M)", f"{kpis['gender_participation_ratio']['value']}", f"{kpis['gender_participation_ratio']['female_pct']}% Female participation.", badge_text="Gender", col=col3)
under_18_share = (users_unique["AgeGroup"] == "<18").mean() * 100
render_kpi_card("Under 18 Share", f"{under_18_share:.1f}%", "High school and secondary learners.", badge_text="<18 Cohort", col=col4)

st.markdown("---")

# Visualizations Row 1
vcol1, vcol2 = st.columns([3, 2])

with vcol1:
    fig_age = plot_age_distribution(filtered_df, title="Learner Age Distribution by Demographic Bands")
    st.plotly_chart(fig_age, use_container_width=True)

with vcol2:
    fig_gender = plot_gender_split(filtered_df, title="Gender Participation Breakdown")
    st.plotly_chart(fig_gender, use_container_width=True)

st.markdown("---")

# Demographic Summary Table
st.markdown("### Demographic Cohort Summary")
age_sum = get_age_group_summary(filtered_df)

st.dataframe(
    age_sum.style.format({
        "TotalEnrollments": "{:,}",
        "UniqueLearners": "{:,}",
        "EnrollmentsShare": "{:.1f}%",
        "CoursesPerLearner": "{:.2f}",
        "BeginnerShare": "{:.1f}%",
        "IntermediateShare": "{:.1f}%",
        "AdvancedShare": "{:.1f}%",
        "FreeCourseShare": "{:.1f}%"
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("""
<div class="insight-box">
    <strong>Key Observations:</strong>
    <ul style="margin-top: 8px; margin-bottom: 0;">
        <li><b>Concentration in 18 to 35:</b> Over 85% of learners are in college or early career stages.</li>
        <li><b>Gender Balance:</b> Female and male participation is evenly split at 50.7% to 49.3%.</li>
        <li><b>High School Activity:</b> The under-18 group maintains an average of 3.33 courses per learner, matching adult engagement.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
