from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "avalia" in pg.url][0]
    
    print("Conectado à página:", page.url)
    
    js_code = """(idx) => {
        const selector = 'input[name="Afirmativas[' + idx + '].Verdadeira"]';
        const input = document.querySelector(selector);
        
        if (!input) return 'Input ' + selector + ' não encontrado';
        
        // 1. Tentar iCheck via jQuery
        if (typeof $ !== 'undefined' && $.fn && $.fn.iCheck) {
            $(selector).iCheck('check');
            return 'Alternativa ' + idx + ' marcada via iCheck jQuery!';
        }
        
        // 2. Clicar no iCheck-helper ou wrapper div
        const wrapper = input.closest('.iradio_flat-green, .iradio_square-green, .iradio_flat, div[class*="iradio"]');
        if (wrapper) {
            const helper = wrapper.querySelector('.iCheck-helper') || wrapper;
            helper.click();
            return 'Alternativa ' + idx + ' marcada clicando no iCheck-helper!';
        }
        
        // 3. Fallback direct click
        input.click();
        input.checked = true;
        return 'Alternativa ' + idx + ' marcada via click direto.';
    }"""
    
    res = page.evaluate(js_code, 0)
    print("Resultado da marcação:", res)
