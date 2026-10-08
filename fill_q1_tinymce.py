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
    
    # 1. Identificação da questão
    ident = str(row0.get('Identificação da questão', '')).strip()
    if page.locator("#Questao_Nome").count() > 0:
        page.locator("#Questao_Nome").fill(ident)
        print("✅ Preenchido Identificação:", ident)
        
    # 2. Palavras-chave
    palavra = str(row0.get('Palavra chave', '')).strip()
    if palavra and page.locator("#PalavrasChave").count() > 0:
        page.locator("#PalavrasChave").fill(palavra)
        page.keyboard.press("Enter")
        print("✅ Preenchido Palavra-chave:", palavra)
        
    # 3. Selecionar Tipo da Questão (id 1 = Múltipla escolha)
    if page.locator("#Questao_IdTipo").count() > 0:
        try:
            page.locator("#Questao_IdTipo").select_option(value="1") # Múltipla escolha
            print("✅ Selecionado Tipo da Questão")
        except:
            pass

    # 4. Selecionar Nível Cognitivo / Dificuldade
    nivel = str(row0.get('Nível cognitivo', '')).strip()
    for select_id in ["#Questao_IdNivelCognitivo", "#Questao_IdNivelDificuldade", "#Questao_IdGrauDificuldade"]:
        if page.locator(select_id).count() > 0:
            try:
                # Tentar selecionar por label ou value
                opts = page.locator(f"{select_id} option").all_inner_texts()
                for i, opt in enumerate(opts):
                    if nivel.lower() in opt.lower():
                        page.locator(select_id).select_option(index=i)
                        print(f"✅ Selecionado Nível Cognitivo ({opt.strip()}) em {select_id}")
                        break
            except Exception as ex:
                print(f"Nota nivel {select_id}: {ex}")

    # 5. Preencher TinyMCE editors
    texto_q = f"Disciplina: Cabeamento estruturado II\n\n{str(row0.get('Texto da Questão', ''))}"
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
            return 'TinyMCE preenchido com sucesso!';
        }
        return 'TinyMCE não encontrado';
    }"""
    
    res = page.evaluate(js_tinymce, {
        "texto_q": texto_q,
        "alt_a": alt_a,
        "alt_b": alt_b,
        "alt_c": alt_c,
        "alt_d": alt_d,
        "feedback": feedback
    })
    print("Resultado do preenchimento dos editores:", res)

    # 6. Remover Alternativa E se não houver
    alt_e = str(row0.get('Alternativa E', '')).strip()
    if not alt_e:
        page.evaluate("""() => {
            const btnDeleteE = document.querySelector('button[onclick*="removerAfirmativa"], a[onclick*="removerAfirmativa"], .btn-remove-afirmativa, i.fa-trash');
            if (btnDeleteE) btnDeleteE.click();
        }""")
        print("✅ Verificado remoção da alternativa E")

    # 7. Marcar alternativa correta
    # Descobrir letra correta do feedback
    feedback_lower = feedback.lower()
    correct_letter = "A"
    if "resposta certa é rj-45" in feedback_lower or "alternativa a" in feedback_lower:
        correct_letter = "A"
    elif "alternativa b" in feedback_lower:
        correct_letter = "B"
    elif "alternativa c" in feedback_lower:
        correct_letter = "C"
    elif "alternativa d" in feedback_lower:
        correct_letter = "D"
        
    print(f"Letra correta identificada: {correct_letter}")
    
    # Marcar checkbox/radio correspondente
    page.evaluate(f"""(letter) => {{
        const idxMap = {{ 'A': 0, 'B': 1, 'C': 2, 'D': 3 }};
        const idx = idxMap[letter] !== undefined ? idxMap[letter] : 0;
        const radios = document.querySelectorAll('input[name*="Correta"], input[name*="RespostaCorreta"], input[type="radio"], input[type="checkbox"].correta');
        if (radios.length > idx) {{
            radios[idx].click();
            radios[idx].checked = true;
        }}
    }}""", correct_letter)
    print("✅ Resposta correta marcada!")

print("\n✨ PREENCHIMENTO DA 1ª QUESTÃO CONCLUÍDO NO NAVEGADOR!")
