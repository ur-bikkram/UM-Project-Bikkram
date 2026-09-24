"""Data integration, cleaning, and feature engineering pipeline for EduPro.
Validates referential integrity, segments learners into standard age bands,
derives behavioral attributes, and exports processed datasets.
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

AGE_BINS = [-np.inf, 17, 25, 35, 45, np.inf]
AGE_LABELS = ["<18", "18–25", "26–35", "36–45", "45+"]


def segment_age(age_series):
    """Categorize numerical age into standard demographic bands."""
    return pd.cut(age_series, bins=AGE_BINS, labels=AGE_LABELS, right=True)


def validate_referential_integrity(df_users, df_courses, df_transactions):
    """Check referential integrity across related tables and return a diagnostic report."""
    user_ids = set(df_users["UserID"].dropna())
    course_ids = set(df_courses["CourseID"].dropna())
    
    tx_user_ids = set(df_transactions["UserID"].dropna())
    tx_course_ids = set(df_transactions["CourseID"].dropna())
    
    orphan_user_tx = df_transactions[~df_transactions["UserID"].isin(user_ids)]
    orphan_course_tx = df_transactions[~df_transactions["CourseID"].isin(course_ids)]
    
    duplicate_tx_ids = df_transactions["TransactionID"].duplicated().sum()
    duplicate_enrollments = df_transactions.duplicated(subset=["UserID", "CourseID"]).sum()
    
    null_users = df_users.isnull().sum().to_dict()
    null_courses = df_courses.isnull().sum().to_dict()
    null_tx = df_transactions.isnull().sum().to_dict()
    
    invalid_ages = df_users[(df_users["Age"] < 5) | (df_users["Age"] > 110)]
    valid_genders = {"Female", "Male", "Other", "Non-Binary"}
    invalid_genders = df_users[~df_users["Gender"].isin(valid_genders)]
    
    report = {
        "total_users": len(df_users),
        "total_courses": len(df_courses),
        "total_transactions": len(df_transactions),
        "unique_enrolled_users": len(tx_user_ids),
        "unique_enrolled_courses": len(tx_course_ids),
        "orphan_user_transactions": int(len(orphan_user_tx)),
        "orphan_course_transactions": int(len(orphan_course_tx)),
        "duplicate_transaction_ids": int(duplicate_tx_ids),
        "duplicate_user_course_enrollments": int(duplicate_enrollments),
        "null_counts": {
            "users": {k: int(v) for k, v in null_users.items()},
            "courses": {k: int(v) for k, v in null_courses.items()},
            "transactions": {k: int(v) for k, v in null_tx.items()}
        },
        "invalid_age_count": int(len(invalid_ages)),
        "invalid_gender_count": int(len(invalid_genders)),
        "integrity_status": "PASS" if len(orphan_user_tx) == 0 and len(orphan_course_tx) == 0 and duplicate_tx_ids == 0 else "WARNINGS_FOUND"
    }
    
    logger.info(f"Referential Integrity Check: {report['integrity_status']}")
    logger.info(f"Orphan User TX: {report['orphan_user_transactions']}, Orphan Course TX: {report['orphan_course_transactions']}")
    logger.info(f"Duplicate TX IDs: {report['duplicate_transaction_ids']}")
    
    return report


def run_pipeline(force_download=False):
    """Execute complete data integration, validation, cleaning, and export."""
    os.makedirs(DATA_PROCESSED_DIR, exist_ok=True)
    from src.data_loader import load_raw_data
    
    users, courses, tx = load_raw_data(force_download=force_download)
    
    # 1. Validation & Integrity Check
    hygiene_report = validate_referential_integrity(users, courses, tx)
    with open(os.path.join(DATA_PROCESSED_DIR, "data_hygiene_report.json"), "w") as f:
        json.dump(hygiene_report, f, indent=2)
        
    # 2. Cleaning Users Table
    users_clean = users.copy()
    users_clean["UserID"] = users_clean["UserID"].astype(str).str.strip()
    users_clean["UserName"] = users_clean["UserName"].astype(str).str.strip()
    users_clean["Gender"] = users_clean["Gender"].astype(str).str.strip().str.title()
    users_clean["Age"] = pd.to_numeric(users_clean["Age"], errors="coerce")
    
    # Handle invalid or missing ages (median imputation if any, log action)
    if users_clean["Age"].isnull().any() or (users_clean["Age"] < 10).any():
        med_age = users_clean.loc[(users_clean["Age"] >= 10) & (users_clean["Age"] <= 100), "Age"].median()
        users_clean["Age"] = users_clean["Age"].fillna(med_age).clip(10, 100).astype(int)
    else:
        users_clean["Age"] = users_clean["Age"].astype(int)
        
    users_clean["AgeGroup"] = segment_age(users_clean["Age"])
    
    # 3. Cleaning Courses Table
    courses_clean = courses.copy()
    courses_clean["CourseID"] = courses_clean["CourseID"].astype(str).str.strip()
    courses_clean["CourseName"] = courses_clean["CourseName"].astype(str).str.strip()
    courses_clean["CourseCategory"] = courses_clean["CourseCategory"].astype(str).str.strip()
    courses_clean["CourseLevel"] = courses_clean["CourseLevel"].astype(str).str.strip().str.title()
    courses_clean["CourseType"] = courses_clean["CourseType"].astype(str).str.strip().str.title()
    
    if "CoursePrice" in courses_clean.columns:
        courses_clean["CoursePrice"] = pd.to_numeric(courses_clean["CoursePrice"], errors="coerce").fillna(0.0)
    else:
        courses_clean["CoursePrice"] = 0.0
        
    if "CourseDuration" in courses_clean.columns:
        courses_clean["CourseDuration"] = pd.to_numeric(courses_clean["CourseDuration"], errors="coerce").fillna(10.0)
        
    if "CourseRating" in courses_clean.columns:
        courses_clean["CourseRating"] = pd.to_numeric(courses_clean["CourseRating"], errors="coerce").fillna(4.5)
        
    # Standardize Course Level ordering
    level_order = ["Beginner", "Intermediate", "Advanced"]
    courses_clean["CourseLevel"] = pd.Categorical(courses_clean["CourseLevel"], categories=level_order, ordered=True)
    
    # 4. Cleaning Transactions Table
    tx_clean = tx.copy()
    tx_clean["TransactionID"] = tx_clean["TransactionID"].astype(str).str.strip()
    tx_clean["UserID"] = tx_clean["UserID"].astype(str).str.strip()
    tx_clean["CourseID"] = tx_clean["CourseID"].astype(str).str.strip()
    tx_clean["TransactionDate"] = pd.to_datetime(tx_clean["TransactionDate"], errors="coerce")
    
    # Drop orphan records if any
    tx_clean = tx_clean[tx_clean["UserID"].isin(users_clean["UserID"]) & tx_clean["CourseID"].isin(courses_clean["CourseID"])]
    tx_clean = tx_clean.drop_duplicates(subset=["TransactionID"])
    
    # 5. Integration / Merge (Users <-> Transactions <-> Courses)
    merged = tx_clean.merge(users_clean, on="UserID", how="inner", suffixes=("", "_user"))
    merged = merged.merge(courses_clean, on="CourseID", how="inner", suffixes=("", "_course"))
    
    # 6. Feature Engineering on Merged Data
    merged["TransactionYear"] = merged["TransactionDate"].dt.year
    merged["TransactionMonth"] = merged["TransactionDate"].dt.month
    merged["TransactionMonthName"] = merged["TransactionDate"].dt.strftime("%b %Y")
    merged["TransactionQuarter"] = "Q" + merged["TransactionDate"].dt.quarter.astype(str) + " " + merged["TransactionDate"].dt.year.astype(str)
    merged["DayOfWeek"] = merged["TransactionDate"].dt.day_name()
    
    # Learner per-capita intensity
    user_tx_counts = merged.groupby("UserID")["CourseID"].transform("count")
    merged["UserEnrollmentCount"] = user_tx_counts
    
    # Activity Tiers
    def categorize_activity(count):
        if count == 1:
            return "Single-Course (1)"
        elif 2 <= count <= 3:
            return "Moderate (2-3)"
        elif 4 <= count <= 7:
            return "Active (4-7)"
        else:
            return "Power Learner (8+)"
            
    merged["LearnerActivityTier"] = merged["UserEnrollmentCount"].apply(categorize_activity)
    tier_order = ["Single-Course (1)", "Moderate (2-3)", "Active (4-7)", "Power Learner (8+)"]
    merged["LearnerActivityTier"] = pd.Categorical(merged["LearnerActivityTier"], categories=tier_order, ordered=True)
    
    merged["IsFreeCourse"] = (merged["CourseType"] == "Free") | (merged["CoursePrice"] == 0)
    
    # 7. Aggregate User Summary Table (1 row per learner)
    user_grp = merged.groupby("UserID")
    user_summary_records = []
    
    for uid, group in user_grp:
        fav_cat = group["CourseCategory"].mode()[0] if not group["CourseCategory"].empty else "N/A"
        dom_lvl = group["CourseLevel"].mode()[0] if not group["CourseLevel"].empty else "Beginner"
        user_row = users_clean[users_clean["UserID"] == uid].iloc[0]
        
        user_summary_records.append({
            "UserID": uid,
            "UserName": user_row["UserName"],
            "Age": user_row["Age"],
            "AgeGroup": str(user_row["AgeGroup"]),
            "Gender": user_row["Gender"],
            "Email": user_row.get("Email", f"{user_row['UserName']}@example.com"),
            "TotalEnrollments": len(group),
            "TotalSpend": float(group["Amount"].sum()) if "Amount" in group.columns else 0.0,
            "FavoriteCategory": fav_cat,
            "DominantLevel": str(dom_lvl),
            "FreeCoursesTaken": int((group["CourseType"] == "Free").sum()),
            "PaidCoursesTaken": int((group["CourseType"] == "Paid").sum()),
            "FirstEnrollmentDate": group["TransactionDate"].min().strftime("%Y-%m-%d"),
            "LastEnrollmentDate": group["TransactionDate"].max().strftime("%Y-%m-%d"),
            "ActivityTier": categorize_activity(len(group))
        })
        
    df_user_summary = pd.DataFrame(user_summary_records)
    
    # Include users who never enrolled if any exist in users table
    non_enrolled_uids = set(users_clean["UserID"]) - set(df_user_summary["UserID"])
    if non_enrolled_uids:
        non_enrolled_records = []
        for uid in non_enrolled_uids:
            urow = users_clean[users_clean["UserID"] == uid].iloc[0]
            non_enrolled_records.append({
                "UserID": uid,
                "UserName": urow["UserName"],
                "Age": urow["Age"],
                "AgeGroup": str(urow["AgeGroup"]),
                "Gender": urow["Gender"],
                "Email": urow.get("Email", f"{urow['UserName']}@example.com"),
                "TotalEnrollments": 0,
                "TotalSpend": 0.0,
                "FavoriteCategory": "None",
                "DominantLevel": "None",
                "FreeCoursesTaken": 0,
                "PaidCoursesTaken": 0,
                "FirstEnrollmentDate": None,
                "LastEnrollmentDate": None,
                "ActivityTier": "Inactive (0)"
            })
        df_user_summary = pd.concat([df_user_summary, pd.DataFrame(non_enrolled_records)], ignore_index=True)
        
    # 8. Export Processed Datasets
    merged_path = os.path.join(DATA_PROCESSED_DIR, "merged_enrollments.csv")
    user_summary_path = os.path.join(DATA_PROCESSED_DIR, "user_summary.csv")
    
    merged.to_csv(merged_path, index=False)
    df_user_summary.to_csv(user_summary_path, index=False)
    
    logger.info(f"Processed dataset successfully saved: {merged_path} ({len(merged)} rows, {len(merged.columns)} columns)")
    logger.info(f"User summary successfully saved: {user_summary_path} ({len(df_user_summary)} users)")
    
    return merged, df_user_summary, hygiene_report


if __name__ == "__main__":
    m, u, r = run_pipeline()
    print("Pipeline executed successfully!")
    print(f"Merged Enrollments: {len(m)}, Users Profiled: {len(u)}")
