import time
from playwright.sync_api import sync_playwright

user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"

with sync_playwright() as p:
    print("Abrindo navegador de automação...")
    context = p.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        args=['--remote-debugging-port=9222']
    )
    page = context.pages[0] if context.pages else context.new_page()
    print("Navegando para o login do AVA...")
    page.goto("https://avauni.grupoa.education/plataforma/auth/signin", wait_until="domcontentloaded")
    print("Navegador aberto e pronto na página de login do AVA!")
    
    # Manter aberto para interação
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
