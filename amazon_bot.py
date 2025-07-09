import time
import asyncio
from playwright.sync_api import sync_playwright
from telegram import Bot
import threading

bot = Bot(token="8055111234:AAFLqqfuxOcauYKAXXLlQFQQeNRVL81JubM")
user_ids = ["1029190869", "1826294300"]
target_location = ""
retry_interval = 1  # seconds
max_retries = -1     # optional: retry up to 20 times (200 seconds total)


async def _send_messages(job_data, bot, user_ids):
    message = f"""————————————————
📍 {job_data['location']}
🦺 {job_data['title']}
🗓 {job_data['schedule_type']} | {job_data['employment_type']}
🕒 Schedule Count: {job_data['schedule_count']}
reminder to complete the application - darshan solanki
————————————————"""

    print("📱 Sending Telegram notifications...")

    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=message)
            print(f"✅ Message sent to {user_id}")
        except Exception as e:
            print(f"❌ Failed to send message to {user_id}: {e}")


def send_telegram_message(job_data):
    def thread_target():
        # ✅ Clean new loop
        asyncio.run(_send_messages(job_data, bot, user_ids))
    thread = threading.Thread(target=thread_target)
    thread.start()
    thread.join()


def extract_job_details(page, card, shift_cards):
    """Extract comprehensive job details from the page"""
    job_data = {
        'location': 'N/A',
        'title': 'N/A',
        'schedule_type': 'N/A',
        'employment_type': 'N/A',
        'schedule_count': len(shift_cards),
        'pay_rate': 'N/A',
        'start_date': 'N/A'
    }

    try:
        # Extract location
        location_element = card.query_selector_all(
            'div.hvh-careers-emotion-1lcyul5')
        if location_element and location_element[-1].query_selector("strong"):
            job_data['location'] = location_element[-1].query_selector(
                "strong").inner_text().strip()

        # Extract job title from multiple possible selectors
        title_selectors = [
            'h3[data-test-id="jobTitle"]',
            'h2[data-test-id="jobTitle"]',
            '.job-title',
            'h3',
            'h2',
            '[data-test-id*="title"]'
        ]

        for selector in title_selectors:
            try:
                title_element = card.query_selector(selector)
                if title_element:
                    job_data['title'] = title_element.inner_text().strip()
                    break
            except:
                continue

        # Extract employment type and schedule type from job details page
        try:
            # Look for employment type indicators
            employment_indicators = page.query_selector_all('div, span, p')
            for element in employment_indicators:
                try:
                    text = element.inner_text().strip().lower()
                    if 'seasonal' in text:
                        job_data['employment_type'] = 'Seasonal'
                    elif 'permanent' in text:
                        job_data['employment_type'] = 'Permanent'
                    elif 'temporary' in text:
                        job_data['employment_type'] = 'Temporary'
                    elif 'full time' in text or 'full-time' in text:
                        job_data['schedule_type'] = 'Full Time'
                    elif 'part time' in text or 'part-time' in text:
                        job_data['schedule_type'] = 'Part Time'
                except:
                    continue
        except:
            pass

        # Extract pay rate and start date from the selected shift
        try:
            # Find the selected/clicked shift card
            for shift_card in shift_cards:
                try:
                    # Check if this shift card is selected/active
                    if shift_card.get_attribute('class') and ('selected' in shift_card.get_attribute('class') or 'active' in shift_card.get_attribute('class')):
                        shift_info = extract_shift_data(shift_card)
                        if shift_info['Pay Rate'] != 'N/A':
                            job_data['pay_rate'] = shift_info['Pay Rate']
                        if shift_info['Start Date'] != 'N/A':
                            job_data['start_date'] = shift_info['Start Date']
                        break
                except:
                    continue

            # If no selected shift found, use the first shift with data
            if job_data['pay_rate'] == 'N/A' and shift_cards:
                shift_info = extract_shift_data(shift_cards[0])
                if shift_info['Pay Rate'] != 'N/A':
                    job_data['pay_rate'] = shift_info['Pay Rate']
                if shift_info['Start Date'] != 'N/A':
                    job_data['start_date'] = shift_info['Start Date']
        except:
            pass

        # Set defaults if still N/A
        if job_data['title'] == 'N/A':
            job_data['title'] = 'Fulfillment Centre Warehouse Associate'
        if job_data['employment_type'] == 'N/A':
            job_data['employment_type'] = 'Seasonal'
        if job_data['schedule_type'] == 'N/A':
            job_data['schedule_type'] = 'Full Time'
        if job_data['pay_rate'] == 'N/A':
            job_data['pay_rate'] = 'Rate TBD'
        if job_data['start_date'] == 'N/A':
            job_data['start_date'] = 'TBD'

    except Exception as e:
        print(f"⚠️ Error extracting job details: {e}")

    return job_data


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


def click_on_next_button(new_page, job_data):
    try:
        print("🔄 Waiting for page to load...")
        # Quick load check - don't wait for networkidle
        new_page.wait_for_load_state('domcontentloaded', timeout=5000)
        time.sleep(1)  # Give more time for dynamic content to load

        # Wait for Next button with faster approach
        next_button = None
        selectors_to_try = [
            "button:has-text('Next')",
            "button[type='submit']:has-text('Next')",
            "input[type='submit'][value='Next']",
            "button:text-is('Next')",
            "[data-test-id*='next'], [data-testid*='next']",
            "button[class*='next']",
            "input[type='button'][value='Next']"
        ]

        # Try multiple times to find the button
        for attempt in range(3):
            for selector in selectors_to_try:
                try:
                    new_page.wait_for_selector(selector, timeout=1400)
                    next_button = new_page.query_selector(selector)
                    if next_button and next_button.is_visible() and next_button.is_enabled():
                        print(f"✅ Found Next button with selector: {selector}")
                        break
                except:
                    continue
            if next_button:
                break
            # time.sleep(1)

        if next_button:
            print("✅ Attempting to click 'Next' button...")

            # Multiple click strategies to ensure it works
            try:
                # Strategy 1: Normal click
                next_button.scroll_into_view_if_needed()
                # time.sleep(1)
                next_button.click()
                print("✅ Next button clicked with normal click")

                # Wait and verify the click worked by checking if page changed
                # time.sleep(2)

                # Check if we're still on the same page or if something changed
                try:
                    # If Next button is still there, click didn't work
                    still_there = new_page.query_selector(selectors_to_try[0])
                    if still_there and still_there.is_visible():
                        print("⚠️ Next button still visible, trying force click...")
                        next_button.click(force=True)
                        time.sleep(2)
                except:
                    pass

            except Exception as click_error:
                print(f"⚠️ Normal click failed: {click_error}")
                try:
                    # Strategy 2: Force click
                    print("🔄 Trying force click...")
                    next_button.click(force=True)
                    time.sleep(2)
                except Exception as force_error:
                    print(f"⚠️ Force click failed: {force_error}")
                    try:
                        # Strategy 3: JavaScript click
                        print("🔄 Trying JavaScript click...")
                        new_page.evaluate(
                            "(element) => element.click()", next_button)
                        time.sleep(2)
                    except Exception as js_error:
                        print(f"⚠️ JavaScript click failed: {js_error}")
                        return False

            print("✅ Next button click attempt completed")
        else:
            print("❌ 'Next' button not found with any selector.")
            # Show available buttons for debugging
            print("🔍 Available buttons on page:")
            buttons = new_page.query_selector_all(
                "button, input[type='submit'], input[type='button']")
            for btn in buttons[:10]:
                try:
                    text = btn.inner_text().strip() or btn.get_attribute(
                        'value') or btn.get_attribute('aria-label')
                    if text:
                        print(f"  - {text}")
                except:
                    continue
            return False

    except Exception as e:
        print(f"⚠️ Error clicking 'Next': {e}")
        return False

    try:
        print("🔄 Looking for 'Create Application' button...")
        # Give more time after Next button click
        time.sleep(3)

        # Try multiple selectors for Create Application button with shorter timeouts
        create_button = None
        create_selectors = [
            "button:has-text('Create Application')",
            "button:text-is('Create Application')",
            "input[type='submit'][value*='Create']",
            "button[type='submit']:has-text('Create')",
            "[data-test-id*='create'], [data-testid*='create']",
            "button:has-text('Apply')",  # Sometimes it's just "Apply"
            "button:text-is('Apply')",
            "button:has-text('Submit')",
            "input[type='submit'][value*='Submit']"
        ]

        # Quick polling approach - check every 500ms instead of long waits
        max_attempts = 15  # 7.5 seconds total
        attempt = 0

        while attempt < max_attempts:
            for selector in create_selectors:
                try:
                    create_button = new_page.query_selector(selector)
                    if create_button and create_button.is_visible() and create_button.is_enabled():
                        print(
                            f"✅ Found Create Application button with selector: {selector}")
                        break
                except:
                    continue

            if create_button:
                break

            if attempt % 3 == 0:  # Print every 1.5 seconds
                print(
                    f"🔄 Attempt {attempt + 1}/15 - Checking for Create Application button...")
            time.sleep(0.5)
            attempt += 1

        if create_button:
            print("✅ Attempting to click 'Create Application' button...")

            # Multiple click strategies
            try:
                create_button.scroll_into_view_if_needed()
                time.sleep(1)
                create_button.click()
                print("✅ Create Application button clicked with normal click")
                time.sleep(3)  # Wait longer to see if it processes

                # Send Telegram message after successful click
                print("📱 Sending Telegram notification...")
                send_telegram_message(job_data)
                # asyncio.run()

                return True

            except Exception as click_error:
                print(f"⚠️ Normal click failed: {click_error}")
                try:
                    # Force click
                    create_button.click(force=True)
                    print("✅ Create Application button clicked with force click")
                    send_telegram_message(job_data)

                    return True
                except Exception as force_error:
                    print(f"⚠️ Force click failed: {force_error}")
                    try:
                        # JavaScript click
                        new_page.evaluate(
                            "(element) => element.click()", create_button)
                        print("✅ Create Application button clicked with JavaScript")
                        send_telegram_message(job_data)
                        return True

                    except Exception as js_error:
                        print(f"⚠️ All click methods failed: {js_error}")
                        return False
        else:
            print("❌ 'Create Application' button not found after polling.")
            # Print page content for debugging
            print("🔍 Current page buttons:")
            buttons = new_page.query_selector_all(
                "button, input[type='submit'], input[type='button']")
            for btn in buttons[:10]:  # Show first 10 buttons
                try:
                    text = btn.inner_text().strip() or btn.get_attribute(
                        'value') or btn.get_attribute('aria-label')
                    if text:
                        print(f"  - {text}")
                except:
                    continue
            return False

    except Exception as e:
        print(f"⚠️ Error clicking 'Create Application': {e}")
        return False

    return True


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled",
              "--disable-web-security"]
    )

    # Create context with additional settings
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    )

    page = context.new_page()

    # Set additional properties to avoid detection
    page.evaluate("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
    """)

    page.goto("https://hiring.amazon.com/app#/jobSearch")
    input("⏳ Please complete login manually, then press Enter to continue...")

    attempt = 0
    while attempt < max_retries or max_retries == -1:
        page.reload()
        try:
            page.wait_for_selector(
                'div.hvh-careers-emotion-1lp5dlv', timeout=8000)
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

                print(f"🔍 Checking job in {location_text}...")

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

                    # Extract comprehensive job details
                    job_data = extract_job_details(page, card, shift_cards)
                    print(f"📋 Extracted job data: {job_data}")

                    for i, shift_card in enumerate(shift_cards, 1):
                        shift_info = extract_shift_data(shift_card)
                        if all(value != "N/A" for value in shift_info.values()):
                            print(
                                f"✅ Clicking on Shift {i} with complete data:")
                            for k, v in shift_info.items():
                                print(f"{k}: {v}")
                            shift_card.click()
                            break

                    # Wait until Apply button is fully visible and enabled
                    try:
                        print("🔄 Waiting for Apply button...")
                        page.wait_for_selector(
                            '[data-test-id="jobDetailApplyButtonDesktop"]:not([disabled])', timeout=7000)
                        apply_button = page.query_selector(
                            '[data-test-id="jobDetailApplyButtonDesktop"]')

                        if apply_button and apply_button.is_visible() and apply_button.is_enabled():
                            print("✅ Apply button found and clickable")

                            # Scroll to the apply button
                            apply_button.scroll_into_view_if_needed()
                            time.sleep(2)  # Give time for any animations

                            # Set up page listener before clicking
                            with context.expect_page() as new_page_info:
                                print("🔄 Clicking Apply button...")
                                apply_button.click(force=True)

                            new_page = new_page_info.value
                            print("✅ New page opened for application")

                            # Wait for the new page to load
                            new_page.wait_for_load_state('domcontentloaded')

                            # Call the button click function and store result
                            print("🔄 Processing application form...")
                            success = click_on_next_button(new_page, job_data)
                            print(f"✅ Button clicking result: {success}")

                            if success:
                                print(
                                    "✅ Application process completed successfully!")
                                print("🔄 Keeping new page open for verification...")
                                input(
                                    "✅ Check the application status, then press Enter to close browser...")
                                browser.close()
                                exit(0)
                            else:
                                print(
                                    "❌ Failed on 'Next' or 'Create Application', retrying...")
                                print("🔄 Closing failed application page...")
                                try:
                                    new_page.close()  # Close the failed page
                                except:
                                    pass
                                time.sleep(2)  # Brief pause before retry
                                continue
                        else:
                            print(
                                "❌ Apply button not found, not visible, or not clickable.")
                            continue

                    except Exception as e:
                        print(f"⚠️ Error with Apply button: {e}")
                        continue

            if not found:
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
    browser.close()
