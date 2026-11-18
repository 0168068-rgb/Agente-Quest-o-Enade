import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "/home/hamilcar/Antigravity/playwright_user_data"
TARGET_URL = "https://avalia.grupoa.com.br/Professor"

def get_logged_in_page(context):
    for p in reversed(context.pages):
        try:
            url = p.url
            if "Login" not in url and "avalia.grupoa.com.br" in url:
                return p
        except Exception:
            pass
    return None

def wait_for_login(context):
    print("\nVerificando login...")
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(TARGET_URL, wait_until="domcontentloaded")
    time.sleep(2)
    
    check_count = 0
    while True:
        logged_page = get_logged_in_page(context)
        if logged_page:
            print(f"✓ Sessão autenticada: {logged_page.url}")
            return logged_page
        check_count += 1
        print(f"[{check_count}] Aguardando login...")
        time.sleep(3)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        USER_DATA_DIR,
        headless=False,
        args=['--no-sandbox', '--disable-setuid-sandbox', '--start-maximized']
    )
    page = wait_for_login(context)
    if TARGET_URL not in page.url:
        page.goto(TARGET_URL, wait_until="domcontentloaded")
        
    time.sleep(4)
    
    # Dump full HTML of the filter section
    html_dump = page.evaluate("""() => {
        const filtersDiv = document.querySelector('div:has-text("Filtros:"), .filter-container, #filtros') || document.body;
        
        // Find all buttons, inputs, selects, multiselects
        const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
            text: b.innerText.trim(),
            title: b.getAttribute('title'),
            class: b.className,
            outerHTML: b.outerHTML
        }));
        
        const multiselects = Array.from(document.querySelectorAll('.btn-group, .dropdown, .multiselect-native-select')).map(g => ({
            html: g.outerHTML
        }));
        
        return { buttons, multiselects };
    }""")
    
    print("\n=== BUTTONS FOUND ===")
    for b in html_dump['buttons']:
        print(f"Button: text='{b['text']}', title='{b['title']}', class='{b['class']}'")
        print(f"  HTML: {b['outerHTML'][:200]}\n")
        
    print("\n=== MULTISELECT GROUPS ===")
    for m in html_dump['multiselects']:
        print(f"Group HTML:\n{m['html']}\n")
        
    time.sleep(5)
    context.close()
