import os
import sys
import time
import json
import pandas as pd
from playwright.sync_api import sync_playwright

excel_path = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Compiladores/questao_2026-3/AD/AD Compiladores.xlsx"
df = pd.read_excel(excel_path).fillna("")

results_tracker = []

def fill_question_index(page, index):
    if index >= len(df):
        return False, "", ""

    row = df.iloc[index]
    ident = str(row.get('Identificação da questão', '')).strip()
    print(f"\n==========================================")
    print(f" 🚀 PREENCHENDO QUESTÃO {index + 1}/{len(df)}: {ident}")
    print(f"==========================================")

    # 1. Identificação
    if page.locator("#Questao_Nome").count() > 0:
        page.locator("#Questao_Nome").fill(ident)
        print("  ✅ Identificação:", ident)
        
    # 2. Palavra-chave
    palavra = str(row.get('Palavra chave', '')).strip()
    if palavra and page.locator("#PalavrasChave").count() > 0:
        page.locator("#PalavrasChave").fill(palavra)
        page.keyboard.press("Enter")
        print("  ✅ Palavra-chave:", palavra)
        
    # 3. Tipo
    if page.locator("#Questao_IdTipo").count() > 0:
        try:
            page.locator("#Questao_IdTipo").select_option(value="1")
            print("  ✅ Tipo: Múltipla Escolha")
        except:
            pass

    # 4. Nível cognitivo
    nivel = str(row.get('Nível cognitivo', '')).strip()
    for select_id in ["#Questao_IdNivelCognitivo", "#Questao_IdNivelDificuldade", "#Questao_IdGrauDificuldade"]:
        if page.locator(select_id).count() > 0:
            try:
                opts = page.locator(f"{select_id} option").all_inner_texts()
                for idx_opt, opt in enumerate(opts):
                    if nivel.lower() in opt.lower():
                        page.locator(select_id).select_option(index=idx_opt)
                        print(f"  ✅ Nível Cognitivo: {opt.strip()}")
                        break
            except Exception:
                pass

    # 5. Textos (mantendo texto limpo da planilha sem duplicações)
    texto_q = str(row.get('Texto da Questão', ''))
    alt_a = str(row.get('Alternativa A', ''))
    alt_b = str(row.get('Alternativa B', ''))
    alt_c = str(row.get('Alternativa C', ''))
    alt_d = str(row.get('Alternativa D', ''))
    feedback = str(row.get('Feedback da questão', ''))
    
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
            return 'OK';
        }
        return 'ERR';
    }"""
    
    res = page.evaluate(js_tinymce, {
        "texto_q": texto_q,
        "alt_a": alt_a,
        "alt_b": alt_b,
        "alt_c": alt_c,
        "alt_d": alt_d,
        "feedback": feedback
    })
    print("  ✅ Editores TinyMCE preenchidos.")

    # 6. Remoção de Alternativa E
    alt_e = str(row.get('Alternativa E', '')).strip()
    if not alt_e:
        page.evaluate("""() => {
            const btnDeleteE = document.querySelector('button[onclick*="removerAfirmativa"], a[onclick*="removerAfirmativa"], .btn-remove-afirmativa, i.fa-trash');
            if (btnDeleteE) btnDeleteE.click();
        }""")

    # 7. Resposta Correta (iCheck)
    feedback_lower = feedback.lower()
    alt_a_lower = alt_a.lower().rstrip('.')
    alt_b_lower = alt_b.lower().rstrip('.')
    alt_c_lower = alt_c.lower().rstrip('.')
    alt_d_lower = alt_d.lower().rstrip('.')
    
    correct_idx = 0
    if "resposta certa é " + alt_a_lower in feedback_lower or "alternativa a" in feedback_lower:
        correct_idx = 0
    elif "resposta certa é " + alt_b_lower in feedback_lower or "alternativa b" in feedback_lower:
        correct_idx = 1
    elif "resposta certa é " + alt_c_lower in feedback_lower or "alternativa c" in feedback_lower:
        correct_idx = 2
    elif "resposta certa é " + alt_d_lower in feedback_lower or "alternativa d" in feedback_lower:
        correct_idx = 3
    else:
        for idx_letter, text_alt in enumerate([alt_a_lower, alt_b_lower, alt_c_lower, alt_d_lower]):
            if text_alt and text_alt in feedback_lower[:120]:
                correct_idx = idx_letter
                break

    js_icheck = """(idx) => {
        const selector = 'input[name="Afirmativas[' + idx + '].Verdadeira"]';
        if (typeof $ !== 'undefined' && $.fn && $.fn.iCheck) {
            $(selector).iCheck('check');
        }
    }"""
    page.evaluate(js_icheck, correct_idx)
    letter_name = ["A", "B", "C", "D"][correct_idx]
    print(f"  ✅ Resposta Correta Marcada: Alternativa {letter_name}")
    print(f"✨ Questão {index + 1} pronta no formulário!")
    return True, ident, letter_name

def main():
    print("==========================================================")
    print(" 🎯 AUTOMAÇÃO COMPILADORES COM CAPTURA DE CÓDIGO AVALIA")
    print("==========================================================")
    
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = [pg for pg in context.pages if "avalia" in pg.url][0]
        
        last_net_id = {}
        
        def handle_response(response):
            try:
                if "SalvarQuestao" in response.url or "Salvar" in response.url:
                    if response.status == 200:
                        text = response.text()
                        try:
                            data = json.loads(text)
                            q_id = data.get("idQuestao") or data.get("IdQuestao") or data.get("id")
                            if q_id:
                                last_net_id['id'] = str(q_id)
                                print(f"  🔥 [REDE] CÓDIGO AVALIA ATRIBUÍDO: {q_id}")
                        except:
                            pass
            except:
                pass

        page.on("response", handle_response)
        
        # Questão 1 já foi preenchida na tela (índice 0)
        # Vamos monitorar o avanço das questões (0 a 9)
        current_idx = 1 # Inicia aguardando o formulário limpo para a Questão 2
        last_filled = "UA-02_QUESTÃO-1_OBJ-1_FÁCIL"
        
        # Adicionar a Q1 no rastreador
        results_tracker = [{
            "num": 1,
            "ident": "UA-02_QUESTÃO-1_OBJ-1_FÁCIL",
            "correct": "C",
            "ava_id": "Pendente"
        }]

        while current_idx < len(df):
            try:
                # Verificar se o formulário está visível e limpo para a próxima questão
                val = page.evaluate("""() => {
                    const el = document.getElementById('Questao_Nome');
                    const hiddenId = document.getElementById('Questao_IdQuestao');
                    return {
                        val: el ? el.value.trim() : null,
                        hiddenId: hiddenId ? hiddenId.value : null
                    };
                }""")
                
                target_ident = str(df.iloc[current_idx].get('Identificação da questão', '')).strip()
                
                # Se a questão anterior foi salva, tentar capturar o ID do hiddenId ou last_net_id
                if current_idx > 0 and results_tracker[current_idx - 1]["ava_id"] == "Pendente":
                    captured_id = val.get('hiddenId') or last_net_id.get('id')
                    if captured_id and captured_id != "0":
                        results_tracker[current_idx - 1]["ava_id"] = str(captured_id)
                        print(f"  📌 Código AVALIA da Questão {current_idx}: {captured_id}")

                # Se o formulário está limpo ou pronto para a nova questão
                if val['val'] is not None and (val['val'] == "" or (val['val'] != target_ident and val['val'] != last_filled)):
                    time.sleep(0.8)
                    success, ident_filled, letter_name = fill_question_index(page, current_idx)
                    if success:
                        last_filled = ident_filled
                        results_tracker.append({
                            "num": current_idx + 1,
                            "ident": ident_filled,
                            "correct": letter_name,
                            "ava_id": "Pendente"
                        })
                        current_idx += 1
                        print(f"⏳ Questão {current_idx}/{len(df)} pronta no formulário. Salve para gerar o código AVALIA!")
                
                time.sleep(1.5)
            except Exception as e:
                time.sleep(2.0)

        # Atualizar ID final da Q10 se capturado
        time.sleep(2)
        if results_tracker and results_tracker[-1]["ava_id"] == "Pendente":
            captured_id = last_net_id.get('id') or page.evaluate("() => document.getElementById('Questao_IdQuestao') ? document.getElementById('Questao_IdQuestao').value : null")
            if captured_id and captured_id != "0":
                results_tracker[-1]["ava_id"] = str(captured_id)

        print("\n==========================================================")
        print(" 📋 RELATÓRIO FINAL DE CÓDIGOS AVALIA — COMPILADORES")
        print("==========================================================")
        print(f"{'#':<3} | {'IDENTIFICADOR ORIGINAL':<35} | {'CÓDIGO AVALIA':<15} | {'CORRETA':<7}")
        print("-" * 70)
        for r in results_tracker:
            print(f"{r['num']:<3} | {r['ident']:<35} | {r['ava_id']:<15} | {r['correct']:<7}")
            
        report_md = "# Relatório de Lançamento de Questões — Compiladores\n\n"
        report_md += "| # | Identificador Original | Código / ID no AVALIA | Resposta Correta |\n"
        report_md += "|---|---|---|---|\n"
        for r in results_tracker:
            report_md += f"| {r['num']} | `{r['ident']}` | **{r['ava_id']}** | Alternativa {r['correct']} |\n"
            
        with open("Relatorio_AVALIA_Compiladores.md", "w", encoding="utf-8") as f:
            f.write(report_md)
            
        print("\n✨ Relatório salvo em Relatorio_AVALIA_Compiladores.md")

if __name__ == "__main__":
    main()
