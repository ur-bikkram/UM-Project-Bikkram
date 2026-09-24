"""Analytical metrics, KPI calculations, cross-tabulations, and Pareto analysis for EduPro.
"""

import os
import sys
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def calculate_kpis(df):
    """Compute headline Key Performance Indicators (KPIs) with definitions.
    
    Args:
        df (pd.DataFrame): Merged enrollments DataFrame.
        
    Returns:
        dict: KPI values and explanations.
    """
    total_enrollments = len(df)
    unique_learners = df["UserID"].nunique()
    unique_courses = df["CourseID"].nunique()
    
    # Enrollments by Age Group
    age_dist = df["AgeGroup"].value_counts(sort=False).to_dict()
    age_pct = (df["AgeGroup"].value_counts(normalize=True, sort=False) * 100).round(1).to_dict()
    
    # Gender Participation Ratio (GPR)
    gender_counts = df["Gender"].value_counts().to_dict()
    females = gender_counts.get("Female", 0)
    males = gender_counts.get("Male", 0)
    gpr = round(females / max(males, 1), 2)
    female_pct = round((females / max(total_enrollments, 1)) * 100, 1)
    
    # Level Preference Distribution
    level_counts = df["CourseLevel"].value_counts(sort=False).to_dict()
    level_pct = (df["CourseLevel"].value_counts(normalize=True, sort=False) * 100).round(1).to_dict()
    
    # Category Popularity Index (CPI)
    # CPI = (Category Enrollments / Category Course Count) / (Total Enrollments / Total Courses) * 100
    cat_enroll = df.groupby("CourseCategory").size()
    cat_course_count = df.groupby("CourseCategory")["CourseID"].nunique()
    total_avg_enroll_per_course = total_enrollments / max(unique_courses, 1)
    
    cpi = ((cat_enroll / cat_course_count.clip(lower=1)) / total_avg_enroll_per_course * 100).round(1).to_dict()
    top_category = max(cpi, key=cpi.get) if cpi else "N/A"
    
    # Courses per learner
    avg_courses_per_learner = round(total_enrollments / max(unique_learners, 1), 2)
    
    return {
        "total_enrollments": {
            "value": total_enrollments,
            "label": "Total Enrollments",
            "definition": "Overall platform engagement indicator measuring aggregate course registrations."
        },
        "unique_learners": {
            "value": unique_learners,
            "label": "Total Active Learners",
            "definition": "Distinct registered users with at least one course enrollment."
        },
        "gender_participation_ratio": {
            "value": gpr,
            "female_pct": female_pct,
            "label": "Gender Participation Ratio",
            "definition": "Inclusivity metric representing female-to-male enrollment proportion (F:M)."
        },
        "avg_courses_per_learner": {
            "value": avg_courses_per_learner,
            "label": "Average Courses / Learner",
            "definition": "Mean number of enrollments completed per registered user."
        },
        "top_category": {
            "value": top_category,
            "index": cpi.get(top_category, 100.0),
            "label": "Top Category by CPI",
            "definition": "Normalized course demand index benchmarked against platform average (= 100)."
        },
        "level_distribution": {
            "counts": level_counts,
            "percentages": level_pct,
            "label": "Level Preference Distribution",
            "definition": "Skill-maturity insight tracking beginner vs. intermediate vs. advanced split."
        },
        "age_distribution": {
            "counts": age_dist,
            "percentages": age_pct,
            "label": "Enrollments by Age Group",
            "definition": "Demographic reach across age bands (<18, 18-25, 26-35, 36-45, 45+)."
        },
        "category_popularity_index": cpi
    }


def get_age_group_summary(df):
    """Compute demographic breakdown per age group."""
    grouped = df.groupby("AgeGroup", observed=False)
    summary = grouped.agg(
        TotalEnrollments=("CourseID", "count"),
        UniqueLearners=("UserID", "nunique"),
        BeginnerShare=("CourseLevel", lambda s: (s == "Beginner").mean() * 100),
        IntermediateShare=("CourseLevel", lambda s: (s == "Intermediate").mean() * 100),
        AdvancedShare=("CourseLevel", lambda s: (s == "Advanced").mean() * 100),
        FreeCourseShare=("IsFreeCourse", lambda s: s.mean() * 100),
        AvgSpend=("Amount", "mean") if "Amount" in df.columns else ("CourseID", lambda _: 0.0)
    ).reset_index()
    
    summary["EnrollmentsShare"] = (summary["TotalEnrollments"] / summary["TotalEnrollments"].sum() * 100).round(1)
    summary["CoursesPerLearner"] = (summary["TotalEnrollments"] / summary["UniqueLearners"].clip(lower=1)).round(2)
    return summary


def get_gender_preference_summary(df):
    """Compute gender-specific preferences across course categories, levels, and types."""
    # Category by Gender
    cat_gender = pd.crosstab(
        df["CourseCategory"],
        df["Gender"],
        normalize="columns"
    ) * 100
    cat_gender = cat_gender.round(1)
    
    # Level by Gender
    lvl_gender = pd.crosstab(
        df["CourseLevel"],
        df["Gender"],
        normalize="columns"
    ) * 100
    lvl_gender = lvl_gender.round(1)
    
    # Type by Gender
    type_gender = pd.crosstab(
        df["CourseType"],
        df["Gender"],
        normalize="columns"
    ) * 100
    type_gender = type_gender.round(1)
    
    return {
        "category_gender": cat_gender,
        "level_gender": lvl_gender,
        "type_gender": type_gender
    }


def get_age_category_heatmap_matrix(df, normalize=False):
    """Compute matrix of AgeGroup vs CourseCategory for heatmap visualization.
    
    Args:
        df: Merged enrollments DataFrame.
        normalize: 'index' (row-wise %), 'columns' (col-wise %), or False (raw counts).
    """
    if normalize and normalize in ["index", "columns", "all", True]:
        ct = pd.crosstab(df["AgeGroup"], df["CourseCategory"], normalize=normalize)
        ct = (ct * 100).round(1)
    else:
        ct = pd.crosstab(df["AgeGroup"], df["CourseCategory"])
    return ct


def get_category_metrics(df):
    """Compute comprehensive category-level performance table."""
    grouped = df.groupby("CourseCategory")
    total_enroll = len(df)
    total_courses = df["CourseID"].nunique()
    avg_enroll_per_course = total_enroll / max(total_courses, 1)
    
    metrics = grouped.agg(
        TotalEnrollments=("CourseID", "count"),
        UniqueCourses=("CourseID", "nunique"),
        UniqueLearners=("UserID", "nunique"),
        AvgRating=("CourseRating", "mean") if "CourseRating" in df.columns else ("CourseID", lambda _: 4.5),
        BeginnerCount=("CourseLevel", lambda s: (s == "Beginner").sum()),
        IntermediateCount=("CourseLevel", lambda s: (s == "Intermediate").sum()),
        AdvancedCount=("CourseLevel", lambda s: (s == "Advanced").sum()),
        FreeEnrollments=("IsFreeCourse", lambda s: s.sum()),
        PaidEnrollments=("IsFreeCourse", lambda s: (~s).sum()),
        TotalRevenue=("Amount", "sum") if "Amount" in df.columns else ("CourseID", lambda _: 0.0)
    ).reset_index()
    
    metrics["EnrollmentShare"] = (metrics["TotalEnrollments"] / total_enroll * 100).round(2)
    metrics["EnrollmentPerCourse"] = (metrics["TotalEnrollments"] / metrics["UniqueCourses"].clip(lower=1)).round(1)
    metrics["CategoryPopularityIndex"] = (metrics["EnrollmentPerCourse"] / avg_enroll_per_course * 100).round(1)
    metrics = metrics.sort_values(by="TotalEnrollments", ascending=False)
    
    return metrics


def compute_pareto_analysis(df):
    """Compute Pareto (80/20) concentration of enrollments among active learners.
    
    Returns:
        dict: Pareto metrics, top learner percentiles, and Lorenz curve points.
    """
    user_counts_desc = df.groupby("UserID").size().sort_values(ascending=False).values
    total_users = len(user_counts_desc)
    total_enrollments = sum(user_counts_desc)
    
    # Descending cumulative for Pareto (Top X% of users account for Y% of enrollments)
    cum_desc = np.cumsum(user_counts_desc)
    cum_desc_share = (cum_desc / total_enrollments) * 100
    user_share_desc = (np.arange(1, total_users + 1) / total_users) * 100
    
    # 20% point
    idx_20 = int(total_users * 0.20)
    enrollment_share_top_20 = round(float(cum_desc_share[idx_20 - 1]), 1) if idx_20 > 0 else 0.0
    
    # 10% point
    idx_10 = int(total_users * 0.10)
    enrollment_share_top_10 = round(float(cum_desc_share[idx_10 - 1]), 1) if idx_10 > 0 else 0.0
    
    # Standard Lorenz curve (ascending order) for Gini
    user_counts_asc = np.sort(user_counts_desc)
    cum_asc = np.cumsum(user_counts_asc)
    lorenz = np.insert(cum_asc / total_enrollments, 0, 0)
    # Area under Lorenz curve
    area = np.trapezoid(lorenz, dx=1 / total_users)
    gini = round(float(1 - 2 * area), 3)
    
    # Subsample 100 points for smooth charting of concentration curve
    subsample_indices = np.linspace(0, total_users - 1, 100, dtype=int)
    
    return {
        "top_20_share": enrollment_share_top_20,
        "top_10_share": enrollment_share_top_10,
        "gini_coefficient": gini,
        "total_active_learners": total_users,
        "total_enrollments": total_enrollments,
        "lorenz_user_pct": user_share_desc[subsample_indices].tolist(),
        "lorenz_enroll_pct": cum_desc_share[subsample_indices].tolist()
    }
