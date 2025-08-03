from playwright.sync_api import sync_playwright

def save_linkedin_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://www.linkedin.com/login", timeout=60000)
        print("⚠️ Please log in manually. Once done, close the browser window.")
        page.wait_for_timeout(30000)  # Allow time for login

        context.storage_state(path="utils/linkedin_auth.json")
        browser.close()
        print("✅ Session saved to utils/linkedin_auth.json")

if __name__ == "__main__":
    save_linkedin_session()
