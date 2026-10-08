import os
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"
    meet_url = "https://meet.google.com/bno-piai-vuq"
    
    print("Iniciando Chromium...")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=[
                '--use-fake-ui-for-media-stream',
                '--use-fake-device-for-media-stream',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--remote-debugging-port=9222'
            ],
            permissions=['microphone', 'camera']
        )
        page = context.new_page()
        print(f"Navegando para: {meet_url}")
        page.goto(meet_url)
        page.wait_for_load_state("networkidle")
        time.sleep(5)
        
        # Mute
        try:
            page.keyboard.press("Control+d")
            page.keyboard.press("Control+e")
            print("Ctrl+D and Ctrl+E pressed.")
        except Exception as e:
            print(f"Mute error: {e}")
            
        time.sleep(2)
        page.screenshot(path="inspect_landing.png")
        print("Screenshot salvo em 'inspect_landing.png'.")
        
        # Check for tooltips and dismiss them
        buttons = page.locator("button, div[role='button']").all()
        print(f"Encontrados {len(buttons)} botões no total.")
        
        for btn in buttons:
            try:
                text = btn.inner_text().strip().replace('\n', ' ')
                visible = btn.is_visible()
                print(f"Botão: '{text}' | Visível: {visible}")
                
                # If tooltip button "Entendi" is visible, click it
                if visible and "entendi" in text.lower():
                    print(f"Clicando para dispensar tooltip: '{text}'")
                    btn.click()
                    time.sleep(2)
            except Exception as e:
                continue
                
        # Take screenshot after dismissing tooltips
        page.screenshot(path="inspect_after_dismiss.png")
        print("Screenshot após fechar tooltips salvo em 'inspect_after_dismiss.png'.")
        
        # Print buttons again
        buttons = page.locator("button, div[role='button']").all()
        print("\n--- Botões após dispensar tooltips ---")
        for btn in buttons:
            try:
                text = btn.inner_text().strip().replace('\n', ' ')
                visible = btn.is_visible()
                print(f"Botão: '{text}' | Visível: {visible}")
            except:
                continue
                
        context.close()

if __name__ == "__main__":
    main()
