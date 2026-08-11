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
            ("0003-scope-risikobehandlung-und-soa.html", "#grade", "/5 richtig"),
            ("0004-kontext-fuehrung-und-dokumentation.html", "#grade", "/5 richtig"),
        ]:
            page = context.new_page()
            errors=[]
            page.on("console", lambda msg: errors.append(f"console:{msg.type}:{msg.text}") if msg.type == "error" else None)
            page.on("pageerror", lambda exc: errors.append(f"pageerror:{exc}"))
            response=page.goto(BASE+filename, wait_until="networkidle")
            if filename.startswith(("0002", "0003", "0004")):
                assert page.locator(".q").count() == 5
                assert all(not page.locator(".explain").nth(i).is_visible() for i in range(5)), "Erklärungen müssen vor der Auswertung verborgen sein"
                page.locator(".q").nth(0).locator("input[value=a]").check()
                page.locator(".q").nth(0).locator("input[value=c]").check()
            page.locator(button).click()
            text=page.locator("#result").inner_text()
            visible=page.locator("#result").is_visible()
            print(f"mobile={mobile} page={filename} http={response.status} visible={visible} result={text!r} errors={errors}")
            assert visible and expected in text and not errors
            if filename.startswith(("0002", "0003", "0004")):
                assert text.startswith("1/5"), text
                assert all(page.locator(".explain").nth(i).is_visible() for i in range(5)), "Erklärungen müssen nach der Auswertung sichtbar sein"
                assert page.locator(".q.ok").count() == 1
                assert page.locator(".q.bad").count() == 4
                assert page.locator(".correct-answer").count() > 0, "Richtige Optionen müssen markiert sein"
                assert page.locator(".q.bad").first.evaluate("e => getComputedStyle(e).backgroundColor") != "rgba(0, 0, 0, 0)", "Falsche Aufgaben brauchen eine sichtbare Markierung"
                for i in range(5):
                    question = page.locator(".q").nth(i)
                    question.locator("input").evaluate_all("els => els.forEach(el => { el.checked = false; })")
                    for value in question.get_attribute("data-correct").split(","):
                        question.locator(f"input[value={value}]").check()
                page.locator(button).click()
                assert page.locator("#result").inner_text().startswith("5/5"), "Vollständig richtige Auswahl muss 5/5 ergeben"
                assert page.locator(".q.ok").count() == 5
                assert page.locator(".q.bad").count() == 0
            page.close()
        context.close()
    browser.close()
