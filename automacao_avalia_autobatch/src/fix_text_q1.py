import pandas as pd
from playwright.sync_api import sync_playwright

excel_path = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Cabeamento estruturado II (seg)/questao_2026-3/AD/AD Cabeamento estruturado II.xlsx"
df = pd.read_excel(excel_path).fillna("")

row0 = df.iloc[0]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "avalia" in pg.url][0]
    
    print("Conectado à página:", page.url)
    
    # 1. Usar o texto exato da planilha sem duplicar "Disciplina:"
    texto_q = str(row0.get('Texto da Questão', ''))
    
    # Preencher no TinyMCE
    js_tinymce = """(texto) => {
        if (typeof tinymce !== 'undefined') {
            let inst = tinymce.get('TextoQuestao');
            if (inst) {
                inst.setContent(texto.replace(/\\n/g, '<br>'));
                return 'Texto corrigido com sucesso!';
            }
        }
        return 'TinyMCE TextoQuestao não encontrado';
    }"""
    
    res = page.evaluate(js_tinymce, texto_q)
    print("Resultado da correção:", res)

print("\n✨ TEXTO CORRIGIDO COM SUCESSO NO NAVEGADOR!")
