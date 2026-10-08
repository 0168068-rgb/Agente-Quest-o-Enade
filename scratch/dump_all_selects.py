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
    
    dump = page.evaluate("""() => {
        const selects = Array.from(document.querySelectorAll('select')).map((s, i) => ({
            index: i,
            id: s.id,
            name: s.name,
            className: s.className,
            parentHTML: s.parentElement ? s.parentElement.outerHTML.substring(0, 300) : '',
            options: Array.from(s.options).map(o => ({
                value: o.value,
                text: o.text,
                selected: o.selected
            }))
        }));
        
        const filterButtons = Array.from(document.querySelectorAll('button')).map(b => ({
            text: b.innerText.trim(),
            title: b.getAttribute('title'),
            className: b.className,
            outerHTML: b.outerHTML.substring(0, 300)
        }));
        
        return { selects, filterButtons };
    }""")
    
    print("\n==================================================")
    print(" DUMP OF ALL SELECT ELEMENTS ON PROFESSOR PAGE")
    print("==================================================")
    for s in dump['selects']:
        print(f"\nSelect #{s['index']} -> id='{s['id']}', name='{s['name']}', class='{s['className']}':")
        print(f" Parent HTML snippet: {s['parentHTML'][:150]}...")
        print(f" Options count: {len(s['options'])}")
        for opt in s['options']:
            print(f"   Option val='{opt['value']}', text='{opt['text']}', selected={opt['selected']}")

    print("\n==================================================")
    print(" DUMP OF ALL BUTTONS ON PROFESSOR PAGE")
    print("==================================================")
    for b in dump['filterButtons']:
        print(f"Button: text='{b['text']}', title='{b['title']}', class='{b['className']}'")

    time.sleep(5)
    context.close()
