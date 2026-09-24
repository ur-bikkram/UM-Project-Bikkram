"""Data loader module for EduPro dataset.
Handles fetching from remote Google Sheets export, local caching, and fallback synthetic data generation.
"""

import os
import sys
import urllib.request
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
GOOGLE_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/1Ts1Yjt9oiTdOeCeuJPbExNz7N3vmd0Ln/export?format=xlsx"
)


def ensure_dirs():
    """Ensure raw and processed data directories exist."""
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    processed_dir = os.path.join(os.path.dirname(DATA_RAW_DIR), "processed")
    os.makedirs(processed_dir, exist_ok=True)


def download_official_dataset(output_path=None):
    """Download the official EduPro Excel file from Google Sheets.
    
    Returns:
        str: Path to downloaded Excel file or None if failed.
    """
    ensure_dirs()
    if output_path is None:
        output_path = os.path.join(DATA_RAW_DIR, "EduPro_Online_Platform.xlsx")
    
    try:
        logger.info("Downloading official EduPro dataset from Google Sheets...")
        urllib.request.urlretrieve(GOOGLE_SHEET_URL, output_path)
        logger.info(f"Downloaded successfully to {output_path}")
        return output_path
    except Exception as e:
        logger.warning(f"Could not download from Google Sheets: {e}")
        return None


def extract_sheets_to_csv(excel_path):
    """Extract individual sheets from Excel file into separate CSV files.
    
    Args:
        excel_path (str): Path to the .xlsx file.
        
    Returns:
        dict: Mapping of sheet names to saved CSV filepaths.
    """
    ensure_dirs()
    xls = pd.ExcelFile(excel_path)
    sheet_files = {}
    
    for sheet_name in xls.sheet_names:
        clean_name = sheet_name.lower().strip()
        csv_path = os.path.join(DATA_RAW_DIR, f"{clean_name}.csv")
        df = pd.read_excel(xls, sheet_name=sheet_name)
        df.to_csv(csv_path, index=False)
        logger.info(f"Extracted sheet '{sheet_name}' ({len(df)} rows) to {csv_path}")
        sheet_files[clean_name] = csv_path
        
    return sheet_files


def generate_synthetic_data(num_users=1000, num_courses=40, num_transactions=7500):
    """Generate realistic synthetic dataset conforming strictly to the schema.
    Used as an offline fallback or for testing with believable distributions.
    
    Returns:
        dict of DataFrames: {'users': df, 'courses': df, 'transactions': df}
    """
    ensure_dirs()
    np.random.seed(42)
    
    # 1. Users
    user_ids = [f"U{i:05d}" for i in range(1, num_users + 1)]
    first_names = ["Jordan", "Taylor", "Alex", "Morgan", "Sam", "Chris", "Pat", "Riley", "Casey", "Avery",
                   "Jamie", "Cameron", "Dakota", "Reese", "Quinn", "Skyler", "Kendall", "Hayden", "Rowan", "Peyton"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson",
                  "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White"]
    
    user_names = [f"{np.random.choice(first_names).lower()}{np.random.randint(10, 99)}" for _ in range(num_users)]
    
    # Realistic skewed age distribution (majority 18-35, some <18 and >35)
    ages = np.concatenate([
        np.random.randint(14, 18, size=int(num_users * 0.12)),
        np.random.randint(18, 26, size=int(num_users * 0.48)),
        np.random.randint(26, 36, size=int(num_users * 0.28)),
        np.random.randint(36, 46, size=int(num_users * 0.08)),
        np.random.randint(46, 65, size=int(num_users * 0.04))
    ])
    np.random.shuffle(ages)
    ages = ages[:num_users]
    
    genders = np.random.choice(["Female", "Male"], size=num_users, p=[0.51, 0.49])
    emails = [f"{name}@{np.random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com'])}" for name in user_names]
    
    df_users = pd.DataFrame({
        "UserID": user_ids,
        "UserName": user_names,
        "Age": ages,
        "Gender": genders,
        "Email": emails
    })
    
    # 2. Courses
    categories = [
        "Data Science", "Machine Learning", "Artificial Intelligence", "Programming",
        "Web Development", "Cybersecurity", "Design", "Business", "Marketing",
        "Digital Marketing", "Finance", "Project Management"
    ]
    course_types = ["Free", "Paid"]
    course_levels = ["Beginner", "Intermediate", "Advanced"]
    
    course_ids = [f"C{i:04d}" for i in range(1, num_courses + 1)]
    course_records = []
    
    for i, cid in enumerate(course_ids):
        cat = categories[i % len(categories)]
        lvl = course_levels[i % len(course_levels)]
        ctype = np.random.choice(course_types, p=[0.60, 0.40])
        price = 0.0 if ctype == "Free" else float(np.random.choice([29.99, 49.99, 79.99, 99.99, 149.99]))
        duration = float(np.random.randint(4, 40))
        rating = round(float(np.random.uniform(3.8, 4.95)), 2)
        cname = f"{cat} - {lvl} Masterclass {i+1}"
        course_records.append({
            "CourseID": cid,
            "CourseName": cname,
            "CourseCategory": cat,
            "CourseType": ctype,
            "CourseLevel": lvl,
            "CoursePrice": price,
            "CourseDuration": duration,
            "CourseRating": rating
        })
    df_courses = pd.DataFrame(course_records)
    
    # 3. Transactions (following Pareto / 80-20 law for course enrollments)
    # Give some courses higher inherent popularity (Data Science, Web Dev, Programming)
    popular_categories = ["Data Science", "Programming", "Machine Learning", "Web Development"]
    course_weights = []
    for _, row in df_courses.iterrows():
        base = 3.0 if row["CourseCategory"] in popular_categories else 1.0
        if row["CourseType"] == "Free":
            base *= 1.8
        if row["CourseLevel"] == "Beginner":
            base *= 1.5
        course_weights.append(base)
    course_weights = np.array(course_weights) / sum(course_weights)
    
    # User activity follows Pareto distribution (power law / exponential)
    user_activity_weights = np.random.pareto(a=1.8, size=num_users) + 0.1
    user_activity_weights /= user_activity_weights.sum()
    
    tx_records = []
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range_days = (end_date - start_date).days
    
    chosen_pairs = set()
    attempts = 0
    max_attempts = num_transactions * 4
    
    while len(tx_records) < num_transactions and attempts < max_attempts:
        attempts += 1
        uid = np.random.choice(user_ids, p=user_activity_weights)
        cid = np.random.choice(course_ids, p=course_weights)
        if (uid, cid) in chosen_pairs:
            continue
        chosen_pairs.add((uid, cid))
        
        tx_id = f"T{len(tx_records)+1:06d}"
        random_days = np.random.randint(0, date_range_days + 1)
        tx_date = start_date + timedelta(days=random_days)
        course_row = df_courses[df_courses["CourseID"] == cid].iloc[0]
        amount = course_row["CoursePrice"]
        payment_method = "Free" if amount == 0 else np.random.choice(["Credit Card", "PayPal", "Debit Card", "UPI"])
        
        tx_records.append({
            "TransactionID": tx_id,
            "UserID": uid,
            "CourseID": cid,
            "TransactionDate": tx_date.strftime("%Y-%m-%d"),
            "Amount": amount,
            "PaymentMethod": payment_method,
            "TeacherID": f"TCH{np.random.randint(1, 20):03d}"
        })
        
    df_tx = pd.DataFrame(tx_records)
    
    # Save CSVs
    df_users.to_csv(os.path.join(DATA_RAW_DIR, "users.csv"), index=False)
    df_courses.to_csv(os.path.join(DATA_RAW_DIR, "courses.csv"), index=False)
    df_tx.to_csv(os.path.join(DATA_RAW_DIR, "transactions.csv"), index=False)
    logger.info("Generated and saved synthetic data fallback.")
    
    return {"users": df_users, "courses": df_courses, "transactions": df_tx}


def load_raw_data(force_download=False):
    """Load or fetch raw datasets (users, courses, transactions).
    
    Returns:
        tuple: (df_users, df_courses, df_transactions)
    """
    ensure_dirs()
    users_csv = os.path.join(DATA_RAW_DIR, "users.csv")
    courses_csv = os.path.join(DATA_RAW_DIR, "courses.csv")
    tx_csv = os.path.join(DATA_RAW_DIR, "transactions.csv")
    excel_path = os.path.join(DATA_RAW_DIR, "EduPro_Online_Platform.xlsx")
    
    if not force_download and os.path.exists(users_csv) and os.path.exists(courses_csv) and os.path.exists(tx_csv):
        logger.info("Loading existing raw CSV datasets from data/raw/...")
        return pd.read_csv(users_csv), pd.read_csv(courses_csv), pd.read_csv(tx_csv)
    
    # Try downloading official Excel
    if not os.path.exists(excel_path) or force_download:
        download_official_dataset(excel_path)
        
    if os.path.exists(excel_path):
        sheet_files = extract_sheets_to_csv(excel_path)
        if "users" in sheet_files and "courses" in sheet_files and "transactions" in sheet_files:
            return (
                pd.read_csv(sheet_files["users"]),
                pd.read_csv(sheet_files["courses"]),
                pd.read_csv(sheet_files["transactions"]),
            )
            
    # Check if root workspace has exported Users CSV
    root_users = os.path.join(os.path.dirname(DATA_RAW_DIR), "..", "EduPro Online Platform.xlsx - Users.csv")
    if os.path.exists(root_users):
        logger.info("Found root Users CSV. Generating matched synthetic courses & transactions to preserve official Users...")
        df_users = pd.read_csv(root_users)
        df_users.to_csv(users_csv, index=False)
        # Generate courses & transactions for existing users
        synth = generate_synthetic_data(num_users=len(df_users), num_courses=60, num_transactions=10000)
        df_users.to_csv(users_csv, index=False)
        return df_users, synth["courses"], synth["transactions"]

    logger.warning("Using synthetic data generator as fallback...")
    synth = generate_synthetic_data()
    return synth["users"], synth["courses"], synth["transactions"]


if __name__ == "__main__":
    u, c, t = load_raw_data(force_download=True)
    print(f"Loaded {len(u)} users, {len(c)} courses, and {len(t)} transactions.")
