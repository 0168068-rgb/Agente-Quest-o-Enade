import os
import sys
import time
import re
import json
import pandas as pd
from playwright.sync_api import sync_playwright

def get_active_page(context):
    # Procura pela aba que está na URL do Elaborador do Grupo A
    for p in context.pages:
        try:
            url = p.url
            if "avalia.grupoa" in url or "Elaborador" in url:
                return p
        except:
            pass
            
    # Se não encontrar, retorna a última aba aberta
    if context.pages:
        return context.pages[-1]
    return None

def load_data(excel_path=None):
    if not excel_path:
        # Look for default files in workspace
        default_files = [
            "/home/hamilcar/Antigravity/questoes_fisioterapia_cardiaca_UA7.xlsx",
            "/home/hamilcar/Antigravity/questoes_fisioterapia_cardiaca.xlsx"
        ]
        for f in default_files:
            if os.path.exists(f):
                excel_path = f
                break
                
    if not excel_path or not os.path.exists(excel_path):
        excel_path = input("Digite o caminho para o arquivo Excel (.xlsx): ").strip()
        
    if not os.path.exists(excel_path):
        print(f"Erro: Arquivo Excel não encontrado em: {excel_path}")
        return None
        
    print(f"Carregando planilha Excel: {excel_path}...")
    try:
        df = pd.read_excel(excel_path)
        df = df.fillna("")
        print(f"Sucesso: {len(df)} questões carregadas.")
        return df, excel_path
    except Exception as e:
        print(f"Erro ao ler arquivo Excel: {e}")
        return None, None

def find_correct_alternative(row):
    feedback = str(row.get('Feedback da questão', '')).strip().lower()
    alt_a = str(row.get('Alternativa A', '')).strip().lower()
    alt_b = str(row.get('Alternativa B', '')).strip().lower()
    alt_c = str(row.get('Alternativa C', '')).strip().lower()
    alt_d = str(row.get('Alternativa D', '')).strip().lower()
    
    # Remove prefix "a resposta certa é" if present
    if feedback.startswith("a resposta certa é"):
        feedback_clean = feedback[len("a resposta certa é"):].strip()
    else:
        feedback_clean = feedback
        
    alts = {
        'A': alt_a,
        'B': alt_b,
        'C': alt_c,
        'D': alt_d
    }
    
    # Try exact match at the start of clean feedback
    for letter, text in alts.items():
        if not text:
            continue
        text_clean = text.rstrip('.')
        if feedback_clean.startswith(text_clean):
            return letter
            
    # Fallback: check if the alternative text is found in the first part of the feedback
    for letter, text in alts.items():
        if not text:
            continue
        text_clean = text.rstrip('.')
        if text_clean in feedback_clean[:150]:
            return letter
            
    # Second fallback: check if there's any mention of "Alternativa A", etc. or "resposta certa é A"
    match = re.search(r'alternativa\s+([a-d])', feedback, re.IGNORECASE)
    if match:
        return match.group(1).upper()
        
    # If still not found, return A as fallback
    print(f"Aviso: Não foi possível identificar a resposta certa automaticamente para a questão: {row.get('Identificação da questão')}")
    return 'A'

def extract_correct_answer_letter(row):
    # Search for an explicit column first
    col_names = [col for col in row.index if str(col).strip().lower() in ("resposta certa", "resposta_certa", "respostacerta", "resposta", "gabarito")]
    if col_names:
        val = str(row[col_names[0]]).strip().upper()
        if val in ('A', 'B', 'C', 'D', 'E'):
            return val
        # If it's a number 1 to 5
        if val in ('1', '2', '3', '4', '5'):
            return chr(ord('A') + int(val) - 1)
            
    # Fallback to feedback text parsing
    return find_correct_alternative(row)

def inspect_elements(page):
    output_lines = []
    output_lines.append("="*50)
    output_lines.append("INSPEÇÃO DE ELEMENTOS NA PÁGINA ATUAL")
    output_lines.append("="*50)
    
    output_lines.append("\n--- Campos de Entrada (Input, Textarea, Contenteditable) ---")
    inputs = page.query_selector_all("input, textarea, [contenteditable='true']")
    for i, el in enumerate(inputs):
        try:
            tag = el.evaluate("el => el.tagName")
            type_attr = el.get_attribute("type") or ""
            id_attr = el.get_attribute("id") or ""
            val = el.evaluate("el => el.value") or el.inner_text() or ""
            placeholder = el.get_attribute("placeholder") or ""
            name_attr = el.get_attribute("name") or ""
            label_text = ""
            # Try to find associated label
            if id_attr:
                label_el = page.query_selector(f"label[for='{id_attr}']")
                if label_el:
                    label_text = label_el.inner_text()
            output_lines.append(f"[{i}] Tag: {tag} | Type: {type_attr} | ID: {id_attr} | Name: {name_attr} | Placeholder: '{placeholder}' | Label: '{label_text}' | Valor: '{val[:50]}'")
        except Exception as e:
            output_lines.append(f"[{i}] Erro ao inspecionar elemento: {e}")
            
    output_lines.append("\n--- Botões da Página ---")
    buttons = page.query_selector_all("button, input[type='button'], input[type='submit']")
    for i, btn in enumerate(buttons):
        try:
            tag = btn.evaluate("el => el.tagName")
            id_attr = btn.get_attribute("id") or ""
            text = (btn.inner_text() or btn.get_attribute("value") or "").strip().replace("\n", " ")
            title = btn.get_attribute("title") or ""
            aria = btn.get_attribute("aria-label") or ""
            output_lines.append(f"[{i}] Tag: {tag} | ID: {id_attr} | Text: '{text}' | Title: '{title}' | Aria-Label: '{aria}'")
        except Exception as e:
            output_lines.append(f"[{i}] Erro ao inspecionar botão: {e}")
            
    full_output = "\n".join(output_lines)
    print(full_output)
    
    try:
        with open("/home/hamilcar/Antigravity/inspection.txt", "w", encoding="utf-8") as f:
            f.write(full_output)
        print("\nMapeamento de DOM salvo em /home/hamilcar/Antigravity/inspection.txt")
    except Exception as e:
        print(f"Erro ao salvar arquivo de inspeção: {e}")

def fill_identificacao(page, val):
    print(f"- Preenchendo Identificação da questão: '{val}'...")
    try:
        res = page.evaluate(f"""(() => {{
            const el = document.getElementById('Questao_Nome') || document.querySelector('input[name="Questao.Nome"]');
            if (el) {{
                el.value = {json.dumps(val)};
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }}
            return false;
        }})()""")
        if res:
            print("  [Sucesso] Identificação preenchida via JS.")
            return True
    except Exception as e:
        print(f"  [Aviso] Erro preenchendo ID via JS: {e}")
        
    try:
        page.locator("#Questao_Nome").fill(val)
        return True
    except Exception as e:
        print(f"  [Aviso] Falha ao preencher ID por seletor exato: {e}")
        for label in ["Identificação da questão", "Identificação", "Identificacao", "Código", "Codigo", "ID da questão"]:
            loc = page.get_by_label(label, exact=False)
            if loc.count() > 0:
                loc.first.fill(val)
                return True
            loc = page.get_by_placeholder(label, exact=False)
            if loc.count() > 0:
                loc.first.fill(val)
                return True
        raise Exception("Não foi possível preencher o campo de Identificação da questão.")

def fill_palavra_chave(page, val):
    print(f"- Preenchendo Palavra-chave: '{val}'...")
    try:
        res = page.evaluate(f"""(() => {{
            const el = document.querySelector('input[name="PalavrasChave"]');
            if (el) {{
                el.value = {json.dumps(val)};
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }}
            return false;
        }})()""")
        if res:
            print("  [Sucesso] Palavra-chave preenchida via JS.")
            return True
    except Exception as e:
        print(f"  [Aviso] Erro preenchendo Palavra-chave via JS: {e}")
        
    try:
        page.locator("input[name='PalavrasChave']").fill(val)
        return True
    except Exception as e:
        print(f"  [Aviso] Falha ao preencher Palavra-chave por seletor exato: {e}")
        for label in ["Palavra chave", "Palavras-chave", "Palavra-chave", "Palavras chave", "Keywords", "Tags", "Tag"]:
            loc = page.get_by_label(label, exact=False)
            if loc.count() > 0:
                loc.first.fill(val)
                return True
            loc = page.get_by_placeholder(label, exact=False)
            if loc.count() > 0:
                loc.first.fill(val)
                return True
        raise Exception("Não foi possível preencher o campo de Palavra-chave.")

def select_tipo_questao(page, val):
    print(f"- Selecionando Tipo da questão: '{val}'...")
    js_code = f"""
    (() => {{
        const select = document.getElementById('Questao_IdTipoQuestao');
        if (!select) return false;
        const valLower = {json.dumps(val)}.toLowerCase();
        
        let matchValue = "";
        for (const opt of select.options) {{
            const txt = opt.text.toLowerCase();
            if (valLower.includes("complementação") || valLower.includes("completamento") || valLower.includes("completar")) {{
                if (txt.includes("complementação")) {{ matchValue = opt.value; break; }}
            }} else if (valLower.includes("múltipla") || valLower.includes("multipla") || valLower.includes("múltiplas") || valLower.includes("multiplas")) {{
                if (txt.includes("múltipla") || txt.includes("multipla")) {{ matchValue = opt.value; break; }}
            }} else if (valLower.includes("asserção") || valLower.includes("asserçao") || valLower.includes("assercao")) {{
                if (txt.includes("asserção")) {{ matchValue = opt.value; break; }}
            }} else if (valLower.includes("discursiva")) {{
                if (txt.includes("discursiva")) {{ matchValue = opt.value; break; }}
            }}
            
            if (valLower.includes(txt) || txt.includes(valLower)) {{
                matchValue = opt.value;
            }}
        }}
        
        if (matchValue) {{
            select.value = matchValue;
            select.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
        }}
        return false;
    }})()
    """
    res = page.evaluate(js_code)
    if res:
        print("  [Sucesso] Tipo selecionado.")
        return True
    
    print(f"  [Aviso] Não foi possível selecionar automaticamente o Tipo: '{val}'")
    input("Por favor, selecione o Tipo da Questão manualmente no navegador e pressione ENTER no terminal para continuar...")
    return False

def select_nivel_cognitivo(page, val):
    print(f"- Selecionando Nível cognitivo: '{val}'...")
    js_code = f"""
    (() => {{
        const select = document.getElementById('IdHabilidadeQuestao');
        if (!select) return false;
        const valLower = {json.dumps(val)}.toLowerCase();
        
        let matchValue = "";
        for (const opt of select.options) {{
            const txt = opt.text.toLowerCase();
            if (valLower.includes("reconhecimento") || valLower.includes("(re)conhecimento")) {{
                if (txt.includes("reconhecimento") || txt.includes("(re)conhecimento")) {{ matchValue = opt.value; break; }}
            }} else if (valLower.includes("compreensão") || valLower.includes("compreensao")) {{
                if (txt.includes("compreensão") || txt.includes("compreensao")) {{ matchValue = opt.value; break; }}
            }} else if (valLower.includes("aplicação") || valLower.includes("aplicacao")) {{
                if (txt.includes("aplicação") || txt.includes("aplicacao")) {{ matchValue = opt.value; break; }}
            }} else if (valLower.includes("análise") || valLower.includes("analise")) {{
                if (txt.includes("análise") || txt.includes("analise")) {{ matchValue = opt.value; break; }}
            }} else if (valLower.includes("síntese") || valLower.includes("sintese")) {{
                if (txt.includes("síntese") || txt.includes("sintese")) {{ matchValue = opt.value; break; }}
            }} else if (valLower.includes("julgamento")) {{
                if (txt.includes("julgamento")) {{ matchValue = opt.value; break; }}
            }}
            
            if (valLower.includes(txt) || txt.includes(valLower)) {{
                matchValue = opt.value;
            }}
        }}
        
        if (matchValue) {{
            select.value = matchValue;
            select.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
        }}
        return false;
    }})()
    """
    res = page.evaluate(js_code)
    if res:
        print("  [Sucesso] Nível cognitivo selecionado.")
        return True
        
    print(f"  [Aviso] Não foi possível selecionar automaticamente o Nível Cognitivo: '{val}'")
    input("Por favor, selecione o Nível Cognitivo manualmente no navegador e pressione ENTER no terminal para continuar...")
    return False

def fill_rich_text_editor(page, editor_id, content):
    """
    Fills a specific TinyMCE rich text editor by its ID, with fallback.
    """
    try:
        val_json = json.dumps(content)
        js_code = f"""
        (() => {{
            if (!window.tinymce) return false;
            const editor = window.tinymce.get('{editor_id}');
            if (!editor) return false;
            
            editor.setContent({val_json});
            editor.fire('change');
            editor.fire('input');
            
            // Sync to the native textarea
            const textarea = document.getElementById('{editor_id}');
            if (textarea) {{
                textarea.value = {val_json};
                textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
                textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            return true;
        }})()
        """
        res = page.evaluate(js_code)
        if res:
            return True
    except Exception as e:
        print(f"  [Debug TinyMCE] Erro no editor '{editor_id}': {e}")
        
    # Fallback to standard textarea filling
    try:
        target = page.locator(f"#{editor_id}")
        if target.count() > 0:
            target.first.scroll_into_view_if_needed()
            target.first.focus()
            target.first.fill(content)
            return True
    except Exception as e:
        print(f"  [Debug Textarea] Erro de fallback no editor '{editor_id}': {e}")
        
    return False

def remove_alternative_e(page):
    print("- Removendo a alternativa E...")
    try:
        page.locator("#btnRemoverAfirmativa").click()
        print("  [Sucesso] Alternativa E removida via botão ID #btnRemoverAfirmativa.")
        return True
    except Exception as e:
        print(f"  [Aviso] Falha ao clicar no botão de remover pelo ID: {e}")
        
    # Fallback to the text search
    if click_element_by_text(page, ["Remover alternativa", "Remover"], "Remover alternativa"):
        return True
        
    print("  [Aviso] Não foi possível clicar no botão de remover a alternativa E automaticamente.")
    input("Por favor, clique para remover/deletar a Alternativa E no navegador e pressione ENTER no terminal...")
    return True

def select_correct_answer_checkbox(page, letter):
    print(f"- Marcando checkbox para a alternativa correta '{letter}'...")
    index = ord(letter.upper()) - ord('A') # A=0, B=1, C=2, D=3
    name = f"Afirmativas[{index}].Verdadeira"
    
    try:
        res = page.evaluate(f"""(() => {{
            const radio = document.querySelector('input[name="Afirmativas[{index}].Verdadeira"]');
            if (radio) {{
                radio.click();
                radio.dispatchEvent(new Event('change', {{ bubbles: true }}));
                radio.dispatchEvent(new Event('click', {{ bubbles: true }}));
                return true;
            }}
            return false;
        }})()""")
        if res:
            print(f"  [Sucesso] Alternativa '{letter}' marcada como correta via JS.")
            return True
    except Exception as e:
        print(f"  [Aviso] Falha ao marcar checkbox via JS: {e}")
        
    try:
        page.locator(f"input[name='{name}']").click(force=True, timeout=3000)
        print(f"  [Sucesso] Alternativa '{letter}' marcada como correta (force click).")
        return True
    except Exception as e:
        print(f"  [Aviso] Falha ao marcar checkbox/radio pelo seletor '{name}': {e}")
        
    print(f"  [Aviso] Não foi possível marcar o checkbox da alternativa '{letter}' automaticamente.")
    input(f"Por favor, marque a alternativa {letter} como a resposta certa no navegador e pressione ENTER no terminal...")
    return True

def click_element_by_text(page, labels, name):
    for label in labels:
        btn = page.locator("button, a, span, div, label").filter(has_text=re.compile(f"^{label}$", re.IGNORECASE))
        if btn.count() > 0:
            btn.first.evaluate("el => el.click()")
            print(f"  [Sucesso] Elemento '{name}' clicado (busca exata).")
            return True
            
    for label in labels:
        btn = page.locator(f"button:has-text('{label}'), a:has-text('{label}'), span:has-text('{label}'), label:has-text('{label}')")
        if btn.count() > 0:
            btn.first.evaluate("el => el.click()")
            print(f"  [Sucesso] Elemento '{name}' clicado (busca parcial).")
            return True
            
    return False

def click_salvar_questao(page):
    print("- Clicando no botão 'Salvar questão'...")
    try:
        page.locator("#submitFormQuestao").click()
        print("  [Sucesso] Botão 'Salvar questão' clicado.")
        return True
    except Exception as e:
        print(f"  [Aviso] Falha ao salvar pelo ID #submitFormQuestao: {e}")
        
    if click_element_by_text(page, ["Salvar questão", "Salvar Questão", "Salvar"], "Salvar questão"):
        return True
    print("  [Aviso] Botão 'Salvar questão' não encontrado.")
    input("Por favor, clique em 'Salvar questão' no navegador e pressione ENTER no terminal...")
    return True

def click_visualizar_questao(page):
    print("- Clicando no botão 'Visualizar questão'...")
    try:
        page.locator("#btnGroupVisualizarQuestao").click()
        print("  [Sucesso] Botão 'Visualizar questão' clicado.")
        return True
    except Exception as e:
        print(f"  [Aviso] Falha ao clicar pelo ID #btnGroupVisualizarQuestao: {e}")
        
    if click_element_by_text(page, ["Visualizar questão", "Visualizar Questão", "Visualizar"], "Visualizar questão"):
        return True
    print("  [Aviso] Botão 'Visualizar questão' não encontrado.")
    input("Por favor, clique em 'Visualizar questão' no navegador e pressione ENTER no terminal...")
    return True

def click_digital(page):
    print("- Selecionando opção 'Digital'...")
    for selector in ["a:has-text('Digital')", "button:has-text('Digital')", "span:has-text('Digital')", ".dropdown-item:has-text('Digital')", "li:has-text('Digital')"]:
        loc = page.locator(selector)
        if loc.count() > 0:
            loc.first.click()
            print("  [Sucesso] Opção 'Digital' clicada.")
            return True
            
    # Heuristic JS search
    js_code = """
    (() => {
        const els = Array.from(document.querySelectorAll('a, button, span, li, div'));
        const target = els.find(el => el.innerText.trim().toLowerCase() === 'digital' && el.offsetWidth > 0);
        if (target) {
            target.click();
            return true;
        }
        return false;
    })()
    """
    if page.evaluate(js_code):
        print("  [Sucesso] Opção 'Digital' clicada via JS.")
        return True
        
    print("  [Aviso] Opção 'Digital' não encontrada automaticamente.")
    input("Por favor, clique na opção 'Digital' no navegador e pressione ENTER no terminal...")
    return True

def click_proximo(page):
    print("- Clicando no botão 'Próximo'...")
    try:
        page.locator("#buttonProximo").click()
        print("  [Sucesso] Botão 'Próximo' clicado.")
        return True
    except Exception as e:
        print(f"  [Aviso] Falha ao avançar pelo ID #buttonProximo: {e}")
        
    if click_element_by_text(page, ["Próximo", "Proximo", "Next", "Avançar"], "Próximo"):
        return True
    print("  [Aviso] Botão 'Próximo' não encontrado.")
    input("Por favor, clique em 'Próximo' no navegador e pressione ENTER no terminal...")
    return True

def handle_step_6(page):
    print("- Processando Passo 6 (Sugestões de correção)...")
    try:
        page.wait_for_timeout(500)
        for attempt in range(15):
            cleared = page.evaluate("""() => {
                const allIgnoreBtns = Array.from(document.querySelectorAll('button, a, input, .btn, span.btn')).filter(el => {
                    const txt = (el.innerText || el.textContent || el.value || '').trim().toLowerCase();
                    const onclick = (el.getAttribute('onclick') || '').toLowerCase();
                    return (txt.includes('ignorar todas') || txt.includes('ignorar tudo') || onclick.includes('ignorartodas')) && el.offsetWidth > 0 && el.offsetHeight > 0;
                });
                if (allIgnoreBtns.length > 0) {
                    try { allIgnoreBtns[0].click(); } catch(e) {}
                    return "all";
                }
                
                const ignoreBtns = Array.from(document.querySelectorAll('button, a, input, .btn, span.btn')).filter(el => {
                    const txt = (el.innerText || el.textContent || el.value || '').trim().toLowerCase();
                    const onclick = (el.getAttribute('onclick') || '').toLowerCase();
                    const id = (el.id || '').toLowerCase();
                    const isIgnorar = (txt === 'ignorar' || txt.includes('ignorar') || onclick.includes('ignorar') || id.includes('ignorar'));
                    return isIgnorar && el.offsetWidth > 0 && el.offsetHeight > 0;
                });
                if (ignoreBtns.length > 0) {
                    try { ignoreBtns[0].click(); } catch(e) {}
                    return ignoreBtns.length;
                }
                return 0;
            }""")
            if not cleared or cleared == 0:
                break
            page.wait_for_timeout(400)
            
        page.evaluate("""() => {
            const saveBtns = Array.from(document.querySelectorAll('button, a, input, .btn')).filter(el => {
                const txt = (el.innerText || el.textContent || el.value || '').trim().toLowerCase();
                const id = (el.id || '').toLowerCase();
                return (txt === 'salvar' || id.includes('salvarcorrecoes')) && !id.includes('submitformquestao') && el.offsetWidth > 0 && el.offsetHeight > 0;
            });
            if (saveBtns.length > 0) {
                try { saveBtns[0].click(); } catch(e) {}
            }
        }""")
        page.wait_for_timeout(600)
    except Exception as e:
        print(f"  [Erro] Falha ao processar botões 'Ignorar': {e}")
        
    return click_proximo(page)

def finish_question_flow(page, is_last):
    if is_last:
        print("- Finalizando última questão. Clicando em 'Enviar'...")
        try:
            page.locator("#btnEnviarQuestao").click()
            print("  [Sucesso] Botão 'Enviar' clicado.")
            return True
        except Exception as e:
            print(f"  [Aviso] Falha pelo ID #btnEnviarQuestao: {e}")
            
        if click_element_by_text(page, ["Enviar", "Finalizar", "Submit", "Send"], "Enviar"):
            return True
        print("  [Aviso] Botão 'Enviar' não encontrado.")
        input("Por favor, clique em 'Enviar' no navegador e pressione ENTER no terminal...")
        return True
    else:
        print("- Clicando em 'Enviar e criar nova questão com os mesmos conteúdo e disciplinas'...")
        try:
            page.locator("#btnEnviarQuestaoCriarNovaMesmosParametros").click()
            print("  [Sucesso] Botão 'Enviar e criar...' clicado.")
            return True
        except Exception as e:
            print(f"  [Aviso] Falha pelo ID #btnEnviarQuestaoCriarNovaMesmosParametros: {e}")
            
        label = "Enviar e criar nova questão com os mesmos conteúdo e disciplinas"
        if click_element_by_text(page, [label, "Enviar e criar nova", "criar nova questão com os mesmos"], "Enviar e criar nova..."):
            return True
        print("  [Aviso] Botão 'Enviar e criar...' não encontrado.")
        input("Por favor, clique no botão para Enviar e criar nova questão e pressione ENTER no terminal...")
        return True

def run_insertion_for_row(page, row, is_last, delay=1.0):
    print(f"\n=======================================================")
    print(f" INSERINDO QUESTÃO: {row.get('Identificação da questão')}")
    print(f"=======================================================")
    
    # PASSO 4 - Elabora a Questão
    # 1. Identificação
    fill_identificacao(page, str(row.get('Identificação da questão', '')))
    time.sleep(delay)
    
    # 2. Palavras-chave
    fill_palavra_chave(page, str(row.get('Palavra chave', '')))
    time.sleep(delay)
    
    # 3. Tipo da Questão
    select_tipo_questao(page, str((row.get('Tipo de Questão') or row.get('Tipo da questão', ''))))
    time.sleep(delay)
    
    # 4. Nível Cognitivo
    select_nivel_cognitivo(page, str(row.get('Nível cognitivo', '')))
    time.sleep(delay)
    
    # 5. Texto da Questão (Editor 'TextoQuestao')
    print("- Preenchendo Texto da Questão...")
    fill_rich_text_editor(page, 'TextoQuestao', str(row.get('Texto da Questão', '')))
    time.sleep(delay)
    
    # 6. Alternativas A, B, C, D (Editores TextoAfirmativaA a TextoAfirmativaD)
    for letter in ['A', 'B', 'C', 'D']:
        col = f"Alternativa {letter}"
        editor_id = f"TextoAfirmativa{letter}"
        print(f"- Preenchendo {col}...")
        fill_rich_text_editor(page, editor_id, str(row.get(col, '')))
        time.sleep(delay)
        
    # 7. Remover Alternativa E
    remove_alternative_e(page)
    time.sleep(delay)
    
    # 8. MarcarCheckbox da Resposta Certa
    correct_letter = extract_correct_answer_letter(row)
    select_correct_answer_checkbox(page, correct_letter)
    time.sleep(delay)
    
    # 9. Inserir Feedback (Editor 'TextoFeedbackQuestao')
    print("- Preenchendo Feedback...")
    fill_rich_text_editor(page, 'TextoFeedbackQuestao', str(row.get('Feedback da questão', '')))
    time.sleep(delay)
    
    # 10. Salvar Questão
    click_salvar_questao(page)
    time.sleep(delay + 1.0)
    
    # 11. Visualizar Questão
    click_visualizar_questao(page)
    time.sleep(delay + 1.0)
    
    # 12. Clicar em Digital
    click_digital(page)
    time.sleep(delay)
    
    # 13. Clicar em Próximo
    click_proximo(page)
    time.sleep(delay + 1.5)
    
    # PASSO 5 - Referência Bibliográficas
    print("\n--- PASSO 5 - Referência Bibliográficas ---")
    click_proximo(page)
    time.sleep(delay + 1.5)
    
    # PASSO 6 - Sugestões de correção
    print("\n--- PASSO 6 - Sugestões de correção ---")
    handle_step_6(page)
    time.sleep(delay + 2.0)
    
    # PASSO 7 - Finalização (Enviar ou Criar Nova)
    finish_question_flow(page, is_last)
    time.sleep(delay + 3.0) # wait for page refresh
    
    print(f"\n[Sucesso] Questão '{row.get('Identificação da questão')}' concluída!")

def main():
    print("Iniciando assistente de automação...")
    
    # Load sheet data
    df, loaded_path = load_data()
    if df is None:
        print("Finalizando porque nenhuma planilha foi carregada.")
        return
        
    with sync_playwright() as p:
        user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"
        print(f"Abrindo navegador Chromium (dados salvos em {user_data_dir})...")
        context = p.chromium.launch_persistent_context(user_data_dir, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        
        # Navigate to login page
        login_url = "https://avauni.grupoa.education/plataforma/auth/signin"
        print(f"Navegando para a página de login: {login_url}")
        page.goto(login_url)
        
        print("\n" + "="*80)
        print(" AÇÃO REQUERIDA NO NAVEGADOR:")
        print(" 1. Faça login na plataforma manualmente.")
        print(" 2. Vá até a tela do 'Passo 4 - Elabora a Questão'.")
        print(" 3. Retorne a este terminal para iniciar a inserção das questões.")
        print("="*80)
        
        delay_actions = 1.0
        
        while True:
            print("\nComandos:")
            print(f"  run       : Insere automaticamente as {len(df)} questões de: {os.path.basename(loaded_path)}")
            print("  test      : Insere apenas a 1ª questão como teste")
            print("  inspect   : Analisa e lista os elementos e botões da página atual")
            print("  load      : Carrega outro arquivo Excel")
            print("  set-delay : Ajusta o delay entre ações (atual: {}s)".format(delay_actions))
            print("  js        : Executa um script JS arbitrário na página")
            print("  exit      : Encerra o script")
            
            cmd = input("\nDigite um comando: ").strip().lower()
            
            # Atualiza a referência para a aba ativa do Elaborador
            page = get_active_page(context)
            if page:
                try:
                    print(f"[Aba Ativa] URL: {page.url}")
                except Exception as e:
                    print(f"[Aba Ativa] Erro ao obter URL: {e}")
            else:
                print("[Aba Ativa] Nenhuma aba encontrada.")
                
            if cmd == 'exit':
                print("Fechando navegador e saindo...")
                break
                
            elif cmd == 'inspect':
                inspect_elements(page)
                
            elif cmd == 'load':
                new_df, new_path = load_data()
                if new_df is not None:
                    df = new_df
                    loaded_path = new_path
                    
            elif cmd == 'set-delay':
                try:
                    delay_actions = float(input("Novo delay em segundos (ex: 1.5): "))
                    print(f"Delay alterado para {delay_actions}s")
                except ValueError:
                    print("Valor inválido.")
                    
            elif cmd == 'js':
                code = input("Código JS para rodar: ")
                try:
                    res = page.evaluate(code)
                    print("Resultado:", res)
                except Exception as e:
                    print("Erro ao executar JS:", e)
                    
            elif cmd == 'test':
                if df.empty:
                    print("Nenhuma questão carregada.")
                    continue
                row = df.iloc[0]
                try:
                    print("\nRodando teste da 1ª questão...")
                    print("Aguardando selector '#Questao_Nome' na página...")
                    try:
                        page.wait_for_selector("#Questao_Nome", timeout=3000)
                    except Exception:
                        print("  [Aviso] Seletor '#Questao_Nome' não apareceu em 3s. Prosseguindo...")
                    run_insertion_for_row(page, row, is_last=True, delay=delay_actions)
                    print("\nTeste finalizado! Verifique o estado da página.")
                except Exception as e:
                    print(f"\n[Erro] Falha ao rodar teste: {e}")
                    
            elif cmd == 'run':
                if df.empty:
                    print("Nenhuma questão carregada.")
                    continue
                    
                start_idx = 0
                try:
                    idx_input = input(f"A partir de qual índice de questão deseja iniciar? (0 a {len(df)-1}, padrão: 0): ").strip()
                    if idx_input:
                        start_idx = int(idx_input)
                except ValueError:
                    print("Índice inválido. Começando do 0.")
                    
                confirm = input(f"Confirmar inserção das questões a partir do índice {start_idx}? (s/n): ").strip().lower()
                if confirm != 's':
                    print("Operação cancelada.")
                    continue
                    
                print(f"Iniciando preenchimento automático das questões...")
                print("Aguardando selector '#Questao_Nome' na página...")
                try:
                    page.wait_for_selector("#Questao_Nome", timeout=3000)
                except Exception:
                    print("  [Aviso] Seletor '#Questao_Nome' não apareceu em 3s. Prosseguindo...")
                success_count = 0
                for i in range(start_idx, len(df)):
                    row = df.iloc[i]
                    is_last = (i == len(df) - 1)
                    
                    try:
                        run_insertion_for_row(page, row, is_last=is_last, delay=delay_actions)
                        success_count += 1
                        print(f"Sucesso: Questão {i} concluída. ({success_count} inseridas nesta sessão)")
                    except Exception as e:
                        print(f"\n[Erro] Erro na questão de índice {i}: {e}")
                        ans = input("Deseja continuar para a próxima questão da planilha? (s/n): ").strip().lower()
                        if ans != 's':
                            break
                            
                print(f"\nInserção concluída. Total de questões inseridas com sucesso: {success_count}.")
                
        context.close()

if __name__ == "__main__":
    main()
