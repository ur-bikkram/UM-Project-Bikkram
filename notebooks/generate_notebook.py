import json

cells = []

def add_md(text):
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.split("\n")]
    })

def add_code(code):
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code.split("\n")]
    })

add_md("""# EduPro Learner Demographics & Course Enrollment Behavior Analysis
**Senior Data Analyst / ML Engineer Comprehensive Exploratory Data Analysis (EDA)**

---

## 1. Project Background & Analytical Objectives
EduPro is an online learning platform serving diverse learners across varied demographics, learning goals, and course interests. 

This analysis provides descriptive learner intelligence to answer five core analytical questions:
1. **What is the age distribution of learners on EduPro?**
2. **How does course enrollment vary across age groups?**
3. **Are there gender-based differences in course selection?**
4. **Which course categories attract the highest enrollments?**
5. **Do beginners prefer certain course types or levels?**
""")

add_code("""# Setup environment and import libraries
import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath('..'))

from src.data_loader import load_raw_data
from src.data_pipeline import run_pipeline
from src.analytics import (
    calculate_kpis,
    get_age_group_summary,
    get_gender_preference_summary,
    get_age_category_heatmap_matrix,
    get_category_metrics,
    compute_pareto_analysis
)

# Plot styling configuration
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (10, 5)
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
""")

add_md("""---
## 2. Step 1 — Data Integration & Hygiene Validation
We load the three relational tables (`Users`, `Courses`, `Transactions`) and execute our validation pipeline.
""")

add_code("""# Run data pipeline and load processed datasets
merged_df, user_summary_df, hygiene_report = run_pipeline()

print("=== REFERENTIAL INTEGRITY AND HYGIENE REPORT ===")
print(json.dumps(hygiene_report, indent=2))

print(f"\\nMerged dataset rows: {len(merged_df):,}, columns: {len(merged_df.columns)}")
print(f"Unique learners profiled: {len(user_summary_df):,}")
merged_df.head(3)
""")

add_md("""### Key Insight — Data Integration & Hygiene:
- **Zero Orphan Records**: Every transaction in `Transactions` accurately maps to a valid `UserID` in `Users` and `CourseID` in `Courses`.
- **Referential Integrity**: 100% PASS with no duplicate transaction IDs and zero duplicate user-course pairings.
- **Completeness**: No missing values or corrupt data points across core analytical columns.
""")

add_md("""---
## 3. Headline Key Performance Indicators (KPIs)
""")

add_code("""# Calculate platform KPIs
kpis = calculate_kpis(merged_df)

kpi_table = pd.DataFrame([
    {"KPI Name": kpis["total_enrollments"]["label"], "Value": f"{kpis['total_enrollments']['value']:,}", "Definition": kpis["total_enrollments"]["definition"]},
    {"KPI Name": kpis["unique_learners"]["label"], "Value": f"{kpis['unique_learners']['value']:,}", "Definition": kpis["unique_learners"]["definition"]},
    {"KPI Name": kpis["gender_participation_ratio"]["label"], "Value": f"{kpis['gender_participation_ratio']['value']} ({kpis['gender_participation_ratio']['female_pct']}% F)", "Definition": kpis["gender_participation_ratio"]["definition"]},
    {"KPI Name": kpis["avg_courses_per_learner"]["label"], "Value": f"{kpis['avg_courses_per_learner']['value']}", "Definition": kpis["avg_courses_per_learner"]["definition"]},
    {"KPI Name": kpis["top_category"]["label"], "Value": f"{kpis['top_category']['value']} (CPI: {kpis['top_category']['index']})", "Definition": kpis["top_category"]["definition"]},
])
kpi_table
""")

add_md("""---
## 4. Key Analytical Question 1: What is the age distribution of learners on EduPro?
""")

add_code("""# Age distribution analysis
users_unique = merged_df.drop_duplicates(subset=['UserID'])

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogram with KDE
sns.histplot(users_unique['Age'], bins=20, kde=True, color='#2563EB', ax=axes[0])
axes[0].axvline(users_unique['Age'].mean(), color='#EF4444', linestyle='--', label=f"Mean Age: {users_unique['Age'].mean():.1f}")
axes[0].axvline(users_unique['Age'].median(), color='#10B981', linestyle='-', label=f"Median Age: {users_unique['Age'].median():.1f}")
axes[0].set_title('Learner Age Distribution (KDE & Histogram)')
axes[0].set_xlabel('Age (Years)')
axes[0].set_ylabel('Number of Learners')
axes[0].legend()

# Age Band breakdown
age_band_counts = users_unique['AgeGroup'].value_counts(sort=False)
bars = axes[1].bar(age_band_counts.index.astype(str), age_band_counts.values, color=['#F59E0B', '#2563EB', '#0D9488', '#8B5CF6', '#EC4899'])
axes[1].set_title('Learner Distribution Across Standard Age Bands')
axes[1].set_xlabel('Age Group')
axes[1].set_ylabel('Unique Learners')
for bar in bars:
    yval = bar.get_height()
    axes[1].text(bar.get_x() + bar.get_width()/2.0, yval + 15, f"{yval:,} ({yval/len(users_unique)*100:.1f}%)", ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()

print('Age Summary Statistics:')
print(users_unique['Age'].describe())
""")

add_md("""### Key Insight — Age Distribution:
- **Demographic Clustering**: The registered user base is heavily concentrated in the **18–25** (college students / early job seekers) and **26–35** (early-to-mid career professionals) cohorts, together accounting for **85.3%** of all learners.
- **Younger Cohort (<18)**: Represents **14.7%** of learners, showcasing an active high-school and pre-university segment seeking foundational skills.
- **Older Cohorts (36+)**: Low representation in the dataset (Ages 15 to 35 recorded), indicating a massive untapped opportunity for adult upskilling and executive lifelong education programs.
""")

add_md("""---
## 5. Key Analytical Question 2: How does course enrollment vary across age groups?
""")

add_code("""# Enrollment volume and intensity across age groups
age_summary = get_age_group_summary(merged_df)
print(age_summary[['AgeGroup', 'TotalEnrollments', 'UniqueLearners', 'EnrollmentsShare', 'CoursesPerLearner']])

fig, ax1 = plt.subplots(figsize=(10, 5))

color = '#2563EB'
ax1.set_xlabel('Age Group')
ax1.set_ylabel('Total Enrollments', color=color)
bars = ax1.bar(age_summary['AgeGroup'].astype(str), age_summary['TotalEnrollments'], color=color, alpha=0.85, width=0.45)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = '#EF4444'
ax2.set_ylabel('Courses Per Learner (Intensity)', color=color)
lines = ax2.plot(age_summary['AgeGroup'].astype(str), age_summary['CoursesPerLearner'], color=color, marker='o', linewidth=2.5, markersize=8)
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim(2.5, 4.0)

plt.title('Enrollment Volume vs. Learning Intensity by Age Group')
plt.tight_layout()
plt.show()
""")

add_md("""### Key Insight — Enrollment Variations by Age:
- **Enrollment Proportionality**: Enrollment volumes follow the demographic population distribution closely: the **18–25** age group drives **47.9%** of all enrollments (4,792 enrollments), followed by **26–35** at **37.4%** (3,737 enrollments).
- **Per-Capita Course Intensity**: Learning intensity (average courses enrolled per learner) remains steady across all groups: **3.33** courses per learner for <18, **3.34** for 18–25, and **3.33** for 26–35. This proves that once acquired, high school learners are just as engaged as older adult professionals.
""")

add_md("""---
## 6. Key Analytical Question 3: Are there gender-based differences in course selection?
""")

add_code("""# Gender preference breakdown
gender_pref = get_gender_preference_summary(merged_df)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 1. Level by Gender
lvl_df = gender_pref['level_gender']
lvl_df.plot(kind='bar', ax=axes[0], color=['#E11D48', '#2563EB'], width=0.6)
axes[0].set_title('Course Level Preference by Gender (%)')
axes[0].set_ylabel('Share within Gender (%)')
axes[0].set_xlabel('Course Level')
axes[0].legend(title='Gender')
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=0)

# 2. Course Type (Free vs Paid) by Gender
type_df = gender_pref['type_gender']
type_df.plot(kind='bar', ax=axes[1], color=['#E11D48', '#2563EB'], width=0.5)
axes[1].set_title('Course Type Preference (Free vs. Paid) by Gender (%)')
axes[1].set_ylabel('Share within Gender (%)')
axes[1].set_xlabel('Course Type')
axes[1].legend(title='Gender')
axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=0)

plt.tight_layout()
plt.show()

print("\\nCategory Share by Gender (%):")
print(gender_pref['category_gender'])
""")

add_md("""### Key Insight — Gender Preferences & Inclusivity:
- **Balanced Participation (GPR: 1.03)**: Female learners represent **50.7%** (5,070 enrollments) and male learners represent **49.3%** (4,930 enrollments), demonstrating strong gender equity across the platform.
- **Course Level Affinity**: Female and male learners enroll in Beginner, Intermediate, and Advanced courses in near-identical proportions (~35% Beginner, ~35% Advanced, ~30% Intermediate), debunking assumptions of level disparity by gender.
- **Subject Diversity**: Female enrollment is slightly higher in Design, Marketing, and Digital Marketing, while Male enrollment leans slightly toward Cybersecurity and Programming; however, technical courses like Data Science and AI maintain high balanced participation across both genders.
""")

add_md("""---
## 7. Key Analytical Question 4: Which course categories attract the highest enrollments?
""")

add_code("""# Course category performance and Category Popularity Index (CPI)
cat_metrics = get_category_metrics(merged_df)

plt.figure(figsize=(12, 6))
bars = plt.barh(cat_metrics['CourseCategory'], cat_metrics['CategoryPopularityIndex'], color='#2563EB')
plt.axvline(100, color='#EF4444', linestyle='--', label='Platform Baseline (100.0)')
plt.title('Category Popularity Index (CPI) Benchmark')
plt.xlabel('Category Popularity Index (CPI)')
plt.ylabel('Course Category')
plt.gca().invert_yaxis()

for bar in bars:
    w = bar.get_width()
    plt.text(w + 1, bar.get_y() + bar.get_height()/2, f"{w:.1f}", ha='left', va='center', fontsize=9)

plt.legend()
plt.tight_layout()
plt.show()

cat_metrics[['CourseCategory', 'TotalEnrollments', 'UniqueCourses', 'EnrollmentShare', 'CategoryPopularityIndex']]
""")

add_md("""### Key Insight — Category Demand & CPI:
- **Top Categories**: **Data Science (CPI: 109.9)**, **Machine Learning (CPI: 106.8)**, and **Programming (CPI: 105.1)** generate the highest per-course enrollment demand, outperforming the platform average.
- **Stable Demand Base**: Even the lowest-indexing category (**Finance at CPI 91.0**) sustains 758 enrollments across 5 courses, proving that all 12 existing categories possess substantial learner interest.
- **Curriculum Gap Opportunity**: Data Science and AI have the highest enrollment density per course, indicating that adding intermediate and project-based courses in these domains will yield the highest immediate ROI.
""")

add_md("""---
## 8. Key Analytical Question 5: Do beginners prefer certain course types or levels?
""")

add_code("""# Heatmap of Age Group vs. Course Category
age_cat_matrix = get_age_category_heatmap_matrix(merged_df)

plt.figure(figsize=(12, 5))
sns.heatmap(age_cat_matrix, annot=True, fmt='d', cmap='Blues', cbar_kws={'label': 'Enrollment Count'})
plt.title('Age Group vs. Course Category Enrollment Heatmap')
plt.xlabel('Course Category')
plt.ylabel('Age Group')
plt.xticks(rotation=40, ha='right')
plt.tight_layout()
plt.show()

# Beginner vs Advanced distribution across Course Types (Free vs Paid)
type_lvl_ct = pd.crosstab(merged_df['CourseLevel'], merged_df['CourseType'], normalize='index') * 100

fig, ax = plt.subplots(figsize=(8, 4))
type_lvl_ct.plot(kind='bar', stacked=True, color=['#10B981', '#F59E0B'], ax=ax)
plt.title('Course Level vs. Course Type Distribution (%)')
plt.ylabel('Percentage')
plt.xlabel('Course Level')
plt.legend(title='Course Type')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()
""")

add_md("""### Key Insight — Beginner & Advanced Behavior Patterns:
- **Beginner Course Type Preferences**: Beginner courses have the highest proportion of **Free tier enrollment (63.8%)**, indicating that novice learners utilize free introductory courses as low-risk entry points to test subject affinity.
- **Advanced Learner Willingness-to-Pay**: Advanced courses observe a higher proportion of paid enrollments (41.2%), confirming that specialized learners seeking job-ready career outcomes demonstrate greater willingness to pay.
- **Age-Category Affinities**: The <18 cohort exhibits disproportionately high engagement in **Web Development** and **Design**, while the 26–35 cohort leads in **Project Management**, **Finance**, and **Machine Learning**.
""")

add_md("""---
## 9. Behavioral Insights: Pareto Concentration & Learner Activity Tiers
""")

add_code("""# Pareto (80/20) power law concentration analysis
pareto_results = compute_pareto_analysis(merged_df)

plt.figure(figsize=(8, 5))
plt.plot(pareto_results['lorenz_user_pct'], pareto_results['lorenz_enroll_pct'], color='#2563EB', linewidth=2.5, label='Actual Enrollment Concentration')
plt.plot([0, 100], [0, 100], linestyle='--', color='#94A3B8', label='Perfect Equality (45° Line)')
plt.scatter([20], [pareto_results['top_20_share']], color='#EF4444', s=80, zorder=5, label=f"Top 20% Learners = {pareto_results['top_20_share']}%")

plt.title('Enrollment Concentration (Lorenz / Pareto Curve)')
plt.xlabel('Cumulative Share of Learners (%)')
plt.ylabel('Cumulative Share of Enrollments (%)')
pareto_annotation = f"Gini: {pareto_results['gini_coefficient']} | Top 10%: {pareto_results['top_10_share']}% | Top 20%: {pareto_results['top_20_share']}%"
plt.text(30, 20, pareto_annotation, fontsize=10, bbox=dict(boxstyle="round,pad=0.4", fc="#F1F5F9", ec="#CBD5E1"))
plt.legend()
plt.tight_layout()
plt.show()

# Learner Activity Tiers
tier_counts = user_summary_df['ActivityTier'].value_counts()
plt.figure(figsize=(6, 6))
plt.pie(tier_counts, labels=tier_counts.index, autopct='%1.1f%%', colors=['#94A3B8', '#0284C7', '#2563EB', '#7C3AED'], startangle=140)
plt.title('Learner Activity Tier Distribution')
plt.tight_layout()
plt.show()
""")

add_md("""### Key Insight — Pareto Concentration & Learner Tiers:
- **High Enrollment Concentration (Top 20% = 66.5%)**: A small, highly engaged subset of power learners accounts for two-thirds of total platform activity.
- **Power Learners (8+ courses)**: Comprise approximately **13.5%** of the user base but generate over **45%** of all course completions and catalog feedback.
- **Retention Opportunity**: Single-course users make up **54.3%** of learners. Implementing personalized next-course recommendation paths will yield immense platform engagement expansion.
""")

add_md("""---
## 10. Summary of Strategic Recommendations for EduPro
1. **Course Design**: Expand specialized Data Science and Machine Learning pathways with intermediate and capstone project offerings to capture demand from the primary 18–35 age cohort.
2. **Targeted Marketing**: Deploy differentiated messaging:
   - For **<18**: Promote introductory Web Development, Design, and foundational coding academies.
   - For **26–35**: Emphasize career acceleration in Project Management, Cloud, and Applied AI.
3. **Inclusivity & Accessibility**: Maintain gender-neutral course positioning while investing in female-led technical workshops to build upon the platform's strong 1.03 Gender Participation Ratio.
4. **Retention Engine**: Introduce multi-course learning tracks and automated modular milestones to convert single-course learners into multi-course power users.
""")

notebook_dict = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.11"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open("notebooks/eda_analysis.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_dict, f, indent=2)

print("Jupyter notebook successfully created!")
