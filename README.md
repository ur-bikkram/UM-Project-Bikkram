# EduPro Learner Demographics and Course Enrollment Analysis

This project provides a descriptive analysis of learner demographics and course enrollment patterns on EduPro. The dataset contains 10,000 course registrations across 3,000 active learners and 60 courses recorded in 2025.

## Summary of Findings

- **Age Distribution**: 85.6% of learners are between 18 and 35 years old (average age is 25.0 years). High school learners (<18) make up 14.4%. Learners over 35 are not currently represented in the dataset.
- **Enrollment Intensity**: Average courses per learner is steady at 3.32 to 3.39 across all age groups. Total enrollment volume aligns with the population size of each cohort.
- **Gender Balance**: Course enrollment is 50.8% female and 49.2% male. Technical subjects like Data Science and Artificial Intelligence have near-equal gender participation.
- **Course Demand**: Data Science, Finance, and Web Development have the highest enrollment density per course, performing above the platform average.
- **Course Levels and Pricing**: Beginner courses rely heavily on free tiers (67.0% free enrollment). Advanced courses have the highest paid enrollment share (42.3%).
- **User Activity**: The top 20% of learners account for 66.5% of total enrollments. About 54% of learners have enrolled in only one course so far.

## Project Structure

```
EduPro/
├── data/
│   ├── raw/                           # Extracted CSV files from source
│   │   ├── users.csv                  # 3,000 learner records
│   │   ├── courses.csv                # 60 course offerings
│   │   └── transactions.csv           # 10,000 transaction records
│   └── processed/
│       ├── merged_enrollments.csv     # Clean merged dataset (10,000 rows)
│       ├── user_summary.csv           # Learner summary profiles (3,000 rows)
│       └── data_hygiene_report.json   # Integrity check log
├── notebooks/
│   └── eda_analysis.ipynb             # Jupyter notebook with step-by-step analysis
├── src/
│   ├── data_loader.py                 # Downloads raw tables and extracts CSVs
│   ├── data_pipeline.py               # Merges tables, cleans data, checks integrity
│   ├── analytics.py                   # KPI calculation and Pareto metrics
│   └── visualizations.py              # Plotly chart builders
├── app/
│   ├── app.py                         # Streamlit dashboard landing page
│   ├── utils.py                       # Filter logic and UI cards
│   └── pages/
│       ├── 1_Demographic_Overview.py     # Age and gender distribution
│       ├── 2_Age_Enrollment_Patterns.py  # Age vs category heatmap
│       ├── 3_Gender_Preferences.py       # Subject and level breakdown by gender
│       ├── 4_Category_Popularity.py      # Category popularity index (CPI)
│       └── 5_Behavioral_Insights.py      # Pareto curve and activity tiers
├── reports/
│   ├── research_paper.md              # Research paper with full analysis
│   └── executive_summary.md           # Non-technical summary
├── requirements.txt                   # Dependency list
└── README.md                          # Project documentation
```
