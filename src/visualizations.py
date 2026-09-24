"""Standardized Plotly visualization module for EduPro.
Employs a cohesive, professional palette with responsive layouts and rich tooltips.
"""

import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Design System Color Tokens
COLOR_PRIMARY = "#3B82F6"       # Vivid Blue
COLOR_SECONDARY = "#0D9488"     # Teal
COLOR_ACCENT = "#F59E0B"        # Amber
COLOR_HIGHLIGHT = "#EC4899"     # Pink / Magenta
COLOR_DARK = "#0F172A"          # Slate 900
COLOR_LIGHT = "#F8FAFC"         # Slate 50
COLOR_TEXT_MAIN = "#F8FAFC"     # Bright text
COLOR_TEXT_MUTED = "#94A3B8"    # Muted slate text
COLOR_MUTED = "#64748B"         # Slate 500 for neutral bars
COLOR_GRID = "rgba(255, 255, 255, 0.08)" # Faint translucent grid
COLOR_LINE = "rgba(255, 255, 255, 0.18)" # Subtle axis lines
COLOR_SUCCESS = "#10B981"       # Emerald
COLOR_FEMALE = "#E11D48"        # Rose / Crimson
COLOR_MALE = "#3B82F6"          # Vivid Blue

PALETTE_CATEGORICAL = [
    "#3B82F6", "#0D9488", "#F59E0B", "#8B5CF6", "#EC4899",
    "#06B6D4", "#10B981", "#6366F1", "#F97316", "#14B8A6",
    "#60A5FA", "#84CC16"
]

LEVEL_COLORS = {
    "Beginner": "#10B981",       # Green
    "Intermediate": "#0284C7",   # Sky Blue
    "Advanced": "#8B5CF6"        # Purple
}


def apply_theme(fig, title=None, height=450):
    """Apply consistent styling, typography, and clean axes to a Plotly figure."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=16, family="Plus Jakarta Sans, Inter, sans-serif", color=COLOR_TEXT_MAIN),
            x=0.01,
            y=0.96
        ),
        font=dict(family="Inter, system-ui, sans-serif", color=COLOR_TEXT_MAIN),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=60, b=40),
        height=height,
        hoverlabel=dict(
            bgcolor="#0F172A",
            bordercolor="#3B82F6",
            font_size=13,
            font_family="Inter, sans-serif",
            font_color="#FFFFFF"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color=COLOR_TEXT_MAIN)
        )
    )
    fig.update_xaxes(
        gridcolor=COLOR_GRID,
        showline=True,
        linecolor=COLOR_LINE,
        tickfont=dict(color=COLOR_TEXT_MUTED, size=11),
        title_font=dict(color=COLOR_TEXT_MUTED, size=12)
    )
    fig.update_yaxes(
        gridcolor=COLOR_GRID,
        showline=True,
        linecolor=COLOR_LINE,
        tickfont=dict(color=COLOR_TEXT_MUTED, size=11),
        title_font=dict(color=COLOR_TEXT_MUTED, size=12)
    )
    return fig


def plot_age_distribution(df, title="Learner Age Distribution & Demographic Bands"):
    """Histogram with demographic age band color coding."""
    age_counts = df.groupby(["Age", "AgeGroup"], observed=False).size().reset_index(name="Enrollments")
    
    fig = px.bar(
        age_counts,
        x="Age",
        y="Enrollments",
        color="AgeGroup",
        color_discrete_sequence=["#F59E0B", "#2563EB", "#0D9488", "#8B5CF6", "#EC4899"],
        labels={"Enrollments": "Total Enrollments", "Age": "Age (Years)", "AgeGroup": "Age Band"}
    )
    fig.update_traces(marker_line_width=0.5, marker_line_color="#FFFFFF")
    return apply_theme(fig, title=title)


def plot_gender_split(df, title="Gender Participation Ratio"):
    """Donut chart showing Male vs. Female enrollment share."""
    counts = df["Gender"].value_counts().reset_index()
    counts.columns = ["Gender", "Count"]
    
    fig = go.Figure(data=[go.Pie(
        labels=counts["Gender"],
        values=counts["Count"],
        hole=0.55,
        marker=dict(colors=[COLOR_FEMALE if g == "Female" else COLOR_MALE for g in counts["Gender"]]),
        textinfo="label+percent",
        textfont=dict(size=13),
        hovertemplate="<b>%{label}</b><br>Enrollments: %{value:,}<br>Share: %{percent}<extra></extra>"
    )])
    
    fig.add_annotation(
        text=f"<b>{len(df):,}</b><br><span style='font-size:11px;color:#94A3B8'>Enrollments</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(size=14, color="#FFFFFF")
    )
    return apply_theme(fig, title=title, height=380)


def plot_age_category_heatmap(ct_matrix, title="Age Group vs. Course Category Preference Heatmap"):
    """Heatmap showing enrollment volume or percentage across age bands and categories."""
    fig = go.Figure(data=go.Heatmap(
        z=ct_matrix.values,
        x=ct_matrix.columns.tolist(),
        y=ct_matrix.index.tolist(),
        colorscale="Blues",
        text=ct_matrix.values,
        texttemplate="%{text}",
        textfont={"size": 11},
        hoverongaps=False,
        hovertemplate="<b>Age: %{y}</b><br>Category: %{x}<br>Value: %{z}<extra></extra>"
    ))
    fig.update_xaxes(tickangle=-35)
    return apply_theme(fig, title=title, height=480)


def plot_category_popularity(metrics_df, title="Category Popularity Index (CPI) Benchmark"):
    """Horizontal bar chart showing Category Popularity Index relative to platform baseline (100)."""
    sorted_df = metrics_df.sort_values(by="CategoryPopularityIndex", ascending=True)
    muted_color = globals().get("COLOR_MUTED", "#64748B")
    colors = [COLOR_PRIMARY if cpi >= 100 else muted_color for cpi in sorted_df["CategoryPopularityIndex"]]
    
    fig = go.Figure(go.Bar(
        x=sorted_df["CategoryPopularityIndex"],
        y=sorted_df["CourseCategory"],
        orientation="h",
        marker=dict(color=colors),
        text=sorted_df["CategoryPopularityIndex"].apply(lambda v: f"{v:.1f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>CPI: %{x:.1f}<br>Total Enrollments: %{customdata[0]:,}<br>Courses: %{customdata[1]}<extra></extra>",
        customdata=sorted_df[["TotalEnrollments", "UniqueCourses"]].values
    ))
    
    fig.add_vline(
        x=100,
        line_dash="dash",
        line_color="#EF4444",
        annotation_text="Baseline (100)",
        annotation_position="top right",
        annotation_font=dict(color="#EF4444", size=11)
    )
    
    fig.update_xaxes(title="Category Popularity Index (CPI)")
    fig.update_yaxes(title="")
    return apply_theme(fig, title=title, height=500)


def plot_level_distribution(df, group_col="CourseCategory", title="Course Level Distribution by Category"):
    """Grouped stacked bar chart showing Beginner, Intermediate, and Advanced distribution."""
    ct = pd.crosstab(df[group_col], df["CourseLevel"], normalize="index") * 100
    ct = ct.round(1).reset_index()
    
    fig = go.Figure()
    for level in ["Beginner", "Intermediate", "Advanced"]:
        if level in ct.columns:
            fig.add_trace(go.Bar(
                x=ct[group_col],
                y=ct[level],
                name=level,
                marker_color=LEVEL_COLORS.get(level, COLOR_PRIMARY),
                text=ct[level].apply(lambda v: f"{v:.0f}%" if v > 5 else ""),
                textposition="inside",
                hovertemplate=f"<b>%{{x}}</b><br>{level}: %{{y:.1f}}%<extra></extra>"
            ))
            
    fig.update_layout(barmode="stack", yaxis=dict(title="Share of Enrollments (%)", range=[0, 105]))
    fig.update_xaxes(tickangle=-35)
    return apply_theme(fig, title=title, height=480)


def plot_gender_category_preference(cat_gender_df, title="Gender Distribution Across Course Categories"):
    """Grouped comparative bar chart for Female vs Male enrollments across categories."""
    df_melt = cat_gender_df.reset_index().melt(
        id_vars="CourseCategory",
        value_vars=["Female", "Male"],
        var_name="Gender",
        value_name="Percentage"
    )
    
    fig = px.bar(
        df_melt,
        x="CourseCategory",
        y="Percentage",
        color="Gender",
        barmode="group",
        color_discrete_map={"Female": COLOR_FEMALE, "Male": COLOR_MALE},
        labels={"Percentage": "Share within Gender (%)", "CourseCategory": "Category"}
    )
    fig.update_xaxes(tickangle=-35)
    fig.update_layout(yaxis=dict(title="Share within Gender (%)"))
    return apply_theme(fig, title=title, height=460)


def plot_pareto_curve(pareto_data, title="Enrollment Concentration (Lorenz Curve / Pareto 80-20)"):
    """Lorenz curve showing cumulative learner share vs cumulative enrollment share."""
    user_pct = pareto_data["lorenz_user_pct"]
    enroll_pct = pareto_data["lorenz_enroll_pct"]
    
    fig = go.Figure()
    
    # Equality Line
    fig.add_trace(go.Scatter(
        x=[0, 100], y=[0, 100],
        mode="lines",
        line=dict(dash="dash", color="#94A3B8", width=1.5),
        name="Perfect Equality"
    ))
    
    # Lorenz Curve
    fig.add_trace(go.Scatter(
        x=user_pct, y=enroll_pct,
        mode="lines",
        line=dict(color=COLOR_PRIMARY, width=3),
        name="Actual Concentration",
        hovertemplate="Top %{x:.1f}% Learners<br>Account for %{y:.1f}% Enrollments<extra></extra>"
    ))
    
    # Highlight 20% point
    top_20 = pareto_data["top_20_share"]
    fig.add_trace(go.Scatter(
        x=[20], y=[top_20],
        mode="markers+text",
        marker=dict(color="#EF4444", size=10),
        text=[f"Top 20% = {top_20}%"],
        textposition="top left",
        name="Pareto 20% Marker"
    ))
    
    fig.add_annotation(
        text=f"<b>Gini Coefficient: {pareto_data['gini_coefficient']}</b>",
        x=70, y=20,
        showarrow=False,
        font=dict(size=13, color="#FFFFFF"),
        bgcolor="#1E293B",
        bordercolor="rgba(255, 255, 255, 0.15)",
        borderwidth=1,
        borderpad=6
    )
    
    fig.update_xaxes(title="Cumulative Share of Learners (%)", range=[0, 102])
    fig.update_yaxes(title="Cumulative Share of Enrollments (%)", range=[0, 102])
    return apply_theme(fig, title=title, height=450)


def plot_activity_tiers(df, title="Learner Activity Tiers"):
    """Donut chart showing breakdown of Single-Course vs Power Learners."""
    user_tiers = df.drop_duplicates(subset=["UserID"])["LearnerActivityTier"].value_counts(sort=False).reset_index()
    user_tiers.columns = ["Tier", "Learners"]
    
    fig = go.Figure(data=[go.Pie(
        labels=user_tiers["Tier"],
        values=user_tiers["Learners"],
        hole=0.5,
        marker=dict(colors=["#94A3B8", "#0284C7", "#2563EB", "#7C3AED"]),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Users: %{value:,}<br>Share: %{percent}<extra></extra>"
    )])
    return apply_theme(fig, title=title, height=380)
