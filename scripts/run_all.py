# run_all.py — Scrape → Generate → Save → Apply

import pandas as pd
from cover_letter_generator_LMStudio import generate_cover_letter, save_letter_to_file, update_google_sheet, fill_job_form
from linkedin_scraper import scrape_linkedin_jobs, save_jobs
from pathlib import Path

# Paths
csv_path = "data/jobs.csv"
Path("data").mkdir(exist_ok=True)

# Step 1: Scrape fresh jobs
keywords = ["Sitecore Developer", ".NET Developer", "Full Stack Developer"]
locations = ["Australia", "Singapore", "Japan"]
jobs = scrape_linkedin_jobs(keywords, locations, max_jobs=5)

print(f"\n🔍 Scraped {len(jobs)} jobs from LinkedIn.")

if not jobs:
    print("⚠️ No jobs found! Try changing keywords or check LinkedIn login/session.")
    exit()

save_jobs(jobs, csv_path)

# Step 2: Process each job
for idx, job in enumerate(jobs, start=1):
    print(f"\n🧠 [{idx}/{len(jobs)}] Generating cover letter for: {job['title']} at {job['company']}")
    try:
        letter = generate_cover_letter(job)
        save_letter_to_file(letter, filename="data/cover_letter.txt")
        update_google_sheet(job, status="Applied")
        fill_job_form(job)
    except Exception as e:
        print(f"❌ Error processing job: {e}")
        continue

print("\n✅ All jobs processed!")
