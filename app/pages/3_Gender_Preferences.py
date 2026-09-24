"""Page 3: Gender-Based Course Preference Analysis
Enrollment parity, category choices, and level selections across genders.
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
from src.analytics import calculate_kpis, get_gender_preference_summary
from src.visualizations import (
    plot_gender_category_preference,
    apply_theme,
    COLOR_FEMALE,
    COLOR_MALE
)

st.set_page_config(page_title="Gender Preferences - EduPro Analytics", layout="wide")
inject_custom_css()

df, user_summary = load_dataset()
filtered_df, filter_state = render_sidebar_filters(df)

st.markdown("""
## Gender-Based Course Preferences
Evaluation of enrollment patterns, subject interests, and course level choices by gender.
""")

if handle_empty_results(filtered_df):
    st.stop()

# Gender KPIs
kpis = calculate_kpis(filtered_df)
g_counts = filtered_df["Gender"].value_counts().to_dict()
female_count = g_counts.get("Female", 0)
male_count = g_counts.get("Male", 0)

col1, col2, col3, col4 = st.columns(4)
render_kpi_card("Female Enrollments", f"{female_count:,}", f"Share: {(female_count/max(len(filtered_df),1)*100):.1f}% of total.", badge_text="Female", col=col1)
render_kpi_card("Male Enrollments", f"{male_count:,}", f"Share: {(male_count/max(len(filtered_df),1)*100):.1f}% of total.", badge_text="Male", col=col2)
render_kpi_card("Ratio (F:M)", f"{kpis['gender_participation_ratio']['value']}", "Gender parity indicator (1.0 = equal).", badge_text="Parity", col=col3)
diff_share = abs((female_count - male_count) / max(len(filtered_df), 1) * 100)
render_kpi_card("Difference", f"{diff_share:.1f}%", "Difference between female and male volume.", badge_text="Gap", col=col4)

st.markdown("---")

# Visualizations Row 1: Category preferences
gender_pref = get_gender_preference_summary(filtered_df)

fig_cat_gender = plot_gender_category_preference(
    gender_pref["category_gender"],
    title="Course Category Distribution by Gender (%)"
)
st.plotly_chart(fig_cat_gender, use_container_width=True)

st.markdown("---")

# Visualizations Row 2: Level & Course Type by Gender
vcol1, vcol2 = st.columns(2)

with vcol1:
    lvl_df = gender_pref["level_gender"].reset_index().melt(id_vars="CourseLevel", value_name="Percentage", var_name="Gender")
    fig_lvl = px.bar(
        lvl_df,
        x="CourseLevel",
        y="Percentage",
        color="Gender",
        barmode="group",
        color_discrete_map={"Female": COLOR_FEMALE, "Male": COLOR_MALE},
        labels={"Percentage": "Share within Gender (%)", "CourseLevel": "Level"}
    )
    fig_lvl = apply_theme(fig_lvl, title="Course Level Selection by Gender (%)")
    st.plotly_chart(fig_lvl, use_container_width=True)

with vcol2:
    type_df = gender_pref["type_gender"].reset_index().melt(id_vars="CourseType", value_name="Percentage", var_name="Gender")
    fig_type = px.bar(
        type_df,
        x="CourseType",
        y="Percentage",
        color="Gender",
        barmode="group",
        color_discrete_map={"Female": COLOR_FEMALE, "Male": COLOR_MALE},
        labels={"Percentage": "Share within Gender (%)", "CourseType": "Course Type"}
    )
    fig_type = apply_theme(fig_type, title="Course Type Selection (Free vs Paid) by Gender (%)")
    st.plotly_chart(fig_type, use_container_width=True)

st.markdown("---")

# Comparative Table: Relative Index of Gender Over-Representation
st.markdown("### Category Breakdown by Gender")
st.caption("Enrollment counts and female-to-male ratio by category.")

cat_crosstab = pd.crosstab(filtered_df["CourseCategory"], filtered_df["Gender"])
cat_crosstab["Total"] = cat_crosstab.sum(axis=1)
cat_crosstab["FemaleShare"] = (cat_crosstab["Female"] / cat_crosstab["Total"] * 100).round(1)
cat_crosstab["MaleShare"] = (cat_crosstab["Male"] / cat_crosstab["Total"] * 100).round(1)
cat_crosstab["Ratio (F:M)"] = (cat_crosstab["Female"] / cat_crosstab["Male"].clip(lower=1)).round(2)

st.dataframe(
    cat_crosstab[["Total", "Female", "Male", "FemaleShare", "MaleShare", "Ratio (F:M)"]].sort_values(by="FemaleShare", ascending=False),
    use_container_width=True
)

st.markdown("""
<div class="insight-box" style="border-left-color: #E11D48;">
    <strong>Key Observations:</strong>
    <ul style="margin-top: 8px; margin-bottom: 0;">
        <li><b>STEM Parity:</b> Technical tracks like <i>Data Science</i> and <i>Artificial Intelligence</i> have roughly 50% female participation.</li>
        <li><b>Small Category Differences:</b> Female enrollments are slightly higher in <i>Design</i> and <i>Marketing</i>, while male enrollments are slightly higher in <i>Programming</i> and <i>Cybersecurity</i>.</li>
        <li><b>Course Type Choices:</b> Both male and female learners choose free and paid courses at nearly the same rate (~63% free, ~37% paid).</li>
    </ul>
</div>
""", unsafe_allow_html=True)
