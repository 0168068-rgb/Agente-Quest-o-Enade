from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    page = browser.contexts[0].pages[0]
    
    res = page.evaluate("""() => {
        const select = document.getElementById('Questao_IdTipoQuestao');
        if (!select) return 'Não encontrado';
        select.value = '60';
        select.dispatchEvent(new Event('change', { bubbles: true }));
        if (typeof $ !== 'undefined') $(select).trigger('change');
        return {
            selectedVal: select.value,
            selectedText: select.options[select.selectedIndex] ? select.options[select.selectedIndex].text : ''
        };
    }""")
    print("Resultado da seleção do Tipo:", res)
