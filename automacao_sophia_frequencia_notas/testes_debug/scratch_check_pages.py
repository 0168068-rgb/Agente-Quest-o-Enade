import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "/home/hamilcar/Antigravity/playwright_user_data"

with sync_playwright() as p:
    try:
        context = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=True)
        print("Pages count:", len(context.pages))
        for idx, page in enumerate(context.pages):
            print(f"Page {idx} URL:", page.url)
            print(f"Page {idx} Title:", page.title())
        context.close()
    except Exception as e:
        print("Error:", e)
