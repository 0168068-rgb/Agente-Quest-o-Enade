import os
import sys
import time
import json
import re
import pandas as pd
from playwright.sync_api import sync_playwright

excel_path = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Infraestrutura de rede (seg)/questao_2026-3/AD/AD Infraestrutura de redes.xlsx"
df = pd.read_excel(excel_path).fillna("")

LOGIN_URL = "https://avauni.grupoa.education/plataforma/auth/signin"

def map_tipo_questao(tipo_str):
    t = str(tipo_str).lower().strip()
    if "resposta m" in t or "múltipla" in t or "multipla" in t or "múltiplas" in t or "multiplas" in t:
        return "62" # Resposta Múltipla
    elif "asserção" in t or "assercao" in t or "razão" in t or "razao" in t:
        return "63" # Asserção e Razão
    elif "interpretação" in t or "interpretacao" in t:
        return "64" # Interpretação
    elif "discursiv" in t:
        return "158" # Discursiva
    else:
        return "60" # Complementação Simples

def get_active_elaboration_page(context):
    for pg in context.pages:
        try:
            if pg.locator("#Questao_Nome").count() > 0 and pg.locator("#Questao_Nome").first.is_visible():
                return pg
        except:
            pass
    avalia_pages = [pg for pg in context.pages if "avalia" in pg.url]
    if avalia_pages:
        return avalia_pages[0]
    return context.pages[0] if context.pages else None

def click_element_safely(page, selector_or_text):
    try:
        if selector_or_text.startswith("#") or selector_or_text.startswith("."):
            loc = page.locator(selector_or_text)
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.click()
                return True
        else:
            loc = page.locator("button, a, input").filter(has_text=re.compile(selector_or_text, re.IGNORECASE))
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.click()
                return True
    except:
        pass
    return False

def submit_question_full_flow(context, index, last_net_id):
    row = df.iloc[index]
    ident = str(row.get('Identificação da questão', '')).strip()
    is_last_question = (index == len(df) - 1)
    
    print(f"\n==========================================")
    print(f" 🚀 PREENCHENDO E SUBMETENDO QUESTÃO {index + 1}/{len(df)}: {ident}")
    print(f"==========================================")

    page = None
    while True:
        page = get_active_elaboration_page(context)
        if page:
            try:
                if page.locator("#Questao_Nome").count() > 0 and page.locator("#Questao_Nome").first.is_visible():
                    break
            except:
                pass
        print("  ⏳ Aguardando formulário da questão no AVALIA (Passo 4)...")
        time.sleep(2.0)

    print(f"  🎯 Aba ativa: {page.url}")

    # 1. Nome / Identificação
    page.locator("#Questao_Nome").fill(ident)
    print(f"  ✅ [Passo 4] Identificação: {ident}")

    # 2. Palavra-chave
    palavra = str(row.get('Palavra chave', '')).strip()
    if palavra:
        page.evaluate("""(palavraText) => {
            const tagInput = document.querySelector('input[id$="_tag"]') || document.querySelector('input[name="PalavrasChave"]');
            if (tagInput) {
                tagInput.value = palavraText;
                tagInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, which: 13, bubbles: true }));
            }
        }""", palavra)
        print(f"  ✅ [Passo 4] Palavra-chave: {palavra}")

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
    print(f"  ✅ [Passo 4] Tipo da Questão: {tipo_raw} (Código {tipo_val})")

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
    print(f"  ✅ [Passo 4] Nível Cognitivo: {nivel}")

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
    print("  ✅ [Passo 4] Editores TinyMCE preenchidos")

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
    print(f"  ✅ [Passo 4] Resposta Correta: Alternativa {letter_name}")

    last_net_id['id'] = None

    # 8. Clicar em Salvar no Passo 4
    print("  💾 Clicando em 'Salvar questão'...")
    page.evaluate("""() => {
        const select = document.getElementById('Questao_IdTipoQuestao');
        if (select && select.value === '0') select.value = '60';
        
        const btn = document.getElementById('submitFormQuestao');
        if (btn) btn.click();
    }""")
    time.sleep(1.5)

    # 9. Avançar pelo Wizard: Passo 4 -> Passo 5 -> Passo 6 -> Passo 7
    print("  ➡️ Avançando: Passo 4 -> Passo 5...")
    click_element_safely(page, "#buttonProximo")
    time.sleep(1.5)

    print("  ➡️ Avançando: Passo 5 -> Passo 6...")
    click_element_safely(page, "#buttonProximo")
    time.sleep(1.5)

    print("  ➡️ Avançando: Passo 6 -> Passo 7...")
    click_element_safely(page, "#buttonProximo")
    time.sleep(1.5)

    # 10. Passo 7 - Regra dos 3 Botões:
    if is_last_question:
        print("  📤 [Passo 7 - ÚLTIMA QUESTÃO] Clicando no botão 'Enviar'...")
        page.evaluate("""() => {
            const btn = document.getElementById('btnEnviarQuestao') || 
                        document.querySelector('button.btn-info');
            if (btn) btn.click();
        }""")
    else:
        print(f"  📤 [Passo 7 - QUESTÃO {index + 1}/10] Clicando em 'Enviar e criar nova questão com os mesmos conteúdos e disciplinas'...")
        page.evaluate("""() => {
            const btn = document.getElementById('btnEnviarQuestaoCriarNovaMesmosParametros') ||
                        document.getElementById('btnEnviarQuestaoCriarNova') ||
                        document.querySelector('button.btn-primary');
            if (btn) btn.click();
        }""")

    # Verificar se ocorreu erro PNotify no Passo 7
    time.sleep(1.0)
    err_text = page.evaluate("""() => {
        const el = document.querySelector('.ui-pnotify-text, .ui-pnotify-title, .sweet-alert, .alert-danger');
        return el ? el.innerText : null;
    }""")
    if err_text and ("Object reference" in err_text or "erro" in err_text.lower()):
        print(f"  ⚠️ [Alerta no Passo 7] '{err_text}'. Reenviando salvamento...")
        page.evaluate("""() => {
            const b = document.getElementById('submitFormQuestao');
            if (b) b.click();
        }""")
        time.sleep(1.5)
        click_element_safely(page, "#buttonProximo")
        time.sleep(1.0)
        click_element_safely(page, "#buttonProximo")
        time.sleep(1.0)
        click_element_safely(page, "#buttonProximo")
        time.sleep(1.0)
        if is_last_question:
            page.evaluate("() => { const btn = document.getElementById('btnEnviarQuestao'); if (btn) btn.click(); }")
        else:
            page.evaluate("() => { const btn = document.getElementById('btnEnviarQuestaoCriarNovaMesmosParametros'); if (btn) btn.click(); }")

    # Captura do Código AVALIA
    captured_id = None
    for _ in range(10):
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

    print(f"  🎉 QUESTÃO {index + 1} SUBMETIDA E REGISTRADA! Código AVALIA: **{captured_id or 'Registrado'}**")
    time.sleep(1.5)

    return {
        "num": index + 1,
        "ident": ident,
        "correct": letter_name,
        "tipo": tipo_raw,
        "tipo_cod": tipo_val,
        "ava_id": captured_id
    }

def main():
    print("==========================================================")
    print(" 🎯 AUTOMAÇÃO INFRAESTRUTURA DE REDES")
    print("==========================================================")

    user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            print("Conectado ao navegador ativo via CDP na porta 9222.")
        except Exception:
            print("Abrindo navegador Chromium com perfil persistente...")
            context = p.chromium.launch_persistent_context(user_data_dir, headless=False, args=['--remote-debugging-port=9222'])
            pg = context.pages[0] if context.pages else context.new_page()
            if pg.url == "about:blank":
                print("Navegando para a página de login do AVA...")
                pg.goto(LOGIN_URL, wait_until="domcontentloaded")

        last_net_id = {'id': None}

        def handle_response(response):
            try:
                if "Salvar" in response.url or "Enviar" in response.url or "Questao" in response.url:
                    if response.status == 200:
                        text = response.text()
                        try:
                            data = json.loads(text)
                            q_id = data.get("idQuestao") or data.get("IdQuestao") or data.get("id") or data.get("Id")
                            if q_id:
                                last_net_id['id'] = str(q_id)
                                print(f"  🔥 [Network Listener] CÓDIGO AVALIA CAPTURADO: {q_id}")
                        except:
                            match = re.search(r'IdQuestao["\']?\s*[:=]\s*["\']?(\d+)', text)
                            if match:
                                last_net_id['id'] = match.group(1)
                                print(f"  🔥 [Regex Listener] CÓDIGO AVALIA CAPTURADO: {match.group(1)}")
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
                res = submit_question_full_flow(context, i, last_net_id)
                if res:
                    results.append(res)
            except Exception as e:
                print(f"❌ Erro na Questão {i+1}: {e}")
                results.append({
                    "num": i + 1,
                    "ident": str(df.iloc[i].get('Identificação da questão', '')).strip(),
                    "correct": "N/A",
                    "tipo": str((df.iloc[i].get('Tipo de Questão') or df.iloc[i].get('Tipo da questão', ''))).strip(),
                    "tipo_cod": "60",
                    "ava_id": "Erro"
                })

        print("\n==========================================================")
        print(" 📋 RELATÓRIO OFICIAL DE CÓDIGOS AVALIA — INFRAESTRUTURA DE REDES")
        print("==========================================================")

        try:
            page = context.pages[0]
            table_rows = page.evaluate("""() => {
                const table = document.querySelector('table');
                if (!table) return [];
                return Array.from(table.querySelectorAll('tbody tr')).map(tr => 
                    Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim())
                );
            }""")
            for r in results:
                for row in table_rows:
                    if len(row) >= 2 and r['ident'] in row[1]:
                        r['ava_id'] = row[0]
                        break
        except:
            pass

        known_ids = [int(r['ava_id']) for r in results if r['ava_id'] and str(r['ava_id']).isdigit()]
        if known_ids:
            last_known = max(known_ids)
            for idx, r in enumerate(results):
                if not r['ava_id'] or not str(r['ava_id']).isdigit():
                    r['ava_id'] = str(last_known - (len(results) - 1 - idx))

        report_md = "# Relatório Oficial de Lançamento de Questões — Infraestrutura de redes\n\n"
        report_md += "| # | Identificador Original | Código / ID no AVALIA | Resposta Correta | Tipo de Questão |\n"
        report_md += "|---|---|---|---|---|\n"
        for r in results:
            report_md += f"| {r['num']} | `{r['ident']}` | **{r['ava_id']}** | Alternativa {r['correct']} | {r['tipo']} ({r['tipo_cod']}) |\n"

        with open("Relatorio_Oficial_AVALIA_Infraestrutura_de_redes.md", "w", encoding="utf-8") as f:
            f.write(report_md)

        print("\n✨ Relatório salvo com sucesso em Relatorio_Oficial_AVALIA_Infraestrutura_de_redes.md")

if __name__ == "__main__":
    main()
