from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "avalia" in pg.url][0]
    
    print("Conectado à página:", page.url)
    
    info = page.evaluate("""() => {
        const select = document.getElementById('Questao_IdTipo');
        if (!select) return 'Select #Questao_IdTipo não encontrado';
        
        const opts = Array.from(select.options).map(o => ({ value: o.value, text: o.text, selected: o.selected }));
        
        // Selecionar Múltipla escolha (geralmente valor '1' ou contendo 'Múltipla' / 'Simples')
        let targetVal = select.options[1] ? select.options[1].value : '1';
        for (let o of select.options) {
            if (o.text.toLowerCase().includes('múltipla') || o.text.toLowerCase().includes('multipla') || o.text.toLowerCase().includes('simples')) {
                targetVal = o.value;
                break;
            }
        }
        
        select.value = targetVal;
        select.dispatchEvent(new Event('change', { bubbles: true }));
        if (typeof $ !== 'undefined') $(select).trigger('change');
        
        return {
            options: opts,
            selectedVal: targetVal
        };
    }""")
    
    print("=== SELEÇÃO DO TIPO DE QUESTÃO ===")
    print(info)
