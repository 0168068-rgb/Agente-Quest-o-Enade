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
    
    # Execute modality update
    page.evaluate("""() => {
        if (window.jQuery) {
            const $ = window.jQuery;
            let $targetSelect = null;
            let eadVal = null;
            $('select').each(function() {
                const $s = $(this);
                $s.find('option').each(function() {
                    const txt = $(this).text().toLowerCase();
                    if (txt.includes('distância') || txt.includes('distancia')) {
                        $targetSelect = $s;
                        eadVal = $(this).val();
                    }
                });
            });
            if ($targetSelect && eadVal) {
                if (typeof $targetSelect.multiselect === 'function') {
                    $targetSelect.multiselect('deselectAll', false);
                    $targetSelect.multiselect('select', [eadVal]);
                    $targetSelect.multiselect('refresh');
                } else {
                    $targetSelect.val([eadVal]);
                }
                $targetSelect.trigger('change');
            }
        }
    }""")
    
    time.sleep(3)
    
    # Set 100 per page
    try:
        length_select = page.locator("select[name*='length'], select[name*='Table']").first
        if length_select.is_visible():
            length_select.select_option("100")
            time.sleep(3)
    except Exception:
        pass

    # Inspect all filter buttons on page
    buttons_info = page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button.multiselect, .filter-container button, div.btn-group button')).map(b => b.innerText.strip ? b.innerText.strip() : b.innerText);
        const rows = Array.from(document.querySelectorAll('table tbody tr')).map(r => r.innerText.strip ? r.innerText.strip() : r.innerText);
        const selects = Array.from(document.querySelectorAll('select')).map(s => {
            const selectedOpts = Array.from(s.selectedOptions).map(o => o.text);
            return { id: s.id, name: s.name, selected: selectedOpts };
        });
        return { btns, rows, selects };
    }""")
    
    print("\n=== CURRENT FILTER BUTTON TEXTS ===")
    for idx, b in enumerate(buttons_info['btns']):
        print(f" Filter Box #{idx + 1}: '{b}'")
        
    print("\n=== CURRENT SELECTS ===")
    for s in buttons_info['selects']:
        print(f" Select id='{s['id']}', name='{s['name']}': selected={s['selected']}")

    print(f"\n=== CURRENT TABLE ROWS ({len(buttons_info['rows'])}) ===")
    for idx, r in enumerate(buttons_info['rows']):
        lines = [l.strip() for l in r.split('\n') if l.strip()]
        disc_text = lines[3] if len(lines) > 3 else r[:100]
        print(f" Row #{idx + 1}: '{disc_text}'")

    time.sleep(5)
    context.close()
