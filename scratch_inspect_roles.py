import time
import json
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "/home/hamilcar/Antigravity/playwright_user_data"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=True)
    page = context.pages[0] if context.pages else context.new_page()
    
    for url in ["https://avalia.grupoa.com.br/CoordenadorCurso", "https://avalia.grupoa.com.br/Professor"]:
        print(f"\n==================================================")
        print(f"Inspecionando {url}...")
        page.goto(url, wait_until="networkidle")
        time.sleep(4)
        
        print("URL final:", page.url)
        print("Título:", page.title())
        
        filename_prefix = url.split("/")[-1]
        page.screenshot(path=f"/home/hamilcar/Antigravity/scratch_{filename_prefix}.png")
        with open(f"/home/hamilcar/Antigravity/scratch_{filename_prefix}.html", "w", encoding="utf-8") as f:
            f.write(page.content())
            
        # Inspecionar tabelas
        info = page.evaluate("""() => {
            const tables = Array.from(document.querySelectorAll('table')).map((t, idx) => {
                const headers = Array.from(t.querySelectorAll('th')).map(th => th.innerText.trim());
                const rowCount = t.querySelectorAll('tbody tr').length;
                const sampleRows = Array.from(t.querySelectorAll('tbody tr')).slice(0, 3).map(r => {
                    return Array.from(r.querySelectorAll('td')).map(td => td.innerText.trim());
                });
                return { tableIndex: idx, headers, rowCount, sampleRows };
            });
            return { tables };
        }""")
        print(f"Tabelas em {filename_prefix}:", json.dumps(info, indent=2, ensure_ascii=False))

    context.close()
