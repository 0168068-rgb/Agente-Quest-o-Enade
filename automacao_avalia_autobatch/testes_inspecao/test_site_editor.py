import time
from playwright.sync_api import sync_playwright

def inspect_site():
    user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"
    site_url = "https://sites.google.com/d/1pe1Kb-8AMGowf4DsYqDoxXRc11aN69jw/edit"
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = context.new_page()
        print(f"Navegando para o Google Sites Editor: {site_url}")
        page.goto(site_url, wait_until="networkidle")
        time.sleep(5)
        
        page.screenshot(path="site_editor_test.png")
        print(f"Título da página: {page.title()}")
        print(f"URL final: {page.url}")
        
        # Check if login is required
        if "accounts.google.com" in page.url:
            print("Redirecionado para tela de login. Precisa de login.")
        else:
            print("Página do editor carregada com sucesso!")
            
            # Print iframes or embedded drive elements
            iframes = page.query_selector_all("iframe")
            print(f"Total de iframes na página: {len(iframes)}")
            for i, frame in enumerate(iframes):
                src = frame.get_attribute("src") or ""
                print(f"  Iframe {i}: src={src[:100]}")
                
        context.close()

if __name__ == '__main__':
    inspect_site()
