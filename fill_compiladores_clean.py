import pandas as pd
from playwright.sync_api import sync_playwright

excel_path = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Compiladores/questao_2026-3/AD/AD Compiladores.xlsx"
df = pd.read_excel(excel_path).fillna("")

row0 = df.iloc[0]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "avalia" in pg.url][0]
    
    print("Conectado à página:", page.url)
    
    # 1. Limpar / Preencher Identificação
    ident = str(row0.get('Identificação da questão', '')).strip()
    if page.locator("#Questao_Nome").count() > 0:
        page.locator("#Questao_Nome").fill(ident)
        print("✅ Identificação:", ident)
        
    # 2. Palavras-chave
    palavra = str(row0.get('Palavra chave', '')).strip()
    if page.locator("#PalavrasChave").count() > 0:
        page.locator("#PalavrasChave").fill(palavra)
        page.keyboard.press("Enter")
        print("✅ Palavra-chave:", palavra)
        
    # 3. Tipo
    if page.locator("#Questao_IdTipo").count() > 0:
        try:
            page.locator("#Questao_IdTipo").select_option(value="1")
            print("✅ Tipo: Múltipla Escolha")
        except:
            pass

    # 4. Nível cognitivo
    nivel = str(row0.get('Nível cognitivo', '')).strip()
    for select_id in ["#Questao_IdNivelCognitivo", "#Questao_IdNivelDificuldade", "#Questao_IdGrauDificuldade"]:
        if page.locator(select_id).count() > 0:
            try:
                opts = page.locator(f"{select_id} option").all_inner_texts()
                for idx_opt, opt in enumerate(opts):
                    if nivel.lower() in opt.lower():
                        page.locator(select_id).select_option(index=idx_opt)
                        print(f"✅ Nível Cognitivo: {opt.strip()}")
                        break
            except Exception:
                pass

    # 5. Textos (mantendo texto exato)
    texto_q = str(row0.get('Texto da Questão', ''))
    alt_a = str(row0.get('Alternativa A', ''))
    alt_b = str(row0.get('Alternativa B', ''))
    alt_c = str(row0.get('Alternativa C', ''))
    alt_d = str(row0.get('Alternativa D', ''))
    feedback = str(row0.get('Feedback da questão', ''))
    
    js_tinymce = """(data) => {
        if (typeof tinymce !== 'undefined') {
            const map = {
                'TextoQuestao': data.texto_q,
                'TextoAfirmativaA': data.alt_a,
                'TextoAfirmativaB': data.alt_b,
                'TextoAfirmativaC': data.alt_c,
                'TextoAfirmativaD': data.alt_d,
                'TextoPadraoResposta': data.feedback,
                'TextoFeedbackQuestao': data.feedback
            };
            
            for (let id in map) {
                let inst = tinymce.get(id);
                if (inst) {
                    inst.setContent(map[id].replace(/\\n/g, '<br>'));
                }
            }
            return 'TinyMCE preenchido!';
        }
        return 'TinyMCE ausente';
    }"""
    
    res = page.evaluate(js_tinymce, {
        "texto_q": texto_q,
        "alt_a": alt_a,
        "alt_b": alt_b,
        "alt_c": alt_c,
        "alt_d": alt_d,
        "feedback": feedback
    })
    print("✅ Editores TinyMCE:", res)

    # 6. Remoção de Alternativa E
    alt_e = str(row0.get('Alternativa E', '')).strip()
    if not alt_e:
        page.evaluate("""() => {
            const btnDeleteE = document.querySelector('button[onclick*="removerAfirmativa"], a[onclick*="removerAfirmativa"], .btn-remove-afirmativa, i.fa-trash');
            if (btnDeleteE) btnDeleteE.click();
        }""")

    # 7. Marcar Alternativa Correta via iCheck (Alternativa C = índice 2)
    correct_idx = 2 # Alternativa C
    js_icheck = """(idx) => {
        const selector = 'input[name="Afirmativas[' + idx + '].Verdadeira"]';
        if (typeof $ !== 'undefined' && $.fn && $.fn.iCheck) {
            $(selector).iCheck('check');
            return 'iCheck OK';
        }
        return 'Fallback';
    }"""
    
    icheck_res = page.evaluate(js_icheck, correct_idx)
    print("✅ Resposta Correta (Alternativa C) marcada:", icheck_res)

print("\n✨ QUESTÃO 1 DE COMPILADORES PREENCHIDA COM SUCESSO NO FORMULÁRIO!")
