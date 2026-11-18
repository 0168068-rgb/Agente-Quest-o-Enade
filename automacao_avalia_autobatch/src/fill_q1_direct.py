import pandas as pd
from playwright.sync_api import sync_playwright

excel_path = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Cabeamento estruturado II (seg)/questao_2026-3/AD/AD Cabeamento estruturado II.xlsx"
df = pd.read_excel(excel_path).fillna("")

row0 = df.iloc[0]

print("=== CONTEÚDO DA DA 1ª QUESTÃO DO EXCEL ===")
for col in df.columns:
    print(f"  {col}: {str(row0[col])[:80]}")

with sync_playwright() as p:
    try:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = None
        for pg in context.pages:
            if "avalia" in pg.url:
                page = pg
                break
                
        if not page:
            page = context.pages[0]
            
        print(f"\nConectado à página: {page.url}")
        
        # 1. Identificação
        identificacao = str(row0.get('Identificação da questão', '')) or str(row0.get('Ordem', '1'))
        if page.locator("#Questao_Nome").count() > 0:
            page.locator("#Questao_Nome").fill(identificacao)
            print("✅ Preenchido Identificação:", identificacao)
            
        # 2. Palavra-chave
        palavra_chave = str(row0.get('Palavra chave', ''))
        if palavra_chave and page.locator("#PalavrasChave").count() > 0:
            page.locator("#PalavrasChave").fill(palavra_chave)
            page.keyboard.press("Enter")
            print("✅ Preenchido Palavra-chave:", palavra_chave)
            
        # 3. Rich Text Editors (CKEditor ou TinyMCE ou iframe / textarea)
        # Vamos preencher Texto da Questão
        texto_q = str(row0.get('Texto da Questão', ''))
        print("Texto da Questão:", texto_q[:60])
        
        # Injetar HTML / texto nos editors usando a API CKEDITOR do site se existir
        js_fill = """(data) => {
            if (typeof CKEDITOR !== 'undefined') {
                for (var instance in CKEDITOR.instances) {
                    var inst = CKEDITOR.instances[instance];
                    if (instance.includes('TextoQuestao') || instance === 'TextoQuestao') {
                        inst.setData(data.texto_q);
                    } else if (instance.includes('TextoAfirmativaA') || instance === 'TextoAfirmativaA') {
                        inst.setData(data.alt_a);
                    } else if (instance.includes('TextoAfirmativaB') || instance === 'TextoAfirmativaB') {
                        inst.setData(data.alt_b);
                    } else if (instance.includes('TextoAfirmativaC') || instance === 'TextoAfirmativaC') {
                        inst.setData(data.alt_c);
                    } else if (instance.includes('TextoAfirmativaD') || instance === 'TextoAfirmativaD') {
                        inst.setData(data.alt_d);
                    } else if (instance.includes('TextoFeedbackQuestao') || instance === 'TextoFeedbackQuestao' || instance.includes('TextoPadraoResposta')) {
                        inst.setData(data.feedback);
                    }
                }
                return 'CKEditor preenchido com sucesso!';
            }
            return 'CKEDITOR não encontrado na página';
        }"""
        
        data_payload = {
            "texto_q": str(row0.get('Texto da Questão', '')),
            "alt_a": str(row0.get('Alternativa A', '')),
            "alt_b": str(row0.get('Alternativa B', '')),
            "alt_c": str(row0.get('Alternativa C', '')),
            "alt_d": str(row0.get('Alternativa D', '')),
            "feedback": str(row0.get('Feedback da questão', ''))
        }
        
        res = page.evaluate(js_fill, data_payload)
        print("Resultado do preenchimento CKEditor:", res)
        
    except Exception as e:
        print("Erro ao conectar/preencher:", e)
