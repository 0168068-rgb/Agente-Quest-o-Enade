import os
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"
    print("Iniciando o Chromium para verificar sessão...")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--remote-debugging-port=9222'
            ]
        )
        page = context.new_page()
        print("Navegando para https://myaccount.google.com/ ...")
        page.goto("https://myaccount.google.com/")
        time.sleep(5)
        page.screenshot(path="session_info.png")
        print("Screenshot salvo em 'session_info.png'.")
        print(f"URL atual: {page.url}")
        print(f"Título da página: {page.title()}")
        context.close()

if __name__ == "__main__":
    main()
