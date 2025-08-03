# linkedin_scraper.py (Playwright-based)

from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime

def scrape_linkedin_jobs(keywords, locations, max_jobs=10):
    jobs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="utils/linkedin_auth.json")
        page = context.new_page()

        for keyword in keywords:
            for loc in locations:
                print(f"\n🔍 Searching: {keyword} in {loc}")
                url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={loc}&f_TP=1&position=1&pageNum=0"
                try:
                    page.goto(url, timeout=60000)
                    page.wait_for_timeout(2000)  # Wait for JS to populate
                    page.wait_for_selector("li.scaffold-layout__list-item", timeout=15000)
                    listings = page.query_selector_all("li.scaffold-layout__list-item")

                    print(f"🟢 Found {len(listings)} listings for {keyword} in {loc}")

                    for job in listings[:max_jobs]:
                        try:
                            title_el = job.query_selector("a.job-card-container__link strong")
                            company_el = job.query_selector("div.artdeco-entity-lockup__subtitle span")
                            location_el = job.query_selector("ul.job-card-container__metadata-wrapper li span")
                            link_el = job.query_selector("a.job-card-container__link")

                            jobs.append({
                                "title": title_el.inner_text().strip() if title_el else "",
                                "company": company_el.inner_text().strip() if company_el else "",
                                "location": location_el.inner_text().strip() if location_el else location,
                                "link": "https://www.linkedin.com" + link_el.get_attribute("href") if link_el else "",
                                "source": "LinkedIn",
                                "date": datetime.now().strftime("%Y-%m-%d")
                            })
                        except Exception as e:
                            print(f"⚠️ Error parsing job card: {e}")
                except Exception as e:
                    print(f"❌ Failed to load job search for {keyword} in {loc}: {e}")
        browser.close()
    return jobs

def save_jobs(jobs, filename="data/jobs.csv"):
    df = pd.DataFrame(jobs)
    df.to_csv(filename, index=False)
    print(f"✅ Saved {len(jobs)} jobs to {filename}")

if __name__ == "__main__":
    keywords = ["Sitecore Developer", ".NET Developer", "Full Stack Developer"]
    locations = ["Australia", "Singapore", "Japan"]

    jobs = scrape_linkedin_jobs(keywords, locations, max_jobs=10)
    save_jobs(jobs)
