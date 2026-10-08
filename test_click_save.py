from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "avalia" in pg.url][0]
    
    print("Conectado ao AVALIA para salvar...")
    
    res = page.evaluate("""() => {
        const btnSave = document.getElementById('submitFormQuestao') || 
                        document.querySelector('button[type="submit"]') ||
                        document.querySelector('.btn-info[onclick*="Salvar"], button[onclick*="salvar"]');
        if (btnSave) {
            btnSave.click();
            return 'Botão de Salvar clicado com sucesso!';
        }
        
        const form = document.getElementById('formSalvarQuestao');
        if (form) {
            form.submit();
            return 'Formulário submetido via form.submit()!';
        }
        
        return 'Nenhum botão ou formulário de salvar encontrado';
    }""")
    
    print("Resultado da ação de salvar:", res)
