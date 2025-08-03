
import openai
import json
from pathlib import Path
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright
from datetime import datetime

# ✅ Use LM Studio Local API
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "lm-studio"  # dummy key

# Your profile summary
USER_PROFILE = {
    "name": "Shri Krishna Gupta",
    "current_role": "Enterprise Applications Specialist at NTT DATA IPS",
    "experience": "5+ years in Sitecore, .NET, SXA, Content Hub",
    "location": "Mumbai, India (Open to relocate, remote, hybrid)",
    "skills": "Sitecore (8.x–10.3), SXA, Docker, Apache Solr, .NET, WinForms, Web API, React, Node.js, Azure, AWS, Git, Jenkins, JS, SCSS",
    "linkedin": "https://www.linkedin.com/in/krishna-gupta-444778122/"
}

PROMPT_TEMPLATE = """\
Write a personalized cover letter for the following job description.

Job Title: {job_title}
Company: {company}
Location: {location}

Job Description:
{job_description}

Applicant Profile:
{profile}

Ensure the tone is professional but enthusiastic, focused on Sitecore/.NET development, and address key job responsibilities. Keep it concise and tailored.
"""

def generate_cover_letter(job_data):
    prompt = PROMPT_TEMPLATE.format(
        job_title=job_data.get("title", "Developer"),
        company=job_data.get("company", "Unknown Company"),
        location=job_data.get("location", "Remote"),
        job_description=job_data.get("description", "No JD Provided"),
        profile=json.dumps(USER_PROFILE, indent=2)
    )

    response = openai.ChatCompletion.create(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a helpful job application assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response['choices'][0]['message']['content'].strip()

def save_letter_to_file(letter, filename="data/cover_letter.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(letter)
    print(f"✅ Cover letter saved to {filename}")

def update_google_sheet(job_data, status="Applied"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("utils/google_sheets_creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Job Tracker").sheet1

    sheet.append_row([
        job_data.get("title", "N/A"),
        job_data.get("company", "N/A"),
        job_data.get("location", "N/A"),
        job_data.get("link", "N/A"),
        job_data.get("description", "N/A")[:100],
        status,
        datetime.now().strftime("%Y-%m-%d")
    ])
    print(f"✅ Google Sheet updated with status: {status}")

def fill_job_form(job_data):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="utils/linkedin_auth.json")
        page = context.new_page()
        page.goto(job_data.get("link"))
        print("📝 Please complete the form manually if needed.")
        page.pause()

        browser.close()

if __name__ == "__main__":
    # Example test run
    example_job = {
        "title": "Sitecore Developer",
        "company": "Tech Solutions Ltd.",
        "location": "Singapore",
        "description": "We are looking for an experienced Sitecore Developer to maintain and build .NET CMS websites for enterprise clients using Sitecore 10.x. Experience with SXA and Azure DevOps preferred.",
        "link": "https://www.example.com/job123"
    }

    letter = generate_cover_letter(example_job)
    save_letter_to_file(letter)
    update_google_sheet(example_job, status="Applied")
    fill_job_form(example_job)
