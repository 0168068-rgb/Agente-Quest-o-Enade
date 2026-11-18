from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "avalia" in pg.url][0]
    
    info = page.evaluate("""() => {
        const btnSave = document.getElementById('btnEnviarQuestao');
        const btnSaveNew = document.getElementById('btnEnviarQuestaoCriarNova');
        return {
            btnSaveExists: !!btnSave,
            btnSaveVisible: btnSave ? btnSave.offsetWidth > 0 : false,
            btnSaveNewExists: !!btnSaveNew,
            btnSaveNewVisible: btnSaveNew ? btnSaveNew.offsetWidth > 0 : false
        };
    }""")
    print("=== BOTÕES DE SALVAR/ENVIAR NO AVALIA ===")
    print(info)
