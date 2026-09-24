"""Streamlit Cloud root entry point for EduPro Analytics.
Redirects execution to app/app.py while ensuring proper module paths.
"""
import os
import sys

# Ensure root directory and app directory are on sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(ROOT_DIR, "app")

for p in (ROOT_DIR, APP_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# Run main app script
if __name__ == "__main__":
    import runpy
    app_path = os.path.join(APP_DIR, "app.py")
    runpy.run_path(app_path, run_name="__main__")
