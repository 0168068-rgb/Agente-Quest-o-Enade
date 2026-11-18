import os
import sys
import json
from playwright.sync_api import sync_playwright

def get_active_page(context):
    for p in reversed(context.pages):
        try:
            if "avalia" in p.url or "Elaborador" in p.url:
                return p
        except:
            pass
    if context.pages:
        return context.pages[-1]
    return None

def main():
    user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(user_data_dir, headless=False)
        page = get_active_page(context)
        if not page:
            print("No active page found.")
            return
            
        print(f"Initial Page URL: {page.url}")
        
        # Navigate to the dashboard if not already there
        if "Elaborador" not in page.url:
            print("Navigating to dashboard...")
            page.goto("https://avalia.grupoa.com.br/Elaborador")
            page.wait_for_timeout(3000)
            
        # Click "Elaborar Novas Questões" to open the editor
        print("Clicking 'Elaborar Novas Questões'...")
        page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, a'));
            const btn = btns.find(b => b.innerText.includes('Elabora Novas Questões') || b.innerText.includes('Elaborar'));
            if (btn) btn.click();
        }""")
        
        # Wait for the editor to open
        page.wait_for_timeout(4000)
        
        # Capture hierarchy when open
        res_open = page.evaluate("""() => {
            const el = document.getElementById('Questao_Nome');
            if (!el) return { error: "no #Questao_Nome element found when open" };
            
            const hierarchy = [];
            let current = el;
            while (current) {
                const style = window.getComputedStyle(current);
                hierarchy.push({
                    tagName: current.tagName,
                    id: current.id,
                    className: current.className,
                    display: style.display,
                    visibility: style.visibility,
                    opacity: style.opacity,
                    position: style.position,
                    zIndex: style.zIndex,
                    top: style.top,
                    rect: current.getBoundingClientRect()
                });
                current = current.parentElement;
            }
            return { hierarchy };
        }""")
        
        print("--- HIERARCHY WHEN OPEN ---")
        if "error" in res_open:
            print(res_open["error"])
        else:
            for item in res_open["hierarchy"][:8]:  # Print first 8 ancestors
                print(f"Tag: {item['tagName']}, ID: {item['id']}, Class: {item['className']}, Display: {item['display']}, Vis: {item['visibility']}, Opacity: {item['opacity']}, Position: {item['position']}, Rect: {item['rect']}")
                
        # Close the editor (click Fechar)
        print("Closing editor...")
        page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('.modal button, .modal a, button, a'));
            const close = btns.find(b => b.innerText.includes('Fechar') || b.className.includes('close'));
            if (close) close.click();
        }""")
        page.wait_for_timeout(3000)
        
        # Capture hierarchy when closed
        res_closed = page.evaluate("""() => {
            const el = document.getElementById('Questao_Nome');
            if (!el) return { error: "no #Questao_Nome element found when closed" };
            
            const hierarchy = [];
            let current = el;
            while (current) {
                const style = window.getComputedStyle(current);
                hierarchy.push({
                    tagName: current.tagName,
                    id: current.id,
                    className: current.className,
                    display: style.display,
                    visibility: style.visibility,
                    opacity: style.opacity,
                    position: style.position,
                    zIndex: style.zIndex,
                    top: style.top,
                    rect: current.getBoundingClientRect()
                });
                current = current.parentElement;
            }
            return { hierarchy };
        }""")
        
        print("--- HIERARCHY WHEN CLOSED ---")
        if "error" in res_closed:
            print(res_closed["error"])
        else:
            for item in res_closed["hierarchy"][:8]:
                print(f"Tag: {item['tagName']}, ID: {item['id']}, Class: {item['className']}, Display: {item['display']}, Vis: {item['visibility']}, Opacity: {item['opacity']}, Position: {item['position']}, Rect: {item['rect']}")
                
        context.close()

if __name__ == "__main__":
    main()
