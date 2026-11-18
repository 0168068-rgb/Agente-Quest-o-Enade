import os
import sys
import time
import json
import re
import pandas as pd
from playwright.sync_api import sync_playwright

excel_path = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Compiladores/questao_2026-3/AD/AD Compiladores.xlsx"
df = pd.read_excel(excel_path).fillna("")

def map_tipo_questao(tipo_str):
    t = str(tipo_str).lower().strip()
    if "resposta m" in t or "múltipla" in t or "multipla" in t or "múltiplas" in t or "multiplas" in t:
        return "62" # Questão de Resposta Múltipla
    elif "asserção" in t or "assercao" in t or "razão" in t or "razao" in t:
        return "63" # Questão de Asserção e Razão
    elif "interpretação" in t or "interpretacao" in t:
        return "64" # Questão de Interpretação
    elif "discursiv" in t:
        return "158" # Questão Discursiva
    else:
        return "60" # Questão de Complementação Simples

def fill_question(page, index, last_net_id):
    row = df.iloc[index]
    ident = str(row.get('Identificação da questão', '')).strip()
    print(f"\n==========================================")
    print(f" 🚀 PREENCHENDO E SALVANDO QUESTÃO {index + 1}/{len(df)}: {ident}")
    print(f"==========================================")

    # Aguardar campo #Questao_Nome estar visível na página
    page.locator("#Questao_Nome").wait_for(state="visible", timeout=600000)

    # 1. Nome / Identificação
    page.locator("#Questao_Nome").fill(ident)
    print(f"  ✅ Identificação: {ident}")

    # 2. Palavra-chave
    palavra = str(row.get('Palavra chave', '')).strip()
    if palavra:
        page.locator("#PalavrasChave").fill(palavra)
        page.keyboard.press("Enter")
        print(f"  ✅ Palavra-chave: {palavra}")

    # 3. Tipo da Questão
    tipo_raw = str((row.get('Tipo de Questão') or row.get('Tipo da questão', '')))
    tipo_val = map_tipo_questao(tipo_raw)
    page.evaluate(f"""() => {{
        const select = document.getElementById('Questao_IdTipoQuestao');
        if (select) {{
            select.value = '{tipo_val}';
            select.dispatchEvent(new Event('change', {{ bubbles: true }}));
            if (typeof $ !== 'undefined') $(select).trigger('change');
        }}
    }}""")
    print(f"  ✅ Tipo da Questão: {tipo_raw} (Código {tipo_val})")

    # 4. Nível cognitivo
    nivel = str(row.get('Nível cognitivo', '')).strip()
    page.evaluate(f"""(nivelText) => {{
        const select = document.getElementById('Questao_IdNivelCognitivo') || document.getElementById('IdHabilidadeQuestao');
        if (select) {{
            let matched = false;
            for (let opt of select.options) {{
                if (opt.text.toLowerCase().includes(nivelText.toLowerCase())) {{
                    select.value = opt.value;
                    select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    if (typeof $ !== 'undefined') $(select).trigger('change');
                    matched = true;
                    break;
                }}
            }}
            if (!matched && select.options.length > 1) {{
                select.options[1].selected = true;
                select.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
        }}
    }}""", nivel)
    print(f"  ✅ Nível Cognitivo: {nivel}")

    # 5. Textos TinyMCE
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
            return true;
        }
        return false;
    }"""
    page.evaluate(js_tinymce, {
        "texto_q": texto_q,
        "alt_a": alt_a,
        "alt_b": alt_b,
        "alt_c": alt_c,
        "alt_d": alt_d,
        "feedback": feedback
    })
    print("  ✅ Editores TinyMCE preenchidos")

    # 6. Remover Alternativa E se vazia
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

    page.evaluate("""(idx) => {
        const selector = 'input[name="Afirmativas[' + idx + '].Verdadeira"]';
        if (typeof $ !== 'undefined' && $.fn && $.fn.iCheck) {
            $(selector).iCheck('check');
        }
    }""", correct_idx)
    letter_name = ["A", "B", "C", "D"][correct_idx]
    print(f"  ✅ Resposta Correta Marcada: Alternativa {letter_name}")

    last_net_id['id'] = None

    # 8. Clicar em Salvar
    print("  💾 Clicando em 'Salvar questão'...")
    page.evaluate("""() => {
        const select = document.getElementById('Questao_IdTipoQuestao');
        if (select && select.value === '0') select.value = '60';
        
        const btn = document.getElementById('submitFormQuestao');
        if (btn) btn.click();
    }""")

    captured_id = "Pendente"
    for _ in range(20):
        time.sleep(0.5)
        if last_net_id.get('id'):
            captured_id = str(last_net_id['id'])
            break
        h_val = page.evaluate("""() => {
            const hidden = document.getElementById('Questao_IdQuestao');
            return hidden ? hidden.value : null;
        }""")
        if h_val and h_val != "0" and h_val != "":
            captured_id = str(h_val)
            break

    print(f"  🎉 QUESTÃO {index + 1} SALVA! Código AVALIA Atribuído: **{captured_id}**")

    # 9. Avançar para a próxima questão (se houver)
    if index < len(df) - 1:
        time.sleep(1.5)
        page.evaluate("""() => {
            const btnNova = document.getElementById('btnEnviarQuestaoCriarNova') || 
                            document.getElementById('btnEnviarQuestaoCriarNovaMesmosParametros') ||
                            document.querySelector('a[href*="ElaborarQuestao"], button[onclick*="novaQuestao"]');
            if (btnNova && btnNova.offsetWidth > 0) {
                btnNova.click();
            } else if (typeof $ !== 'undefined' && $('#formSalvarQuestao').length > 0) {
                $('#Questao_Nome').val('');
            }
        }""")
        time.sleep(1.5)

    return {
        "num": index + 1,
        "ident": ident,
        "correct": letter_name,
        "ava_id": captured_id
    }

def main():
    print("==========================================================")
    print(" 🎯 AUTOMAÇÃO COMPILADORES — PASSO 4")
    print("==========================================================")

    user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            print("Conectado via CDP na porta 9222.")
        except Exception:
            print("Abrindo navegador Chromium...")
            context = p.chromium.launch_persistent_context(user_data_dir, headless=False, args=['--remote-debugging-port=9222'])

        pages = [pg for pg in context.pages if "avalia" in pg.url]
        if pages:
            page = pages[0]
        else:
            page = context.pages[0] if context.pages else context.new_page()

        if page.url == "about:blank":
            print("Redirecionando aba branca para AVALIA...")
            page.goto("https://avalia.grupoa.com.br/Elaborador", wait_until="domcontentloaded")

        last_net_id = {'id': None}

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
                                print(f"  🔥 [Network Listener] AVALIA ID Detectado: {q_id}")
                        except:
                            match = re.search(r'IdQuestao["\']?\s*[:=]\s*["\']?(\d+)', text)
                            if match:
                                last_net_id['id'] = match.group(1)
                                print(f"  🔥 [Regex Listener] AVALIA ID Detectado: {match.group(1)}")
            except:
                pass

        def setup_listeners(target_page):
            target_page.on("response", handle_response)

        for pg in context.pages:
            setup_listeners(pg)
        context.on("page", setup_listeners)

        results = []
        for i in range(len(df)):
            try:
                res = fill_question(page, i, last_net_id)
                results.append(res)
            except Exception as e:
                print(f"❌ Erro na Questão {i+1}: {e}")
                results.append({
                    "num": i + 1,
                    "ident": str(df.iloc[i].get('Identificação da questão', '')).strip(),
                    "correct": "N/A",
                    "ava_id": "Erro"
                })

        print("\n==========================================================")
        print(" 📋 RELATÓRIO OFICIAL DE CÓDIGOS AVALIA — COMPILADORES")
        print("==========================================================")
        print(f"{'#':<3} | {'IDENTIFICADOR ORIGINAL':<35} | {'CÓDIGO AVALIA':<15} | {'CORRETA':<7}")
        print("-" * 70)
        for r in results:
            print(f"{r['num']:<3} | {r['ident']:<35} | {r['ava_id']:<15} | {r['correct']:<7}")

        report_md = "# Relatório Oficial de Lançamento de Questões — Compiladores\n\n"
        report_md += "| # | Identificador Original | Código / ID no AVALIA | Resposta Correta |\n"
        report_md += "|---|---|---|---|\n"
        for r in results:
            report_md += f"| {r['num']} | `{r['ident']}` | **{r['ava_id']}** | Alternativa {r['correct']} |\n"

        with open("Relatorio_Oficial_AVALIA_Compiladores.md", "w", encoding="utf-8") as f:
            f.write(report_md)

        print("\n✨ Relatório salvo com sucesso em Relatorio_Oficial_AVALIA_Compiladores.md")

if __name__ == "__main__":
    main()
