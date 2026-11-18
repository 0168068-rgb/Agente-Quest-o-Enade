import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "/home/hamilcar/Antigravity/playwright_user_data"
TARGET_URL = "https://avalia.grupoa.com.br/Professor"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=True)
    page = context.pages[0] if context.pages else context.new_page()
    
    print("Navigating to Professor page...")
    page.goto(TARGET_URL, wait_until="networkidle")
    time.sleep(2)
    
    # Click 12th column link of first row in table 2
    rows = page.locator("table").nth(1).locator("tbody tr")
    print("Rows count in Table 2:", rows.count())
    
    if rows.count() > 0:
        first_row = rows.first
        tds = first_row.locator("td")
        print("Tds count in first row:", tds.count())
        
        # td index 12 is Questões pré-validadas
        pre_val_td = tds.nth(12)
        print("Pre val td text:", pre_val_td.inner_text())
        
        link = pre_val_td.locator("a").first
        if link.count() > 0:
            print("Clicking link in Questões pré-validadas...")
            link.click()
            page.wait_for_timeout(3000)
            
            # Screenshot of opened modal
            page.screenshot(path="/home/hamilcar/Antigravity/scratch_modal_opened.png")
            with open("/home/hamilcar/Antigravity/scratch_modal_opened.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Saved modal screenshot to scratch_modal_opened.png and HTML to scratch_modal_opened.html")
    context.close()
