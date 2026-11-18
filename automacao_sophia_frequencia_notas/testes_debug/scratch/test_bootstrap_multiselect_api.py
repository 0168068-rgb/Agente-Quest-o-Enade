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
    
    # Inspect all select elements and options
    select_info = page.evaluate("""() => {
        const result = [];
        const selects = Array.from(document.querySelectorAll('select'));
        selects.forEach((s, idx) => {
            const options = Array.from(s.options).map(o => ({
                value: o.value,
                text: o.text,
                selected: o.selected
            }));
            result.push({
                index: idx,
                id: s.id,
                name: s.name,
                class: s.className,
                optionsCount: options.length,
                options: options
            });
        });
        return result;
    }""")
    
    print("\n=== ALL SELECT ELEMENTS ===")
    for s in select_info:
        print(f"Select #{s['index']}: id='{s['id']}', name='{s['name']}', class='{s['class']}'")
        for opt in s['options']:
            print(f"   Option value='{opt['value']}', text='{opt['text']}', selected={opt['selected']}")
            
    # Test jQuery multiselect refresh API
    test_res = page.evaluate("""() => {
        if (window.jQuery) {
            const $ = window.jQuery;
            const $selects = $('select');
            let matchedSelectIndex = -1;
            let eadValue = null;
            
            $selects.each(function(idx) {
                const $s = $(this);
                $s.find('option').each(function() {
                    const txt = $(this).text().toLowerCase();
                    if (txt.includes('distância') || txt.includes('distancia')) {
                        matchedSelectIndex = idx;
                        eadValue = $(this).val();
                    }
                });
            });
            
            if (matchedSelectIndex !== -1) {
                const $targetSelect = $selects.eq(matchedSelectIndex);
                // Unselect all, select EAD, refresh multiselect, trigger change
                if (typeof $targetSelect.multiselect === 'function') {
                    $targetSelect.multiselect('deselectAll', false);
                    $targetSelect.multiselect('select', [eadValue]);
                    $targetSelect.multiselect('refresh');
                } else {
                    $targetSelect.val([eadValue]);
                }
                $targetSelect.trigger('change');
                return { matchedSelectIndex, eadValue, status: 'SUCCESS' };
            }
        }
        return { status: 'NO_JQUERY_OR_SELECT' };
    }""")
    
    print(f"\nJQUERY MULTISELECT TEST RESULT: {test_res}")
    time.sleep(4)
    
    # Check updated rows in table
    rows = page.locator("table tbody tr")
    print(f"Total rows in table after multiselect API update: {rows.count()}")
    for i in range(min(15, rows.count())):
        tds = rows.nth(i).locator("td")
        if tds.count() > 3:
            print(f" Row #{i+1}: '{tds.nth(3).inner_text().strip()}'")
            
    time.sleep(5)
    context.close()
