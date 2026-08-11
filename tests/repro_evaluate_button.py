import os
from playwright.sync_api import sync_playwright

BASE = os.environ.get("TEST_BASE", "https://joku-create.github.io/iso-27001-lernportal/lessons/")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for mobile in (False, True):
        context = browser.new_context(
            viewport={"width": 390, "height": 844} if mobile else {"width": 1280, "height": 900},
            user_agent=("Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/151.0 Mobile Safari/537.36 Telegram-Android/12.0") if mobile else None,
        )
        for filename, button, expected in [
            ("0001-standortbestimmung.html", "button[type=submit]", "von 10 Punkten"),
            ("0002-normarchitektur-und-versionsfalle.html", "#grade", "/5 richtig"),
        ]:
            page = context.new_page()
            errors=[]
            page.on("console", lambda msg: errors.append(f"console:{msg.type}:{msg.text}") if msg.type == "error" else None)
            page.on("pageerror", lambda exc: errors.append(f"pageerror:{exc}"))
            response=page.goto(BASE+filename, wait_until="networkidle")
            page.locator(button).click()
            text=page.locator("#result").inner_text()
            visible=page.locator("#result").is_visible()
            print(f"mobile={mobile} page={filename} http={response.status} visible={visible} result={text!r} errors={errors}")
            assert visible and expected in text and not errors
            page.close()
        context.close()
    browser.close()
