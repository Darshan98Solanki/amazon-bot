from playwright.sync_api import sync_playwright

target_location = "Granville, NY"


def extract_shift_data(card):
    def get_text(selector):
        el = card.query_selector(selector)
        return el.inner_text().strip() if el else "N/A"

    # Use specific class selectors or data-test attributes where applicable
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


def get_text_after_label(card, label):
    # Finds <strong> with label, then gets its next sibling text
    label_element = card.query_selector(f"text='{label}'")
    if label_element:
        parent = label_element.evaluate_handle("e => e.parentElement")
        return parent.evaluate("e => e.innerText.replace(`${e.querySelector('strong').innerText}`, '').trim()")
    return "N/A"


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    # Replace with actual job listing URL
    page.goto("https://hiring.amazon.com/app#/jobSearch")

    # Wait for the job cards to load
    page.wait_for_selector('div.hvh-careers-emotion-1lp5dlv')

    job_cards = page.query_selector_all('div.hvh-careers-emotion-1lp5dlv')

    for card in job_cards:
        # print("---- Job ----")

        # title = card.query_selector("div.jobDetailText strong")
        # title_text = title.inner_text().strip() if title else "N/A"

        # shifts = card.query_selector('div.hvh-careers-emotion-1lcyul5')
        # shifts_text = shifts.inner_text().strip() if shifts else "N/A"

        # job_type = get_text_after_label(card, "Type:")
        # duration = get_text_after_label(card, "Duration:")
        # pay = get_text_after_label(card, "Pay rate:")

        # Location is usually in a <strong> inside the same class as shifts
        location_element = card.query_selector_all(
            'div.hvh-careers-emotion-1lcyul5')
        location_text = (
            location_element[-1].query_selector("strong").inner_text().strip()
            if location_element and location_element[-1].query_selector("strong")
            else "N/A"
        )
        if location_text == target_location:
            print(f"Found matching job in {location_text}, clicking...")
            card.click()

            # Wait for the dropdown to appear
            page.wait_for_selector('div.jobDetailScheduleDropdown')

            # Click on the dropdown
            dropdown = page.query_selector('div.jobDetailScheduleDropdown')
            dropdown.click()

            print("Clicked the 'Select one' dropdown.")

            page.wait_for_selector(
                "div[data-test-component='StencilReactCard']")

            # checking for shifts
            shift_cards = page.query_selector_all(
                "div[data-test-component='StencilReactCard']")
            print(f"\n🔎 Found {len(shift_cards)} shift(s):\n")

            for i, card in enumerate(shift_cards, 1):
                shift_info = extract_shift_data(card)

                # Check if none of the extracted fields are "N/A"
                if all(value != "N/A" for value in shift_info.values()):
                    print(f"✅ Clicking on Shift {i} with complete data:")
                    for k, v in shift_info.items():
                        print(f"{k}: {v}")
                    card.click()
                    break
            
            # Click the Apply button
            page.wait_for_selector('[data-test-id="jobDetailApplyButtonDesktop"]')
            page.click('[data-test-id="jobDetailApplyButtonDesktop"]')

            # break
        input("Press Enter to close browser...")
        # print(f"Title: {title_text}")
        # print(f"Shifts: {shifts_text}")
        # print(f"Type: {job_type}")
        # print(f"Duration: {duration}")
        # print(f"Pay: {pay}")
        # print(f"Location: {location_text}")
        # print()

    # browser.close()
