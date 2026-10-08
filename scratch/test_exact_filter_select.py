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
    
    res = page.evaluate("""() => {
        // Find filter selects ignoring DataTables length dropdown
        const filterSelects = Array.from(document.querySelectorAll('select')).filter(s => 
            !s.name.includes('length') && !s.id.includes('length') &&
            !s.name.includes('Table') && !s.id.includes('Table')
        );
        
        const details = filterSelects.map(s => ({
            id: s.id,
            name: s.name,
            options: Array.from(s.options).map(o => ({ value: o.value, text: o.text, selected: o.selected }))
        }));
        
        // Find modality select (the one with 'semipresencial' or 'distância')
        let modSelect = filterSelects.find(s => 
            Array.from(s.options).some(o => o.text.toLowerCase().includes('semipresencial') || o.text.toLowerCase().includes('distância'))
        );
        
        if (modSelect) {
            const eadOpt = Array.from(modSelect.options).find(o => 
                o.text.toLowerCase().includes('distância') || o.text.toLowerCase().includes('distancia')
            );
            if (eadOpt) {
                const $ = window.jQuery;
                if ($ && typeof $(modSelect).multiselect === 'function') {
                    $(modSelect).multiselect('deselectAll', false);
                    $(modSelect).multiselect('select', [eadOpt.value]);
                    $(modSelect).multiselect('refresh');
                    $(modSelect).trigger('change');
                } else {
                    modSelect.value = eadOpt.value;
                    modSelect.dispatchEvent(new Event('change', { bubbles: true }));
                }
                return { status: 'SUCCESS_UPDATED_MODALITY', eadText: eadOpt.text, details };
            }
        }
        return { status: 'MODALITY_SELECT_NOT_FOUND', details };
    }""")
    
    print("\nMODALITY SELECT TEST RESULT:")
    print(f"Status: {res['status']}")
    if 'eadText' in res:
        print(f"EAD Text: '{res['eadText']}'")
        
    print("\nFILTER SELECTS FOUND:")
    for d in res['details']:
        print(f" Select id='{d['id']}', name='{d['name']}':")
        for o in d['options']:
            print(f"   Option val='{o['value']}', text='{o['text']}', selected={o['selected']}")

    time.sleep(3)
    
    # Set 100 per page
    try:
        length_select = page.locator("select[name*='length'], select[name*='Table']").first
        if length_select.is_visible():
            length_select.select_option("100")
            time.sleep(3)
    except Exception:
        pass

    rows = page.locator("table tbody tr")
    print(f"\nTOTAL ROWS IN TABLE AFTER EAD FILTER: {rows.count()}")
    for i in range(rows.count()):
        tds = rows.nth(i).locator("td")
        if tds.count() > 3:
            disc_name = tds.nth(3).inner_text().strip()
            print(f" Row #{i+1}: '{disc_name}'")
            if "infraestrutura" in disc_name.lower():
                print(f" *** FOUND TARGET DISCIPLINA ON ROW #{i+1}: '{disc_name}' ***")

    time.sleep(5)
    context.close()
