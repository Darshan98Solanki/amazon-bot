import time
from playwright.sync_api import sync_playwright

target_location = "Granville, NY"
retry_interval = 0.5  # seconds
max_retries = 20     # optional: retry up to 20 times (200 seconds total)


def extract_shift_data(card):
    def get_text(selector):
        el = card.query_selector(selector)
        return el.inner_text().strip() if el else "N/A"
    shift = get_text("div:has-text('Shift:') + div")
    duration = get_text("div:has-text('Duration:') + div")
    start_date = get_text("div:has-text('Start date:') + div")
    language = get_text("div:has-text('Language Supported:') + div")
    bonus = get_text("div.scheduleBannerText")
    pay_rate = get_text("div[data-test-id='scheduleCardPayRate']")
    per_hour = get_text("div[data-test-id='scheduleCardPayRate'] + div")

    return {
        "Shift": shift,
        "Duration": duration,
        "Start Date": start_date,
        "Language": language,
        "Bonus": bonus,
        "Pay Rate": f"{pay_rate} {per_hour}"
    }


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False, args=["--disable-blink-features=AutomationControlled"])
    page = browser.new_page()
    page.evaluate(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    page.goto("https://hiring.amazon.com/app#/jobSearch")
    input("⏳ Please complete login manually, then press Enter to continue...")

    attempt = 0
    while attempt < max_retries or max_retries == -1:
        page.reload()
        try:
            page.wait_for_selector(
                'div.hvh-careers-emotion-1lp5dlv', timeout=5000)
            job_cards = page.query_selector_all(
                'div.hvh-careers-emotion-1lp5dlv')
            found = False

            for card in job_cards:
                location_element = card.query_selector_all(
                    'div.hvh-careers-emotion-1lcyul5')
                location_text = (
                    location_element[-1].query_selector(
                        "strong").inner_text().strip()
                    if location_element and location_element[-1].query_selector("strong")
                    else "N/A"
                )

                if not target_location or location_text == target_location:
                    print(
                        f"✅ Found matching job in {location_text}, clicking...")
                    card.click()
                    page.wait_for_selector('div.jobDetailScheduleDropdown')
                    dropdown = page.query_selector(
                        'div.jobDetailScheduleDropdown')
                    dropdown.click()

                    page.wait_for_selector(
                        "div[data-test-component='StencilReactCard']")
                    shift_cards = page.query_selector_all(
                        "div[data-test-component='StencilReactCard']")
                    print(f"\n🔎 Found {len(shift_cards)} shift(s):\n")

                    for i, card in enumerate(shift_cards, 1):
                        shift_info = extract_shift_data(card)
                        if all(value != "N/A" for value in shift_info.values()):
                            print(
                                f"✅ Clicking on Shift {i} with complete data:")
                            for k, v in shift_info.items():
                                print(f"{k}: {v}")
                            card.click()
                            break

                    page.wait_for_selector(
                        '[data-test-id="jobDetailApplyButtonDesktop"]')
                    page.click('[data-test-id="jobDetailApplyButtonDesktop"]')
                    input("Press Enter to close browser...")
                    found = True
                    break

            if found:
                break
            else:
                print(
                    f"🔁 No matching job found. Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
                attempt += 1
        except Exception as e:
            print(f"⚠️ Error during attempt {attempt+1}: {e}")
            time.sleep(retry_interval)
            attempt += 1

    print("❌ Job not found after retries." if attempt >=
          max_retries else "✅ Job processed.")
