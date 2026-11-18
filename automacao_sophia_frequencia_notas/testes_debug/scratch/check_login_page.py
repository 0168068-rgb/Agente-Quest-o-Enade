import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "/home/hamilcar/Antigravity/playwright_user_data"
TARGET_URL = "https://avalia.grupoa.com.br/Professor"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        USER_DATA_DIR,
        headless=False,
        args=['--no-sandbox', '--disable-setuid-sandbox', '--start-maximized']
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(TARGET_URL, wait_until="domcontentloaded")
    time.sleep(3)
    
    print("Current URL:", page.url)
    if "Login" in page.url:
        print("On login page!")
        user_val = page.locator("#Usuario, input[name*='Usuario'], input[name*='user']").first.input_value() if page.locator("#Usuario, input[name*='Usuario'], input[name*='user']").count() > 0 else "N/A"
        pass_val = page.locator("#Senha, input[name*='Senha'], input[type='password']").first.input_value() if page.locator("#Senha, input[name*='Senha'], input[type='password']").count() > 0 else "N/A"
        print(f"User field value: '{user_val}', Pass field value: '{pass_val}'")
        
        btn = page.locator("button[type='submit'], input[type='submit'], .btn-primary, button:has-text('Entrar')").first
        if btn.count() > 0:
            print(f"Submit button found: text='{btn.inner_text()}'")
            if user_val and pass_val:
                print("Fields are pre-filled! Clicking submit button...")
                btn.click()
                time.sleep(5)
                print("After click URL:", page.url)
    context.close()
