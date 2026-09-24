"""Shared utilities, caching, and custom components for EduPro Streamlit app.
"""

import os
import sys
import streamlit as st
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.data_pipeline import run_pipeline


@st.cache_data(show_spinner="Loading EduPro datasets...")
def load_dataset():
    """Load or build the processed merged enrollment and user summary datasets."""
    data_path = os.path.join(BASE_DIR, "data", "processed", "merged_enrollments.csv")
    user_path = os.path.join(BASE_DIR, "data", "processed", "user_summary.csv")
    
    if not os.path.exists(data_path) or not os.path.exists(user_path):
        merged, user_summary, _ = run_pipeline()
        return merged, user_summary
        
    merged = pd.read_csv(data_path)
    user_summary = pd.read_csv(user_path)
    
    # Ensure proper datetime parsing
    merged["TransactionDate"] = pd.to_datetime(merged["TransactionDate"])
    
    # Ensure proper categorical ordering
    level_order = ["Beginner", "Intermediate", "Advanced"]
    merged["CourseLevel"] = pd.Categorical(merged["CourseLevel"], categories=level_order, ordered=True)
    
    tier_order = ["Single-Course (1)", "Moderate (2-3)", "Active (4-7)", "Power Learner (8+)"]
    merged["LearnerActivityTier"] = pd.Categorical(merged["LearnerActivityTier"], categories=tier_order, ordered=True)
    
    age_order = ["<18", "18–25", "26–35", "36–45", "45+"]
    merged["AgeGroup"] = pd.Categorical(merged["AgeGroup"], categories=age_order, ordered=True)
    
    return merged, user_summary


def inject_custom_css():
    """Inject modern, sleek typography and CSS styling tokens."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, sans-serif;
    }
    
    h1, h2, h3, .metric-title {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Modern Dark Theme Metric Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        margin-bottom: 12px;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px -4px rgba(59, 130, 246, 0.25);
        border-color: #3B82F6;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #FFFFFF !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
        line-height: 1.2;
        margin-top: 4px;
    }
    .kpi-label {
        font-size: 0.80rem;
        font-weight: 600;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-subtext {
        font-size: 0.78rem;
        color: #CBD5E1 !important;
        margin-top: 6px;
        line-height: 1.35;
    }
    .badge {
        display: inline-block;
        padding: 2px 8px;
        font-size: 0.72rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: rgba(59, 130, 246, 0.18);
        color: #60A5FA !important;
        border: 1px solid rgba(59, 130, 246, 0.35);
        margin-top: 4px;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Alert / Empty State */
    .empty-state-box {
        background-color: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        color: #FBBF24;
        margin: 20px 0;
    }

    /* Insight Box */
    .insight-box {
        background-color: #1E293B;
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 16px 20px;
        margin-top: 16px;
        color: #E2E8F0;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .insight-box strong {
        color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)


def render_kpi_card(label, value, definition, badge_text=None, col=None):
    """Render a styled KPI card with definitions and optional badge."""
    badge_html = f"<div class='badge'>{badge_text}</div>" if badge_text else ""
    html = f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {badge_html}
        <div class="kpi-subtext">{definition}</div>
    </div>
    """
    if col:
        col.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


def render_sidebar_filters(df):
    """Render comprehensive live filters in the sidebar and return filtered DataFrame.
    
    Returns:
        tuple: (filtered_df, filter_dict)
    """
    st.sidebar.markdown("### Filters")
    st.sidebar.caption("Filter data across all dashboard views.")
    
    # 1. Age Group Filter
    available_age_groups = [ag for ag in ["<18", "18–25", "26–35", "36–45", "45+"] if ag in df["AgeGroup"].values]
    selected_age_groups = st.sidebar.multiselect(
        "Age Band:",
        options=available_age_groups,
        default=available_age_groups,
        help="Filter by age group."
    )
    
    # 2. Gender Filter
    gender_options = ["All"] + sorted(list(df["Gender"].dropna().unique()))
    selected_gender = st.sidebar.selectbox(
        "Gender:",
        options=gender_options,
        index=0,
        help="Filter by gender."
    )
    
    # 3. Course Category Filter
    all_categories = sorted(list(df["CourseCategory"].dropna().unique()))
    selected_categories = st.sidebar.multiselect(
        "Course Category:",
        options=all_categories,
        default=all_categories,
        help="Filter by course category."
    )
    
    # 4. Course Level Filter
    available_levels = [lvl for lvl in ["Beginner", "Intermediate", "Advanced"] if lvl in df["CourseLevel"].values]
    selected_levels = st.sidebar.multiselect(
        "Course Level:",
        options=available_levels,
        default=available_levels,
        help="Filter by difficulty level."
    )
    
    # 5. Course Type Filter (Free vs Paid)
    available_types = sorted(list(df["CourseType"].dropna().unique()))
    selected_types = st.sidebar.multiselect(
        "Course Type:",
        options=available_types,
        default=available_types,
        help="Filter by Free vs Paid."
    )
    
    # Apply filtering
    filtered = df.copy()
    
    if selected_age_groups:
        filtered = filtered[filtered["AgeGroup"].isin(selected_age_groups)]
    else:
        filtered = filtered.iloc[0:0]
        
    if selected_gender != "All":
        filtered = filtered[filtered["Gender"] == selected_gender]
        
    if selected_categories:
        filtered = filtered[filtered["CourseCategory"].isin(selected_categories)]
    else:
        filtered = filtered.iloc[0:0]
        
    if selected_levels:
        filtered = filtered[filtered["CourseLevel"].isin(selected_levels)]
    else:
        filtered = filtered.iloc[0:0]
        
    if selected_types:
        filtered = filtered[filtered["CourseType"].isin(selected_types)]
    else:
        filtered = filtered.iloc[0:0]
        
    # Filter stats in sidebar
    total_recs = len(df)
    filtered_recs = len(filtered)
    pct = (filtered_recs / total_recs) * 100 if total_recs > 0 else 0
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Showing Records:** `{filtered_recs:,}` / `{total_recs:,}` ({pct:.1f}%)")
    
    if st.sidebar.button("Reset Filters", use_container_width=True):
        st.session_state.clear()
        st.rerun()
        
    filter_state = {
        "age_groups": selected_age_groups,
        "gender": selected_gender,
        "categories": selected_categories,
        "levels": selected_levels,
        "types": selected_types,
        "records_count": filtered_recs
    }
    
    return filtered, filter_state


def handle_empty_results(df):
    """Render a friendly warning message if filtered DataFrame has 0 rows."""
    if len(df) == 0:
        st.markdown("""
        <div class="empty-state-box">
            <h3>No Matching Records Found</h3>
            <p>Your current filter selection resulted in 0 enrollments.<br>
            Please expand your filter selections in the sidebar.</p>
        </div>
        """, unsafe_allow_html=True)
        return True
    return False
