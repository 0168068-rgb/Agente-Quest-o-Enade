import os
import sys
import time
import re
import json
import glob
import pandas as pd
from playwright.sync_api import sync_playwright

# Global control flags updated by JavaScript callbacks in the browser
start_automation_requested = False
test_automation_requested = False
requested_start_idx = 0
user_action = None
current_df = None
current_df_path = None
is_paused = False

def on_start(start_idx):
    global start_automation_requested, requested_start_idx
    start_automation_requested = True
    requested_start_idx = int(start_idx)
    print(f"\n[Evento] Início de inserção solicitado a partir do índice {start_idx}")

def on_test(start_idx):
    global test_automation_requested, requested_start_idx
    test_automation_requested = True
    requested_start_idx = int(start_idx)
    print(f"\n[Evento] Teste de questão solicitado no índice {start_idx}")

def on_user_action(action):
    global user_action
    user_action = action
    print(f"[Evento] Ação do usuário: {action}")

def get_active_page(context):
    # First, look for a page that actually has the editor fields and is visible
    for p in reversed(context.pages):
        try:
            if p.locator("#Questao_Nome").count() > 0 and p.locator("#Questao_Nome").is_visible():
                return p
        except:
            pass
            
    # Second, look for a page with 'avalia' or 'Elaborador' in the URL (newest first)
    for p in reversed(context.pages):
        try:
            url = p.url
            if "avalia" in url or "Elaborador" in url:
                return p
        except:
            pass
            
    # Third, look for any other page in the domains (newest first)
    for p in reversed(context.pages):
        try:
            url = p.url
            if any(domain in url for domain in ["plataforma", "avauni", "grupoa"]):
                return p
        except:
            pass
            
    if context.pages:
        return context.pages[-1]
    return None

def load_data(excel_path=None):
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
        
    if not excel_path:
        path_input = input("Digite o caminho completo/nome do arquivo de planilha (ou pressione Enter para ver a lista): ").strip()
        if path_input:
            excel_path = path_input
            
    if not excel_path:
        all_files = []
        for root, dirs, files in os.walk("/home/hamilcar/Antigravity"):
            dirs[:] = [d for d in dirs if d not in ["venv", "playwright_user_data", ".git", "__pycache__"] and not d.startswith(".")]
            for f in files:
                if f.endswith((".xlsx", ".xls", ".csv")):
                    all_files.append(os.path.join(root, f))
                    
        if all_files:
            print("\nArquivos de planilhas encontrados no workspace:")
            for idx, f in enumerate(all_files):
                rel_path = os.path.relpath(f, "/home/hamilcar/Antigravity")
                print(f"  [{idx}] {rel_path}")
            print(f"  [{len(all_files)}] Outro (digitar caminho completo)")
            
            try:
                choice = input(f"Selecione o arquivo (0 a {len(all_files)}, padrão: 0): ").strip()
                if not choice:
                    excel_path = all_files[0]
                elif int(choice) == len(all_files):
                    excel_path = input("Digite o caminho completo para o arquivo Excel/CSV: ").strip()
                else:
                    excel_path = all_files[int(choice)]
            except Exception:
                excel_path = all_files[0]
        else:
            excel_path = input("Nenhuma planilha encontrada. Digite o caminho completo para o arquivo Excel/CSV: ").strip()
            
    if not excel_path or not os.path.exists(excel_path):
        print(f"Erro: Arquivo não encontrado em: {excel_path}")
        return None, None
        
    print(f"Carregando planilha: {excel_path}...")
    try:
        if excel_path.endswith('.csv'):
            df = pd.read_csv(excel_path)
        else:
            df = pd.read_excel(excel_path)
        df = df.fillna("")
        print(f"Sucesso: {len(df)} questões carregadas.")
        return df, excel_path
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return None, None

def find_correct_alternative(row):
    feedback = str(row.get('Feedback da questão', '')).strip().lower()
    alt_a = str(row.get('Alternativa A', '')).strip().lower()
    alt_b = str(row.get('Alternativa B', '')).strip().lower()
    alt_c = str(row.get('Alternativa C', '')).strip().lower()
    alt_d = str(row.get('Alternativa D', '')).strip().lower()
    
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
    
    # Try exact match at the start
    for letter, text in alts.items():
        if not text:
            continue
        text_clean = text.rstrip('.')
        if feedback_clean.startswith(text_clean):
            return letter
            
    # Fallback to substring in the first part of feedback
    for letter, text in alts.items():
        if not text:
            continue
        text_clean = text.rstrip('.')
        if text_clean in feedback_clean[:150]:
            return letter
            
    # Regex fallback for "Alternativa X"
    match = re.search(r'alternativa\s+([a-d])', feedback, re.IGNORECASE)
    if match:
        return match.group(1).upper()
        
    print(f"Aviso: Não foi possível deduzir a resposta certa pelo feedback para a questão.")
    return 'A'

def extract_correct_answer_letter(row):
    # Procura por colunas explícitas
    possible_cols = [
        "resposta certa", "resposta_certa", "respostacerta", "resposta",
        "gabarito", "questão correta", "questao correta", "questão_correta", "questaocorreta"
    ]
    col_names = [col for col in row.index if str(col).strip().lower() in possible_cols]
    if col_names:
        val = str(row[col_names[0]]).strip().upper()
        if val in ('A', 'B', 'C', 'D', 'E'):
            return val
        if val in ('1', '2', '3', '4', '5'):
            return chr(ord('A') + int(val) - 1)
            
    # Fallback para extrair do feedback
    return find_correct_alternative(row)

# DOM Actions with exact selectors
def fill_identificacao(page, val):
    print(f"- Preenchendo Identificação: '{val}'...")
    try:
        page.locator("#Questao_Nome").fill(val)
        return
    except Exception as e:
        print(f"  [Aviso] Playwright fill falhou: {e}. Usando fallback JS...")
        
    try:
        page.evaluate(f"""(() => {{
            const el = document.getElementById('Questao_Nome') || document.querySelector('input[name="Questao.Nome"]');
            if (el) {{
                el.value = {json.dumps(val)};
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }}
            return false;
        }})()""")
    except:
        pass

def fill_palavra_chave(page, val):
    print(f"- Preenchendo Palavra-chave: '{val}'...")
    try:
        page.locator("input[name='PalavrasChave']").fill(val, timeout=1000)
        return
    except Exception as e:
        print(f"  [Aviso] Playwright fill falhou: {e}. Usando fallback JS...")
        
    try:
        page.evaluate(f"""(() => {{
            const el = document.querySelector('input[name="PalavrasChave"]');
            if (el) {{
                el.value = {json.dumps(val)};
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return true;
            }}
            return false;
        }})()""")
    except:
        pass

def select_tipo_questao(page, val):
    print(f"- Selecionando Tipo da questão: '{val}'...")
    try:
        options = page.evaluate("() => Array.from(document.getElementById('Questao_IdTipoQuestao').options).map(o => ({text: o.text, value: o.value}))")
        print(f"  [DEBUG] Opções de tipo de questão: {options}")
    except Exception as e:
        print(f"  [Aviso] Não foi possível obter opções: {e}")
        options = []
        
    val_lower = val.lower().strip()
    match_value = ""
    
    if "complementação" in val_lower or "complementacao" in val_lower or "completamento" in val_lower or "simples" in val_lower:
        opt = next((o for o in options if "complementação" in o['text'].lower() or "complementacao" in o['text'].lower()), None)
        if opt:
            match_value = opt['value']
    elif "múltipla escolha" in val_lower or "multipla escolha" in val_lower:
        opt = next((o for o in options if "múltipla escolha" in o['text'].lower() or "multipla escolha" in o['text'].lower()), None)
        if opt:
            match_value = opt['value']
        else:
            opt_fallback = next((o for o in options if "múltipla" in o['text'].lower() or "multipla" in o['text'].lower()), None)
            if opt_fallback:
                match_value = opt_fallback['value']
    elif "resposta múltipla" in val_lower or "resposta multipla" in val_lower or "múltiplas" in val_lower or "multiplas" in val_lower or "resposta múltiplas" in val_lower or "resposta multiplas" in val_lower:
        opt = next((o for o in options if "resposta múltipla" in o['text'].lower() or "resposta multipla" in o['text'].lower()), None)
        if opt:
            match_value = opt['value']
    elif "associação" in val_lower or "associacao" in val_lower:
        opt = next((o for o in options if "associação" in o['text'].lower() or "associacao" in o['text'].lower()), None)
        if opt:
            match_value = opt['value']
    elif "asserção" in val_lower or "assercao" in val_lower or "razão" in val_lower or "razao" in val_lower:
        opt = next((o for o in options if "asserção" in o['text'].lower() or "assercao" in o['text'].lower() or "razão" in o['text'].lower()), None)
        if opt:
            match_value = opt['value']
    elif "discursiva" in val_lower or "discursivo" in val_lower:
        opt = next((o for o in options if "discursiva" in o['text'].lower() or "discursivo" in o['text'].lower()), None)
        if opt:
            match_value = opt['value']
            
    if not match_value:
        for o in options:
            t = o['text'].lower()
            if val_lower in t or t in val_lower:
                match_value = o['value']
                break
                
    if not match_value:
        match_value = "60"

    if match_value:
        try:
            page.locator("#Questao_IdTipoQuestao").select_option(value=match_value)
            print(f"  [Sucesso] Tipo selecionado nativamente (ID: {match_value}).")
            return True
        except Exception as e:
            print(f"  [Aviso] Falha ao selecionar nativamente: {e}. Usando fallback JS...")
            
        try:
            page.evaluate(f"""(() => {{
                const select = document.getElementById('Questao_IdTipoQuestao');
                if (select) {{
                    select.value = "{match_value}";
                    select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return true;
                }}
                return false;
            }})()""")
            print(f"  [Sucesso] Tipo selecionado via JS (ID: {match_value}).")
            return True
        except Exception as js_err:
            print(f"  [Erro JS] {js_err}")
            
    raise Exception(f"Não foi possível selecionar o Tipo: '{val}'")

def select_nivel_cognitivo(page, val):
    print(f"- Selecionando Nível cognitivo: '{val}'...")
    try:
        options = page.evaluate("() => Array.from(document.getElementById('IdHabilidadeQuestao').options).map(o => ({text: o.text, value: o.value}))")
    except Exception as e:
        print(f"  [Aviso] Não foi possível obter opções: {e}")
        options = []
        
    val_lower = val.lower().strip()
    match_value = ""
    
    for o in options:
        txt = o['text'].lower()
        if "reconhecimento" in val_lower or "(re)conhecimento" in val_lower:
            if "reconhecimento" in txt or "(re)conhecimento" in txt:
                match_value = o['value']
                break
        elif "compreensão" in val_lower or "compreensao" in val_lower:
            if "compreensão" in txt or "compreensao" in txt:
                match_value = o['value']
                break
        elif "aplicação" in val_lower or "aplicacao" in val_lower:
            if "aplicação" in txt or "aplicacao" in txt:
                match_value = o['value']
                break
        elif "análise" in val_lower or "analise" in val_lower:
            if "análise" in txt or "analise" in txt:
                match_value = o['value']
                break
        elif "síntese" in val_lower or "sintese" in val_lower:
            if "síntese" in txt or "sintese" in txt:
                match_value = o['value']
                break
        elif "julgamento" in val_lower:
            if "julgamento" in txt:
                match_value = o['value']
                break
                
        if val_lower in txt or txt in val_lower:
            match_value = o['value']
            
    if match_value:
        try:
            page.locator("#IdHabilidadeQuestao").select_option(value=match_value)
            print(f"  [Sucesso] Nível cognitivo selecionado nativamente (ID: {match_value}).")
            return True
        except Exception as e:
            print(f"  [Aviso] Falha ao selecionar nativamente: {e}. Usando fallback JS...")
            
        try:
            page.evaluate(f"""(() => {{
                const select = document.getElementById('IdHabilidadeQuestao');
                if (select) {{
                    select.value = "{match_value}";
                    select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return true;
                }}
                return false;
            }})()""")
            print(f"  [Sucesso] Nível cognitivo selecionado via JS (ID: {match_value}).")
            return True
        except Exception as js_err:
            print(f"  [Erro JS] {js_err}")
            
    raise Exception(f"Não foi possível selecionar o Nível Cognitivo: '{val}'")

def text_to_html(text):
    """Convert plain text (from Excel cells) to HTML for TinyMCE.
    - Each line becomes a <p> paragraph without extra blank lines
    """
    if not text or not str(text).strip():
        return "<p><br></p>"
    
    # Normalize line endings (\r\n or \r → \n)
    text = str(text).replace('\r\n', '\n').replace('\r', '\n')
    
    lines = text.split('\n')
    html_parts = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            # Escape HTML special characters in the content
            escaped = (stripped
                       .replace('&', '&amp;')
                       .replace('<', '&lt;')
                       .replace('>', '&gt;'))
            html_parts.append(f"<p>{escaped}</p>")
    
    return "".join(html_parts) if html_parts else "<p><br></p>"

def fill_rich_text_editor(page, editor_id, content):
    print(f"- Preenchendo Rich Text Editor '{editor_id}'...")
    
    # Check if the element exists in the DOM at all
    exists = page.evaluate(f"""() => {{
        return document.getElementById('{editor_id}') !== null;
    }}""")
    if not exists:
        print(f"  [Info] Elemento '{editor_id}' não existe no DOM. Pulando.")
        return
        
    # Convert plain text (with \n) to HTML paragraphs for TinyMCE
    html_content = text_to_html(content)
    
    # Wait for TinyMCE to initialize for this editor_id
    for _ in range(30):
        is_ready = page.evaluate(f"""() => {{
            return typeof window.tinymce !== 'undefined' && 
                   window.tinymce.get('{editor_id}') !== null;
        }}""")
        if is_ready:
            break
        page.wait_for_timeout(150)
        
    try:
        val_json = json.dumps(html_content)
        js_code = f"""
        (() => {{
            if (!window.tinymce) return false;
            const editor = window.tinymce.get('{editor_id}');
            if (!editor) return false;
            
            editor.setContent({val_json});
            editor.save();
            editor.fire('change');
            editor.fire('input');
            
            const textarea = document.getElementById('{editor_id}');
            if (textarea) {{
                textarea.value = {val_json};
                textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
                textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
            return true;
        }})()
        """
        if page.evaluate(js_code):
            return
    except Exception as e:
        print(f"  [TinyMCE] Erro: {e}")
        
    # Fallback to direct textarea filling (use html_content here too)
    print(f"  [Aviso] TinyMCE indisponível para '{editor_id}'. Usando fallback direto no textarea...")
    page.locator(f"#{editor_id}").scroll_into_view_if_needed()
    page.locator(f"#{editor_id}").fill(html_content)


def remove_alternative_e(page):
    print("- Removendo a alternativa E...")
    # Check if Alternative E is visible in the DOM
    alternative_e_exists = page.evaluate("""() => {
        const el = document.getElementById('TextoAfirmativaE') || 
                   document.querySelector('[name*="Afirmativas[4]"]') ||
                   document.querySelector('[id*="AfirmativaE"]');
        const btn = document.getElementById('btnRemoverAfirmativa');
        const isElVisible = el && el.offsetWidth > 0 && el.offsetHeight > 0;
        const isBtnVisible = btn && btn.offsetWidth > 0 && btn.offsetHeight > 0;
        return !!(isElVisible || isBtnVisible);
    }""")
    
    if not alternative_e_exists:
        print("  [Info] Alternativa E não detectada ou já removida (ou invisível). Pulando remoção.")
        return

    # Try normal Playwright click first
    try:
        page.locator("#btnRemoverAfirmativa").click(timeout=2000)
        print("  [Sucesso] Botão #btnRemoverAfirmativa clicado via Playwright.")
        return
    except Exception as e:
        print(f"  [Aviso] Playwright click em #btnRemoverAfirmativa falhou: {e}. Usando fallback JS...")

    # Try programmatic JS click as fallback
    try:
        clicked = page.evaluate("""() => {
            const btn = document.getElementById('btnRemoverAfirmativa');
            if (btn) {
                btn.click();
                return true;
            }
            return false;
        }""")
        if clicked:
            print("  [Sucesso] Botão #btnRemoverAfirmativa clicado via JS.")
            return
    except Exception as e:
        print(f"  [Erro ao clicar #btnRemoverAfirmativa via JS] {e}")
        
    # Heuristic via JS
    js_code = """
    (() => {
        // 1. Try to find by onclick containing "remover" or "Excluir" and index 4 (Alternative E)
        const btnOnclick = document.querySelector('[onclick*="remover"][onclick*="4"]') ||
                           document.querySelector('[onclick*="Excluir"][onclick*="4"]') ||
                           document.querySelector('[onclick*="excluir"][onclick*="4"]');
        if (btnOnclick) {
            btnOnclick.click();
            return "onclick_4";
        }
        
        // 2. Try to find all visible remove buttons
        const removeEls = Array.from(document.querySelectorAll('button, a, span, i'))
            .filter(el => {
                const str = (el.id + ' ' + el.className + ' ' + (el.getAttribute('onclick') || '') + ' ' + el.innerText).toLowerCase();
                return str.includes('remover') || str.includes('remove') || str.includes('trash') || str.includes('excluir');
            })
            .filter(el => el.offsetWidth > 0 && el.offsetHeight > 0);
            
        if (removeEls.length > 0) {
            removeEls[removeEls.length - 1].click();
            return "last_remove_el";
        }
        return null;
    })()
    """
    try:
        res = page.evaluate(js_code)
        if res:
            print(f"  [Sucesso] Alternativa E removida via heurística JS ({res}).")
            return
    except Exception as e:
        print(f"  [Erro JS] {e}")

    # Fallback to text search
    for btn_text in ["Remover alternativa", "Remover", "Remover afirmativa", "Excluir"]:
        try:
            btn = page.locator("button, a").filter(has_text=re.compile(f"^{btn_text}$", re.IGNORECASE))
            if btn.count() > 0:
                btn.first.click(timeout=1500)
                print("  [Sucesso] Botão clicado via texto fallback.")
                return
        except:
            pass

    raise Exception("Não foi possível clicar no botão de remover a alternativa E automaticamente. Por favor, remova-a manualmente e clique 'Continuar' no painel.")

def select_correct_answer_checkbox(page, letter):
    print(f"- Marcando checkbox para a alternativa correta '{letter}'...")
    
    # Check if there are any radio or checkbox inputs for alternatives in the DOM
    has_inputs = page.evaluate("""() => {
        return document.querySelectorAll('input[type="radio"], input[type="checkbox"]').length > 0;
    }""")
    if not has_inputs:
        print("  [Info] Nenhum campo de alternativa (radio/checkbox) encontrado. Pulando marcação de resposta correta.")
        return
        
    index = ord(letter.upper()) - ord('A')  # A=0, B=1, C=2, D=3
    
    js_code = f"""
    (() => {{
        const selector = `input[name="Afirmativas[{index}].Verdadeira"]`;
        const input = document.querySelector(selector);
        
        if (typeof $ !== 'undefined' && $.fn && $.fn.iCheck) {{
            $(selector).iCheck('check');
            return "icheck_jquery";
        }}
        
        if (input) {{
            input.checked = true;
            input.dispatchEvent(new Event('change', {{ bubbles: true }}));
            input.dispatchEvent(new Event('click', {{ bubbles: true }}));
            const wrapper = input.closest('.iradio_flat-green, .iradio_square-green, .iradio_flat, div[class*="iradio"]');
            const helper = wrapper ? wrapper.querySelector('.iCheck-helper') : null;
            if (helper) {{
                helper.click();
            }} else {{
                input.click();
            }}
            return "exact_name";
        }}
        
        const list = Array.from(document.querySelectorAll('input[type="radio"], input[type="checkbox"]'))
            .filter(el => {{
                const name = (el.name || '').toLowerCase();
                return name.includes('verdadeira') || name.includes('correta') || name.includes('resposta') || name.includes('afirmativa');
            }});
        if (list.length > {index}) {{
            const radio = list[{index}];
            radio.checked = true;
            radio.dispatchEvent(new Event('change', {{ bubbles: true }}));
            radio.dispatchEvent(new Event('click', {{ bubbles: true }}));
            const wrapper = radio.closest('.iradio_flat-green, .iradio_square-green, .iradio_flat, div[class*="iradio"]');
            const helper = wrapper ? wrapper.querySelector('.iCheck-helper') : null;
            if (helper) {{
                helper.click();
            }} else {{
                radio.click();
            }}
            return "index_list";
        }}
        return null;
    }})()
    """
    try:
        res = page.evaluate(js_code)
        if res:
            print(f"  [Sucesso] Marcado checkbox via JS ({res}).")
            return
    except Exception as e:
        print(f"  [Erro JS ao marcar checkbox] {e}")
        
    # Fallback Playwright click
    name = f"Afirmativas[{index}].Verdadeira"
    try:
        page.locator(f"input[name='{name}']").evaluate("el => { if (el.parentNode) el.parentNode.click(); else el.click(); }")
    except:
        page.locator(f"input[name='{name}']").click(force=True)

def click_salvar_questao(page, row=None):
    try:
        page.evaluate("() => document.querySelectorAll('.ui-pnotify, .sweet-alert, .swal2-container').forEach(el => el.remove())")
    except:
        pass
    print("- Clicando em 'Salvar questão'...")
    if row is not None:
        try:
            # Check and correct if they were reset
            tipo_val = str(row.get('Tipo de Questão') or row.get('Tipo da questão', ''))
            hab_val = str(row.get('Nível cognitivo', ''))
            
            # Check current select values
            current_tipo = page.evaluate("() => document.getElementById('Questao_IdTipoQuestao')?.value")
            current_hab = page.evaluate("() => document.getElementById('IdHabilidadeQuestao')?.value")
            
            if not current_tipo or current_tipo == "0":
                print("  [Aviso] Tipo da questão foi resetado para 0! Re-selecionando...")
                select_tipo_questao(page, tipo_val)
                
            if not current_hab or current_hab == "0":
                print("  [Aviso] Nível cognitivo foi resetado para 0! Re-selecionando...")
                select_nivel_cognitivo(page, hab_val)
        except Exception as check_e:
            print(f"  [Aviso] Erro no double-check dos dropdowns: {check_e}")

    try:
        btns = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('button, a, input[type="submit"], input[type="button"]')).map(el => ({
                tag: el.tagName,
                id: el.id,
                className: el.className,
                text: el.innerText.trim(),
                value: el.value,
                onclick: el.getAttribute('onclick'),
                type: el.getAttribute('type')
            }));
        }""")
        print("  [DEBUG] Botões na página:")
        for b in btns:
            if b['text'] or b['id'] or b['value']:
                print(f"    - Tag: {b['tag']}, ID: {b['id']}, Class: {b['className']}, Text: '{b['text']}', Value: '{b['value']}', Onclick: '{b['onclick']}', Type: '{b['type']}'")
    except Exception as e:
        print(f"  [DEBUG Erro listing buttons] {e}")

    js_code = """
    (() => {
        let btn = document.getElementById('submitFormQuestao');
        if (btn && btn.offsetWidth > 0) {
            btn.click();
            return "id_submit";
        }
        const btns = Array.from(document.querySelectorAll('button, a, input[type="submit"]'));
        const salvar = btns.find(b => {
            const text = b.innerText.toLowerCase().trim();
            return text === 'salvar questão' || text === 'salvar questao' || (text.includes('salvar') && text.includes('quest'));
        });
        if (salvar) {
            salvar.click();
            return "text_salvar";
        }
        return null;
    })()
    """
    try:
        res = page.evaluate(js_code)
        if res:
            print(f"  [Sucesso] Botão 'Salvar questão' clicado via JS ({res}).")
            return
    except Exception as e:
        print(f"  [Erro JS ao salvar] {e}")

    try:
        page.locator("#submitFormQuestao").click(timeout=3000)
        return
    except:
        pass
        
    for txt in ["Salvar questão", "Salvar Questão", "Salvar"]:
        btn = page.locator("button, input[type='submit']").filter(has_text=re.compile(f"^{txt}$", re.IGNORECASE))
        if btn.count() > 0:
            btn.first.click()
            return
    raise Exception("Botão 'Salvar questão' não encontrado.")

def click_visualizar_questao(page):
    print("- Clicando em 'Visualizar questão'...")
    # Wait for the button to become visible and clickable, retrying for up to 16 seconds
    for attempt in range(8):
        try:
            accept_confirmations(page)
        except:
            pass
            
        try:
            # 1. Try by ID
            loc = page.locator("#btnGroupVisualizarQuestao")
            if loc.count() > 0 and loc.is_visible():
                loc.click(timeout=2000)
                print("  [Sucesso] Botão 'Visualizar questão' clicado.")
                return
        except:
            pass
            
        if attempt == 0:
            try:
                page.screenshot(path="/home/hamilcar/Antigravity/error_screenshot_save.png")
                print("  [Screenshot Save] Editor screenshot saved to /home/hamilcar/Antigravity/error_screenshot_save.png")
            except Exception as e:
                print(f"  [Erro ao tirar screenshot de salvamento] {e}")
            
        # 2. Try JS clicker
        try:
            js_code = """
            (() => {
                let btn = document.getElementById('btnGroupVisualizarQuestao');
                if (btn && btn.offsetWidth > 0) {
                    btn.click();
                    return "id_visualizar";
                }
                const btns = Array.from(document.querySelectorAll('button, a'));
                const vis = btns.find(b => {
                    const text = b.innerText.toLowerCase().trim();
                    return text === 'visualizar questão' || text === 'visualizar questao' || text === 'visualizar';
                });
                if (vis && vis.offsetWidth > 0) {
                    vis.click();
                    return "text_visualizar";
                }
                return null;
            })()
            """
            res = page.evaluate(js_code)
            if res:
                print(f"  [Sucesso] Botão 'Visualizar questão' clicado via JS ({res}).")
                return
        except:
            pass
            
        page.wait_for_timeout(2000)
        
    raise Exception("Botão 'Visualizar questão' não encontrado após aguardar salvamento.")

def reopen_question_from_dashboard(page, ident):
    print(f"- Reabrindo questão '{ident}' a partir do dashboard...")
    try:
        # Wait for the table/search element to load on the dashboard
        page.wait_for_selector("input[type='search'], #Pesquisar, .dataTables_filter input", timeout=8000)
    except Exception as e:
        print(f"  [Aviso] Campo de pesquisa não carregou: {e}")
        # Take a screenshot to see where we are
        page.screenshot(path="/home/hamilcar/Antigravity/error_screenshot_dashboard.png")
        print("  [Screenshot Save] Dashboard screenshot saved to /home/hamilcar/Antigravity/error_screenshot_dashboard.png")
        return False

    # 1. Click "Em elaboração" and "Pendentes" filters if they are not already checked
    js_click_filters = """
    (() => {
        const elements = Array.from(document.querySelectorAll('button, a, span, label, div, li'));
        const targets = ['em elaboração', 'em elaboracao', 'pendentes', 'pendente'];
        let clicked = 0;
        for (const el of elements) {
            // Only examine leaf nodes/inner nodes for text matching
            if (el.children.length > 0 && Array.from(el.children).some(c => ['span', 'label', 'button'].includes(c.tagName.toLowerCase()))) {
                continue;
            }
            const text = (el.innerText || '').toLowerCase().trim();
            if (targets.some(t => text.includes(t))) {
                const parent = el.closest('label, button, a, div.filtros') || el;
                const parentText = (parent.innerText || '');
                const hasCheck = parentText.includes('✓') || 
                                 parent.className.includes('active') ||
                                 (parent.querySelector('input') && parent.querySelector('input').checked);
                if (!hasCheck) {
                    el.click();
                    clicked++;
                }
            }
        }
        return clicked;
    })()
    """
    try:
        res = page.evaluate(js_click_filters)
        print(f"  [Info] Filtros clicados: {res}")
        page.wait_for_timeout(1500)  # Wait for data table to update
    except Exception as e:
        print(f"  [Aviso ao marcar filtros] {e}")

    # 2. Fill the search input with the question identification
    try:
        search_input = page.locator("input[type='search'], .dataTables_filter input, #Pesquisar").first
        search_input.fill(ident)
        page.wait_for_timeout(2000)  # Wait for table to filter
    except Exception as e:
        print(f"  [Erro ao preencher pesquisa] {e}")

    # 3. Locate the row with the matching question and click the edit link
    js_click_edit = f"""
    (() => {{
        const rows = Array.from(document.querySelectorAll('table tbody tr'));
        for (const row of rows) {{
            if (row.innerText.includes("{ident}")) {{
                const links = Array.from(row.querySelectorAll('a, button'));
                const editLink = links.find(l => {{
                    const text = l.innerText.toLowerCase().trim();
                    const title = (l.getAttribute('title') || '').toLowerCase();
                    return text.includes('editar') || text.includes('edit') || title.includes('editar') || title.includes('edit') || l.className.includes('edit');
                }});
                if (editLink) {{
                    editLink.click();
                    return "clicked_edit_link";
                }}
                if (links.length > 0) {{
                    links[links.length - 1].click(); // Fallback to last link in Actions column
                    return "clicked_last_link";
                }}
            }}
        }}
        return null;
    }})()
    """
    try:
        res = page.evaluate(js_click_edit)
        if res:
            print(f"  [Sucesso] Clique em editar realizado: {res}")
            # Wait for the editor form to load and be visible in viewport
            opened = False
            for _ in range(30):
                if is_element_in_viewport(page, "#Questao_Nome"):
                    opened = True
                    break
                page.wait_for_timeout(500)
            if opened:
                print("  [Sucesso] Editor de questão reaberto com sucesso.")
                return True
    except Exception as e:
        print(f"  [Erro ao clicar em editar via JS] {e}")

    # Fallback to Playwright click
    try:
        row = page.locator(f"tr:has-text('{ident}')").first
        edit_btn = row.locator("a:has-text('Editar'), button:has-text('Editar'), [title*='Editar']").first
        if edit_btn.count() > 0:
            edit_btn.click(timeout=3000)
            opened = False
            for _ in range(30):
                if is_element_in_viewport(page, "#Questao_Nome"):
                    opened = True
                    break
                page.wait_for_timeout(500)
            if opened:
                print("  [Sucesso] Editor de questão reaberto via fallback.")
                return True
    except Exception as e:
        print(f"  [Erro no fallback de clique em editar] {e}")

    return False

def is_element_in_viewport(page, selector):
    js_code = f"""
    (() => {{
        const el = document.querySelector("{selector}");
        if (!el) return {{ status: false, reason: "no element" }};
        
        // 1. Check if the element or any parent is explicitly hidden via display/visibility/opacity
        let current = el;
        while (current && current !== document.body) {{
            const style = window.getComputedStyle(current);
            if (style.display === 'none' || 
                style.visibility === 'hidden' || 
                style.opacity === '0') {{
                return {{ status: false, reason: "parent hidden: " + current.tagName + " class=" + current.className + " display=" + style.display + " vis=" + style.visibility + " op=" + style.opacity }};
            }}
            current = current.parentElement;
        }}
        
        // 2. Check if the parent modal wrapper (if any) is positioned off-screen (closed modal cache)
        const modal = el.closest('.modal');
        if (modal) {{
            if (!modal.classList.contains('in') && !modal.classList.contains('show')) {{
                return {{ status: false, reason: "modal is closed (missing 'in'/'show' class)" }};
            }}
            const style = window.getComputedStyle(modal);
            if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {{
                return {{ status: false, reason: "modal wrapper hidden" }};
            }}
            const mRect = modal.getBoundingClientRect();
            const isOutside = mRect.bottom <= 0 || mRect.top >= window.innerHeight || mRect.right <= 0 || mRect.left >= window.innerWidth;
            if (isOutside) {{
                return {{ status: false, reason: "modal wrapper off-screen: t=" + mRect.top + " b=" + mRect.bottom }};
            }}
        }}
        
        const rect = el.getBoundingClientRect();
        const ok = rect.width > 0 && rect.height > 0 && rect.right > 0;
        return {{ status: ok, reason: "rect: w=" + rect.width + " h=" + rect.height + " r=" + rect.right + " l=" + rect.left + " t=" + rect.top }};
    }})()
    """
    try:
        res = page.evaluate(js_code)
        if res['status']:
            print(f"    [Viewport Check] '{selector}' IS visible: {res['reason']}")
        return res['status']
    except:
        return False

def close_editor_modal(page):
    print("- Fechando modais ativos via JS...")
    try:
        close_active_modals(page)
    except Exception as e:
        print(f"  [Aviso] Erro ao limpar modais: {e}")

    print("- Navegando pelo menu lateral para retornar ao dashboard...")
    try:
        # Try clicking "Questões IES" or "Início" in the sidebar
        for sel in ["a:has-text('Questões IES')", "a:has-text('Questoes IES')", "a:has-text('Início')", "a:has-text('Inicio')"]:
            loc = page.locator(sel)
            if loc.count() > 0:
                loc.first.click(timeout=4000)
                print(f"  [Sucesso] Clique no menu lateral realizado ({sel}).")
                page.wait_for_timeout(2000)
                return
    except Exception as e:
        print(f"  [Aviso] Erro ao navegar pelo menu lateral: {e}")

def click_visualizar_questao_step(page, ident):
    print("- Aguardando confirmação do salvamento...")
    is_dashboard = False
    save_status = "waiting"
    
    # Wait for up to 30 seconds
    for idx in range(150):
        # First check if we are redirected to dashboard
        if not is_element_in_viewport(page, "#Questao_Nome"):
            print("  [Info] O editor não está mais no viewport (redirecionado ou modal fechado).")
            is_dashboard = True
            save_status = "success"
            break
            
        # Check save status via JS
        try:
            status_res = page.evaluate("""() => {
                const idVal = document.getElementById("Questao_IdQuestao")?.value;
                if (idVal && idVal !== "0") {
                    return { status: "success", reason: "id_assigned: " + idVal };
                }
                const notices = Array.from(document.querySelectorAll('.ui-pnotify, .sweet-alert, .swal2-container'));
                for (const n of notices) {
                    if (n.offsetWidth > 0) {
                        const txt = n.innerText;
                        const lowerTxt = txt.toLowerCase();
                        if (lowerTxt.includes("sucesso") || lowerTxt.includes("cadastrada") || lowerTxt.includes("salva")) {
                            return { status: "success", reason: "success_notification: " + txt };
                        } else {
                            return { status: "error", reason: "notification: " + txt };
                        }
                    }
                }
                const valErrs = Array.from(document.querySelectorAll('.field-validation-error, .text-danger, .error-message, .invalid-feedback'));
                const visibleValErrs = valErrs.filter(el => el.offsetWidth > 0 && el.innerText.trim() && el.innerText.trim() !== '*');
                if (visibleValErrs.length > 0) {
                    return { status: "error", reason: "validation_errors: " + visibleValErrs.map(el => el.innerText.trim()).join(", ") };
                }
                return { status: "waiting" };
            }""")
            
            if status_res["status"] == "success":
                print(f"  [Confirmado] Salvamento com sucesso: {status_res['reason']}")
                save_status = "success"
                break
            elif status_res["status"] == "error":
                print(f"  [Erro] Falha no salvamento: {status_res['reason']}")
                raise Exception(f"Erro ao salvar questão: {status_res['reason']}")
        except Exception as eval_e:
            if "Erro ao salvar questão:" in str(eval_e):
                raise eval_e
            # ignore other eval errors
            pass
            
        page.wait_for_timeout(200)
        
    if save_status != "success":
        raise Exception(f"Falha ao confirmar salvamento da questão (status: {save_status})")
            
    # Aguarda um pequeno delay para garantir que qualquer redirecionamento automático pós-salvamento ocorra
    page.wait_for_timeout(500)
    
    # Se o editor não estiver mais visível, significa que fomos redirecionados ao dashboard
    if not is_element_in_viewport(page, "#Questao_Nome"):
        print("  [Info] O editor fechou ou redirecionou após o salvamento. Forçando is_dashboard = True.")
        is_dashboard = True
        
    if is_dashboard:
        print("  [Info] Detectado desvio/salvamento do editor. Retornando ao dashboard...")
        # Fechar o modal do editor para retornar ao dashboard
        close_editor_modal(page)
        
        # Fechar possíveis modais de bloqueio no dashboard (como Termos de Uso)
        try:
            close_btn = page.locator("button:has-text('Fechar'), .modal button:has-text('Fechar'), .close, [data-dismiss='modal']").first
            if close_btn.count() > 0 and close_btn.is_visible():
                close_btn.click(timeout=2000)
                print("  [Info] Modal de bloqueio (ex: Termos de Uso) fechado.")
                page.wait_for_timeout(1000)
        except Exception as e:
            print(f"  [Aviso] Erro ao fechar modal de bloqueio: {e}")
            
        success = reopen_question_from_dashboard(page, ident)
        if not success:
            raise Exception("Não foi possível reabrir a questão a partir do dashboard.")
    else:
        print("  [Info] Permanecemos no editor de questões (modo edição).")
    
    # Click the Visualizar botão
    click_visualizar_questao(page)

def click_digital(page):
    print("- Selecionando 'Digital'...")
    
    # 1. Tenta clicar diretamente via ID com espera dinâmica de visibilidade
    try:
        page.locator("#btnVisualizarOnline").wait_for(state="visible", timeout=3000)
        page.locator("#btnVisualizarOnline").click(timeout=1000)
        print("  [Sucesso] Opção 'Digital' clicada via locator (#btnVisualizarOnline).")
        return
    except Exception as e:
        print(f"  [Aviso] Playwright click falhou para 'Digital': {e}. Tentando fallback JS...")
        
    # 2. Fallback para busca por texto usando JS
    js_code = """
    (() => {
        const els = Array.from(document.querySelectorAll('a, button, span, li, div, label, input'));
        const target = els.find(el => {
            const text = (el.innerText || el.value || '').trim().toLowerCase();
            return text === 'digital' && el.offsetWidth > 0;
        });
        if (target) {
            target.click();
            return true;
        }
        return false;
    })()
    """
    for attempt in range(20):
        try:
            if page.evaluate(js_code):
                print("  [Sucesso] Opção 'Digital' clicada via JS.")
                return
        except:
            pass
        page.wait_for_timeout(150)
        
    raise Exception("Opção 'Digital' não encontrada no menu/preview.")

def click_proximo(page):
    print("- Clicando em 'Próximo'...")
    try:
        # First try to wait and click the main ID locator directly
        page.locator("#buttonProximo").click(timeout=3000)
        return
    except Exception as e:
        print(f"  [Aviso] Falha ao clicar em #buttonProximo via Playwright: {e}. Tentando heurísticas...")
        
    for txt in ["Próximo", "Proximo", "Next", "Avançar"]:
        btn = page.locator("button, a").filter(has_text=re.compile(f"^{txt}$", re.IGNORECASE))
        if btn.count() > 0:
            try:
                btn.first.click(timeout=2000)
                return
            except:
                pass
    raise Exception("Botão 'Próximo' não pôde ser clicado ou está obstruído.")

def close_preview_modal(page):
    print("- Fechando modal de visualização (preview)...")
    try:
        # 1. Aguarda até 4 segundos para o modal de visualização ficar visível
        preview_modal = page.locator(".modal:not(:has(#Questao_Nome)):not(:has(#wizard))")
        try:
            preview_modal.first.wait_for(state="visible", timeout=4000)
        except Exception as wait_err:
            print(f"  [Info] Modal de visualização não apareceu como visível: {wait_err}. Prosseguindo...")
            
        # 2. Tenta encontrar e clicar no botão de fechar dentro do modal
        close_btn = preview_modal.locator("button.close, button:has-text('Fechar'), a:has-text('Fechar'), [aria-label='Close']").first
        clicked = False
        if close_btn.count() > 0:
            try:
                close_btn.click(timeout=2000)
                print("  [Sucesso] Botão de fechar modal clicado via locator.")
                clicked = True
            except Exception as click_err:
                print(f"  [Aviso] Falha ao clicar botão de fechar via locator: {click_err}")
                
        if not clicked:
            # Fallback JS click
            print("  [Info] Usando fallback JS para fechar o modal...")
            page.evaluate("""() => {
                const modals = Array.from(document.querySelectorAll('.modal'));
                modals.forEach(m => {
                    if (!m.querySelector('#Questao_Nome') && !m.querySelector('#wizard')) {
                        const closeBtns = Array.from(m.querySelectorAll('button, a, span'));
                        const closeBtn = closeBtns.find(b => {
                            const txt = (b.innerText || '').toLowerCase().trim();
                            return txt.includes('fechar') || txt === '×' || txt === 'x' || b.className.includes('close');
                        });
                        if (closeBtn) {
                            closeBtn.click();
                        } else {
                            m.style.display = 'none';
                            m.classList.remove('in', 'show');
                        }
                    }
                });
            }""")
            
        # 3. Aguarda o modal sumir completamente
        try:
            preview_modal.first.wait_for(state="hidden", timeout=3000)
            print("  [Sucesso] Modal de visualização ocultado com sucesso.")
        except Exception as hide_err:
            print(f"  [Aviso] Modal não sumiu em 3s: {hide_err}. Forçando ocultação via JS...")
            page.evaluate("""() => {
                document.querySelectorAll('.modal:not(:has(#Questao_Nome)):not(:has(#wizard))').forEach(m => {
                    m.style.display = 'none';
                    m.classList.remove('in', 'show');
                });
                document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
            }""")
            print("  [Sucesso] Ocultação forçada via JS aplicada.")
    except Exception as e:
        print(f"  [Aviso] Erro geral no close_preview_modal: {e}")

def close_active_modals(page):
    print("- Fechando possíveis modais abertos...")
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
    except:
        pass
        
    try:
        page.evaluate("""() => {
            // Force hide all modal overlay elements
            const modals = document.querySelectorAll('.modal');
            modals.forEach(m => {
                m.style.display = 'none';
                m.classList.remove('in', 'show');
            });
            // Remove backdrops
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(b => b.remove());
            // Restore body scroll
            document.body.classList.remove('modal-open');
            document.body.style.paddingRight = '';
        }""")
        page.wait_for_timeout(500)
    except Exception as e:
        print(f"  [Aviso] Erro ao fechar modais via JS: {e}")

def accept_confirmations(page):
    print("- Aceitando possíveis confirmações HTML...")
    for _ in range(6):
        js_code = """
        (() => {
            const btns = Array.from(document.querySelectorAll('.modal button, .sweet-alert button, .swal2-container button, .bootbox button, .modal a, .sweet-alert a'));
            const confirmBtn = btns.find(b => {
                const text = b.innerText.toLowerCase().trim();
                return text === 'sim' || text === 'confirmar' || text === 'ok' || text === 'yes' || text === 'aceitar';
            });
            if (confirmBtn && confirmBtn.offsetWidth > 0 && confirmBtn.offsetHeight > 0) {
                confirmBtn.click();
                return true;
            }
            return false;
        })()
        """
        try:
            res = page.evaluate(js_code)
            if res:
                print("  [Sucesso] Confirmação HTML aceita.")
                page.wait_for_timeout(1000)
                return
        except Exception as e:
            print(f"  [Erro ao aceitar confirmação] {e}")
        page.wait_for_timeout(500)


def handle_step_6(page):
    print("- Processando Passo 6 (Sugestões de correção)...")
    try:
        page.wait_for_timeout(500)
        # Loop para garantir que todos os botões 'Ignorar' / 'Ignorar todas' sejam clicados
        for attempt in range(15):
            cleared = page.evaluate("""() => {
                // 1. Procurar por botões de 'Ignorar todas'
                const allIgnoreBtns = Array.from(document.querySelectorAll('button, a, input, .btn, span.btn')).filter(el => {
                    const txt = (el.innerText || el.textContent || el.value || '').strip().toLowerCase();
                    const onclick = (el.getAttribute('onclick') || '').toLowerCase();
                    return (txt.includes('ignorar todas') || txt.includes('ignorar tudo') || onclick.includes('ignorartodas')) && el.offsetWidth > 0 && el.offsetHeight > 0;
                });
                if (allIgnoreBtns.length > 0) {
                    try { allIgnoreBtns[0].click(); } catch(e) {}
                    return "all";
                }
                
                // 2. Procurar por botões individuais de 'Ignorar'
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
            
        # Clicar em Salvar Correções se houver botão específico
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
        print(f"  Erro ao clicar em Ignorar: {e}")
        
    click_proximo(page)

def finish_question_flow(page, is_last):
    # Clear any old notifications/modals
    try:
        page.evaluate("() => document.querySelectorAll('.ui-pnotify, .sweet-alert, .swal2-container').forEach(el => el.remove())")
    except:
        pass

    # Wait up to 3 seconds for the submit buttons to become visible
    try:
        page.locator("#btnEnviarQuestao, #btnEnviarQuestaoCriarNovaMesmosParametros").first.wait_for(state="visible", timeout=3000)
    except:
        pass

    if is_last:
        print("- Finalizando. Clicando em 'Enviar'...")
        js_code = """
        (() => {
            let btn = document.getElementById('btnEnviarQuestao');
            if (btn && btn.offsetWidth > 0) {
                btn.click();
                return "id_enviar";
            }
            const btns = Array.from(document.querySelectorAll('button, a, input[type="submit"], input[type="button"]'));
            const enviar = btns.find(b => {
                const text = b.innerText.toLowerCase().trim();
                return text === 'enviar' || text === 'finalizar' || text === 'concluir';
            });
            if (enviar) {
                enviar.click();
                return "text_enviar";
            }
            return null;
        })()
        """
        clicked = False
        try:
            res = page.evaluate(js_code)
            if res:
                print(f"  [Sucesso] Botão de finalizar clicado via JS ({res}).")
                clicked = True
        except:
            pass
            
        if not clicked:
            try:
                page.locator("#btnEnviarQuestao").click(timeout=4000)
                clicked = True
            except:
                pass
                
        if not clicked:
            for txt in ["Enviar", "Finalizar", "Submit"]:
                btn = page.locator("button, a").filter(has_text=re.compile(f"^{txt}$", re.IGNORECASE))
                if btn.count() > 0:
                    btn.first.click()
                    clicked = True
                    break
                    
        if not clicked:
            raise Exception("Botão 'Enviar' final não encontrado.")
    else:
        print("- Clicando em 'Enviar e criar nova questão com os mesmos conteúdos e disciplinas'...")
        js_code = """
        (() => {
            // First try by ID — the safest approach
            let btn = document.getElementById('btnEnviarQuestaoCriarNovaMesmosParametros');
            if (btn && btn.offsetWidth > 0) {
                btn.click();
                return "id_criar_nova_mesmos";
            }
            // Fallback: find by text but ONLY if it contains 'mesmos' — to avoid the shorter button
            const btns = Array.from(document.querySelectorAll('button, a, input[type="submit"], input[type="button"]'));
            const criarNova = btns.find(b => {
                const text = b.innerText.toLowerCase().trim();
                return text.includes('mesmos') && text.includes('conteúdo');
            });
            if (criarNova) {
                criarNova.click();
                return "text_criar_nova_mesmos";
            }
            return null;
        })()
        """
        clicked = False
        try:
            res = page.evaluate(js_code)
            if res:
                print(f"  [Sucesso] Botão correto 'mesmos conteúdos' clicado via JS ({res}).")
                clicked = True
        except:
            pass

        if not clicked:
            try:
                page.locator("#btnEnviarQuestaoCriarNovaMesmosParametros").click(timeout=4000)
                clicked = True
                print("  [Sucesso] Botão clicado via locator por ID.")
            except:
                pass
                
        if not clicked:
            # Only try text-based matching for buttons that explicitly contain 'mesmos'
            for txt in ["mesmos conteúdo", "mesmos conteúdos e disciplinas", "Enviar e criar nova questão com os mesmos"]:
                btn = page.locator("button, a").filter(has_text=re.compile(txt, re.IGNORECASE))
                if btn.count() > 0:
                    btn.first.click()
                    clicked = True
                    print(f"  [Sucesso] Botão clicado via texto parcial: '{txt}'.")
                    break
                    
        if not clicked:
            raise Exception("Botão 'Enviar e criar nova questão com os mesmos conteúdos e disciplinas' não encontrado.")


    # Now, wait for the response/result of the submission
    print("- Aguardando resultado da submissão...")
    success = False
    error_msg = None
    
    # We poll for up to 30 seconds for either the editor to disappear/reset or an error to appear
    for _ in range(30):
        # 1. Check if redirected to dashboard (only relevant for is_last)
        if is_last and not is_element_in_viewport(page, "#Questao_Nome"):
            print("  [Sucesso] O editor não está mais visível (retornou ao dashboard).")
            success = True
            break
            
        # 2. Check notifications
        res = page.evaluate("""() => {
            const notices = Array.from(document.querySelectorAll('.ui-pnotify, .sweet-alert, .swal2-container'));
            for (const n of notices) {
                if (n.offsetWidth > 0) {
                    const txt = n.innerText;
                    const lowerTxt = txt.toLowerCase();
                    if (lowerTxt.includes("sucesso") || lowerTxt.includes("enviada") || lowerTxt.includes("enviado") || lowerTxt.includes("cadastrada")) {
                        return { status: "success", text: txt };
                    } else {
                        return { status: "error", text: txt };
                    }
                }
            }
            return null;
        }""")
        
        if res:
            if res["status"] == "success":
                print(f"  [Sucesso] Submissão confirmada por notificação: {res['text']}")
                success = True
                break
            else:
                error_msg = res["text"]
                break
                
        page.wait_for_timeout(1000)
        
    if not success:
        if error_msg:
            raise Exception(f"Erro no envio da questão: {error_msg}")
        else:
            raise Exception("Timeout aguardando confirmação de envio da questão.")
            
    # If not the last question, wait for the form to reset to a blank state
    if not is_last:
        print("- Aguardando o carregamento do novo formulário em branco...")
        form_reset = False
        for _ in range(30):
            reset_res = page.evaluate("""() => {
                const idVal = document.getElementById("Questao_IdQuestao")?.value;
                const textVal = typeof tinymce !== 'undefined' && tinymce.get('TextoQuestao') ? tinymce.get('TextoQuestao').getContent() : 'not_ready';
                
                // Form is reset if IdQuestao is "0" or empty, and the question text is empty
                const isIdReset = (idVal === "0" || idVal === "");
                const isTextReset = (textVal === "" || textVal === "<p></p>" || textVal === "<p><br></p>");
                return isIdReset && isTextReset;
            }""")
            if reset_res:
                print("  [Sucesso] Novo formulário em branco carregado.")
                form_reset = True
                break
            page.wait_for_timeout(1000)
            
        if not form_reset:
            raise Exception("Timeout aguardando o carregamento do novo formulário em branco (o form anterior não resetou).")

# In-page UI Injection
def inject_control_panel(page, df):
    global is_paused
    total_questions = len(df)
    try:
        # Detect state
        is_elaboration = is_element_in_viewport(page, "#Questao_Nome") or is_paused
        panel_exists = page.evaluate("() => !!document.getElementById('antigravity-panel')")
        callback_exists = page.evaluate("() => typeof window.pyStartAutomation === 'function'")
        
        if panel_exists and callback_exists:
            current_type = page.evaluate("() => document.getElementById('antigravity-panel').getAttribute('data-type')")
            expected_type = "elaboration" if is_elaboration else "waiting"
            if current_type == expected_type:
                return
            else:
                page.evaluate("() => document.getElementById('antigravity-panel').remove()")
        elif panel_exists:
            page.evaluate("() => document.getElementById('antigravity-panel')?.remove()")
                
        # Detect start index
        detected_idx = 0
        if is_elaboration:
            try:
                current_name = page.evaluate("document.getElementById('Questao_Nome')?.value")
                text_val = page.evaluate("typeof tinymce !== 'undefined' && tinymce.get('TextoQuestao') ? tinymce.get('TextoQuestao').getContent() : ''")
                is_empty = (text_val == "" or text_val == "<p></p>" or text_val == "<p><br></p>")
                
                if current_name:
                    for idx in range(total_questions):
                        ident = df.iloc[idx].get('Identificação da questão', '')
                        if ident and ident.strip() == current_name.strip():
                            if is_empty:
                                detected_idx = min(idx + 1, total_questions - 1)
                            else:
                                detected_idx = idx
                            break
            except:
                pass

        # CSS helper
        js_style_helper = """
        function stylePanel(div) {
            div.style.position = 'fixed';
            div.style.top = '20px';
            div.style.right = '20px';
            div.style.zIndex = '2147483647';
            div.style.width = '320px';
            div.style.background = 'rgba(15, 23, 42, 0.96)';
            div.style.backdropFilter = 'blur(12px)';
            div.style.border = '1px solid rgba(56, 189, 248, 0.3)';
            div.style.borderRadius = '14px';
            div.style.boxShadow = '0 20px 30px -10px rgba(0, 0, 0, 0.7), 0 0 15px rgba(56, 189, 248, 0.2)';
            div.style.color = '#f8fafc';
            div.style.padding = '18px';
            div.style.fontFamily = 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        }
        """
        
        file_name = os.path.basename(current_df_path) if 'current_df_path' in globals() and current_df_path else "Planilha Carregada"

        if is_elaboration:
            js_code = f"""
            (() => {{
                const div = document.createElement('div');
                div.id = 'antigravity-panel';
                div.setAttribute('data-type', 'elaboration');
                div.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
                        <span style="font-weight: 800; font-size: 13px; letter-spacing: 0.5px; color: #38bdf8; display: flex; align-items: center; gap: 6px;">
                            🤖 ANTIGRAVITY AUTOMATION
                        </span>
                        <span id="antigravity-indicator" style="width: 10px; height: 10px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 10px #22c55e;"></span>
                    </div>

                    <div style="background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.4); border-radius: 8px; padding: 10px; margin-bottom: 12px;">
                        <div style="font-weight: 700; font-size: 12px; color: #4ade80; margin-bottom: 4px;">✅ EDITOR DETECTADO E PRONTO!</div>
                        <div style="font-size: 11px; color: #cbd5e1; line-height: 1.3;">
                            📄 <b>{file_name}</b> ({total_questions} questões)
                        </div>
                    </div>

                    <div style="font-size: 11px; color: #e2e8f0; margin-bottom: 14px; line-height: 1.4; background: rgba(30, 41, 59, 0.7); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);" id="antigravity-status">
                        👉 <b>Passo final:</b> Confira o índice da questão inicial e clique em <b>🚀 Iniciar Inserção</b>.
                    </div>
                    
                    <div style="margin-bottom: 14px; background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);" id="antigravity-setup-area">
                        <label style="display: block; font-size: 10px; color: #94a3b8; font-weight: 700; margin-bottom: 6px; text-transform: uppercase;">1. Questão Inicial (Índice 0-based):</label>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <input type="number" id="antigravity-start-idx" value="{detected_idx}" min="0" max="{total_questions - 1}" style="
                                width: 80px;
                                background: rgba(30, 41, 59, 0.9);
                                border: 1px solid rgba(56, 189, 248, 0.4);
                                border-radius: 6px;
                                color: #f8fafc;
                                padding: 6px 8px;
                                font-size: 13px;
                                font-weight: 700;
                                outline: none;
                                text-align: center;
                            ">
                            <span style="font-size: 11px; color: #94a3b8;">(1ª questão = 0) / max: {total_questions - 1}</span>
                        </div>
                    </div>
                    
                    <div style="display: flex; flex-direction: column; gap: 10px;" id="antigravity-action-area">
                        <button id="antigravity-btn-run" style="
                            background: linear-gradient(135deg, #0ea5e9, #2563eb);
                            color: white;
                            border: none;
                            border-radius: 8px;
                            padding: 12px;
                            font-size: 14px;
                            font-weight: 700;
                            cursor: pointer;
                            transition: all 0.2s;
                            box-shadow: 0 4px 14px rgba(14, 165, 233, 0.4);
                        ">🚀 Iniciar Inserção Automática</button>
                        
                        <button id="antigravity-btn-test" style="
                            background: rgba(30, 41, 59, 0.8);
                            color: #cbd5e1;
                            border: 1px solid rgba(255, 255, 255, 0.15);
                            border-radius: 8px;
                            padding: 9px;
                            font-size: 12px;
                            font-weight: 600;
                            cursor: pointer;
                            transition: all 0.2s;
                        ">🧪 Testar Preenchimento (Sem Salvar)</button>
                    </div>

                    <div style="display: none; gap: 8px;" id="antigravity-error-area">
                        <button id="antigravity-btn-continue" style="
                            flex: 1;
                            background: #22c55e;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            padding: 8px;
                            font-size: 12px;
                            font-weight: 700;
                            cursor: pointer;
                        ">Continuar</button>
                        <button id="antigravity-btn-skip" style="
                            flex: 1;
                            background: #f59e0b;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            padding: 8px;
                            font-size: 12px;
                            font-weight: 700;
                            cursor: pointer;
                        ">Pular</button>
                        <button id="antigravity-btn-cancel" style="
                            flex: 1;
                            background: #ef4444;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            padding: 8px;
                            font-size: 12px;
                            font-weight: 700;
                            cursor: pointer;
                        ">Parar</button>
                    </div>
                `;
                
                stylePanel(div);
                document.body.appendChild(div);
                
                document.getElementById('antigravity-btn-run').addEventListener('click', () => {{
                    const startIdx = document.getElementById('antigravity-start-idx').value;
                    window.pyStartAutomation(parseInt(startIdx));
                }});
                
                document.getElementById('antigravity-btn-test').addEventListener('click', () => {{
                    const startIdx = document.getElementById('antigravity-start-idx').value;
                    window.pyTestAutomation(parseInt(startIdx));
                }});
                
                document.getElementById('antigravity-btn-continue').addEventListener('click', () => {{
                    window.pyUserAction("continue");
                }});
                
                document.getElementById('antigravity-btn-skip').addEventListener('click', () => {{
                    window.pyUserAction("skip");
                }});
                
                document.getElementById('antigravity-btn-cancel').addEventListener('click', () => {{
                    window.pyUserAction("cancel");
                }});
            }})()
            """
            page.evaluate(js_style_helper + js_code)
        else:
            js_code = f"""
            (() => {{
                const div = document.createElement('div');
                div.id = 'antigravity-panel';
                div.setAttribute('data-type', 'waiting');
                div.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">
                        <span style="font-weight: 800; font-size: 13px; letter-spacing: 0.5px; color: #38bdf8; display: flex; align-items: center; gap: 6px;">
                            🤖 ANTIGRAVITY AUTOMATION
                        </span>
                        <span style="width: 10px; height: 10px; background: #f59e0b; border-radius: 50%; box-shadow: 0 0 10px #f59e0b; animation: pulse 1.5s infinite;"></span>
                    </div>

                    <div style="font-weight: 700; font-size: 12px; color: #fbbf24; margin-bottom: 10px;">
                        ⏳ GUIA DE INÍCIO DA AUTOMAÇÃO
                    </div>

                    <div style="font-size: 11px; color: #cbd5e1; line-height: 1.5; background: rgba(30, 41, 59, 0.7); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 12px;">
                        <div style="margin-bottom: 8px; display: flex; gap: 6px;">
                            <span>1️⃣</span> <span>Faça o <b>Login</b> na plataforma se ainda não estiver logado.</span>
                        </div>
                        <div style="display: flex; gap: 6px;">
                            <span>2️⃣</span> <span>Navegue até a página de <b>Elaboração de Questão (Passo 4)</b>.</span>
                        </div>
                    </div>

                    <button id="antigravity-btn-goto-elab" style="
                        width: 100%;
                        background: rgba(56, 189, 248, 0.15);
                        color: #38bdf8;
                        border: 1px solid rgba(56, 189, 248, 0.3);
                        border-radius: 8px;
                        padding: 9px;
                        font-size: 12px;
                        font-weight: 700;
                        cursor: pointer;
                        transition: all 0.2s;
                    ">📍 Ir para Tela do Elaborador</button>

                    <style>
                        @keyframes pulse {{
                            0% {{ transform: scale(0.95); opacity: 0.5; }}
                            50% {{ transform: scale(1.15); opacity: 1; }}
                            100% {{ transform: scale(0.95); opacity: 0.5; }}
                        }}
                    </style>
                `;
                
                stylePanel(div);
                document.body.appendChild(div);

                document.getElementById('antigravity-btn-goto-elab').addEventListener('click', () => {{
                    window.location.href = 'https://avalia.grupoa.com.br/Elaborador';
                }});
            }})()
            """
            page.evaluate(js_style_helper + js_code)
    except Exception:
        pass
    except Exception:
        pass

def update_panel_status(page, message, status_type="info"):
    global current_df
    try:
        panel_exists = page.evaluate("() => !!document.getElementById('antigravity-panel')")
        if not panel_exists and current_df is not None:
            inject_control_panel(page, current_df)
    except:
        pass

    color_map = {
        "info": "#e2e8f0",
        "success": "#22c55e",
        "error": "#ef4444",
        "warning": "#f59e0b",
        "running": "#38bdf8"
    }
    color = color_map.get(status_type, "#e2e8f0")
    js_code = f"""
    (() => {{
        const statusEl = document.getElementById('antigravity-status');
        if (statusEl) {{
            statusEl.innerText = {json.dumps(message)};
            statusEl.style.color = '{color}';
        }}
    }})()
    """
    try:
        page.evaluate(js_code)
    except:
        pass

def set_panel_mode(page, mode):
    js_code = f"""
    (() => {{
        const actionArea = document.getElementById('antigravity-action-area');
        const setupArea = document.getElementById('antigravity-setup-area');
        const errorArea = document.getElementById('antigravity-error-area');
        const indicator = document.getElementById('antigravity-indicator');
        
        if (actionArea && errorArea && setupArea) {{
            if ('{mode}' === 'running') {{
                actionArea.style.display = 'none';
                setupArea.style.display = 'none';
                errorArea.style.display = 'none';
                if (indicator) {{
                    indicator.style.background = '#38bdf8';
                    indicator.style.boxShadow = '0 0 8px #38bdf8';
                }}
            }} else if ('{mode}' === 'error') {{
                actionArea.style.display = 'none';
                setupArea.style.display = 'none';
                errorArea.style.display = 'flex';
                if (indicator) {{
                    indicator.style.background = '#ef4444';
                    indicator.style.boxShadow = '0 0 8px #ef4444';
                }}
            }} else {{
                actionArea.style.display = 'flex';
                setupArea.style.display = 'block';
                errorArea.style.display = 'none';
                if (indicator) {{
                    indicator.style.background = '#22c55e';
                    indicator.style.boxShadow = '0 0 8px #22c55e';
                }}
            }}
        }}
    }})()
    """
    try:
        page.evaluate(js_code)
    except:
        pass

def wait_for_user_action(page):
    global user_action, is_paused, current_df
    user_action = None
    is_paused = True
    
    # Wait until user_action is set
    while user_action is None:
        try:
            panel_exists = page.evaluate("() => !!document.getElementById('antigravity-panel')")
            if not panel_exists and current_df is not None:
                inject_control_panel(page, current_df)
            set_panel_mode(page, "error")
            page.wait_for_timeout(250)
        except:
            time.sleep(0.25)
            
    action = user_action
    user_action = None
    is_paused = False
    set_panel_mode(page, "running")
    return action

def navigate_step1_to_step4(page):
    print("- Detectado que não estamos no Passo 4 (Elaboração). Tentando navegar automaticamente...")
    try:
        # Check if '#Questao_Nome' is visible first
        if is_element_in_viewport(page, "#Questao_Nome"):
            return True
            
        # We try to click "AvaliA" button on Step 1
        avalia_btn = page.locator("button, a").filter(has_text=re.compile(r"^AvaliA$", re.IGNORECASE))
        if avalia_btn.count() > 0 and avalia_btn.first.is_visible():
            print("  [Passo 1] Selecionando fonte 'AvaliA'...")
            avalia_btn.first.click()
            page.wait_for_timeout(500)
            
        # For Step 2 and 3, and generally, we look for #buttonProximo and click it
        for attempt in range(5):
            btn_prox = page.locator("#buttonProximo")
            if btn_prox.count() > 0 and btn_prox.first.is_visible():
                print(f"  [Passo {attempt+1}] Clicando em 'Próximo'...")
                btn_prox.first.click()
                page.wait_for_timeout(1500)
                if is_element_in_viewport(page, "#Questao_Nome"):
                    print("  [Sucesso] Chegamos ao Passo 4!")
                    return True
    except Exception as e:
        print(f"  [Aviso na Navegação] {e}")
        
    return is_element_in_viewport(page, "#Questao_Nome")

def wait_for_form_ready(page):
    print("- Aguardando inicialização completa do formulário/editor...")
    
    # 1. If not on Step 4, attempt navigation from Step 1 to 4
    if not is_element_in_viewport(page, "#Questao_Nome"):
        navigate_step1_to_step4(page)
        
    # 2. Wait for the main input field to be visible in viewport
    page.locator("#Questao_Nome:visible").wait_for(state="visible", timeout=20000)
    
    # 2. Wait for loading spinner to be hidden
    try:
        page.locator("#loadingQuestao:visible").wait_for(state="hidden", timeout=5000)
    except:
        pass
        
    # 3. Wait for the dropdowns to have options populated (more than just the default '0' or empty) and tinyMCE to be ready
    for _ in range(40):
        try:
            has_options = page.evaluate("""() => {
                const visibleModal = Array.from(document.querySelectorAll('.modal')).find(m => {
                    const style = window.getComputedStyle(m);
                    return (m.classList.contains('in') || m.classList.contains('show')) && style.display !== 'none';
                }) || document;
                
                const tipoSelect = visibleModal.querySelector('#Questao_IdTipoQuestao');
                const habSelect = visibleModal.querySelector('#IdHabilidadeQuestao');
                const tinymceReady = typeof window.tinymce !== 'undefined';
                
                const tipoOk = tipoSelect && tipoSelect.options.length > 1;
                const habOk = habSelect && habSelect.options.length > 1;
                
                return tipoOk && habOk && tinymceReady;
            }""")
            if has_options:
                # Extra small timeout to ensure any final binding/rendering completes
                page.wait_for_timeout(1000)
                print("  [Sucesso] Formulário pronto para interação.")
                return True
        except:
            pass
        page.wait_for_timeout(500)
        
    print("  [Aviso] Form ready check expirou, prosseguindo mesmo assim...")
    return False

# Full step flow runner
def run_insertion_for_row(page, row, is_last, delay=1.0):
    tipo_val = str(row.get('Tipo de Questão') or row.get('Tipo da questão', '')).lower()
    is_discursiva = "discursiva" in tipo_val or "discursivo" in tipo_val
    
    if is_discursiva:
        steps = [
            ("Aguardar Formulário", lambda: wait_for_form_ready(page)),
            ("Tipo da Questão", lambda: select_tipo_questao(page, str(row.get('Tipo de Questão') or row.get('Tipo da questão', '')))),
            ("Nível Cognitivo", lambda: select_nivel_cognitivo(page, str(row.get('Nível cognitivo', '')))),
            ("Identificação", lambda: fill_identificacao(page, str(row.get('Identificação da questão', '')))),
            ("Palavras-chave", lambda: fill_palavra_chave(page, str(row.get('Palavra chave', '')))),
            ("Texto da Questão", lambda: fill_rich_text_editor(page, 'TextoQuestao', str(row.get('Texto da Questão', '')))),
            ("Padrão de Resposta", lambda: fill_rich_text_editor(page, 'TextoPadraoResposta', str(row.get('Feedback da questão', '')))),
            ("Feedback", lambda: fill_rich_text_editor(page, 'TextoFeedbackQuestao', str(row.get('Feedback da questão', '')))),
            ("Salvar Questão", lambda: click_salvar_questao(page, row)),
            ("Visualizar Questão", lambda: click_visualizar_questao_step(page, str(row.get('Identificação da questão', '')))),
            ("Clicar em Digital", lambda: click_digital(page)),
            ("Fechar Modais", lambda: close_preview_modal(page)),
            ("Clicar em Próximo (Passo 4)", lambda: click_proximo(page)),
            ("Clicar em Próximo (Passo 5)", lambda: click_proximo(page)),
            ("Sugestões de correção (Passo 6)", lambda: handle_step_6(page)),
            ("Finalização (Passo 7)", lambda: finish_question_flow(page, is_last))
        ]
    else:
        steps = [
            ("Aguardar Formulário", lambda: wait_for_form_ready(page)),
            ("Tipo da Questão", lambda: select_tipo_questao(page, str(row.get('Tipo de Questão') or row.get('Tipo da questão', '')))),
            ("Nível Cognitivo", lambda: select_nivel_cognitivo(page, str(row.get('Nível cognitivo', '')))),
            ("Identificação", lambda: fill_identificacao(page, str(row.get('Identificação da questão', '')))),
            ("Palavras-chave", lambda: fill_palavra_chave(page, str(row.get('Palavra chave', '')))),
            ("Texto da Questão", lambda: fill_rich_text_editor(page, 'TextoQuestao', str(row.get('Texto da Questão', '')))),
            ("Alternativa A", lambda: fill_rich_text_editor(page, 'TextoAfirmativaA', str(row.get('Alternativa A', '')))),
            ("Alternativa B", lambda: fill_rich_text_editor(page, 'TextoAfirmativaB', str(row.get('Alternativa B', '')))),
            ("Alternativa C", lambda: fill_rich_text_editor(page, 'TextoAfirmativaC', str(row.get('Alternativa C', '')))),
            ("Alternativa D", lambda: fill_rich_text_editor(page, 'TextoAfirmativaD', str(row.get('Alternativa D', '')))),
            ("Remover Alternativa E", lambda: remove_alternative_e(page)),
            ("Aceitar Confirmações Deletar", lambda: accept_confirmations(page)),
            ("Marcar Resposta Correta", lambda: select_correct_answer_checkbox(page, extract_correct_answer_letter(row))),
            ("Padrão de Resposta", lambda: fill_rich_text_editor(page, 'TextoPadraoResposta', str(row.get('Feedback da questão', '')))),
            ("Feedback", lambda: fill_rich_text_editor(page, 'TextoFeedbackQuestao', str(row.get('Feedback da questão', '')))),
            ("Salvar Questão", lambda: click_salvar_questao(page, row)),
            ("Visualizar Questão", lambda: click_visualizar_questao_step(page, str(row.get('Identificação da questão', '')))),
            ("Clicar em Digital", lambda: click_digital(page)),
            ("Fechar Modais", lambda: close_preview_modal(page)),
            ("Clicar em Próximo (Passo 4)", lambda: click_proximo(page)),
            ("Clicar em Próximo (Passo 5)", lambda: click_proximo(page)),
            ("Sugestões de correção (Passo 6)", lambda: handle_step_6(page)),
            ("Finalização (Passo 7)", lambda: finish_question_flow(page, is_last))
        ]
    
    id_assigned = None
    
    for step_name, step_fn in steps:
        print(f"Executando etapa: {step_name}...")
        update_panel_status(page, f"Executando: {step_name}...", "running")
        
        while True:
            try:
                step_fn()
                page.wait_for_timeout(int(delay * 1000))
                
                # Captura o ID da questão se o passo "Salvar Questão" ou "Visualizar Questão" foi bem-sucedido
                if step_name in ["Salvar Questão", "Visualizar Questão"]:
                    try:
                        val = page.evaluate("""() => {
                            const el1 = document.getElementById('Questao_IdQuestao');
                            if (el1 && el1.value && el1.value !== '0') return el1.value;
                            const el2 = document.getElementById('IdQuestao');
                            if (el2 && el2.value && el2.value !== '0') return el2.value;
                            return null;
                        }""")
                        if val:
                            id_assigned = val
                    except:
                        pass
                break
            except Exception as e:
                print(f"Erro na etapa {step_name}: {e}")
                try:
                    page.screenshot(path="/home/hamilcar/Antigravity/error_screenshot.png")
                    print("  [Screenshot] Salvo em /home/hamilcar/Antigravity/error_screenshot.png")
                except Exception as err:
                    print(f"  [Erro ao tirar screenshot] {err}")
                update_panel_status(page, f"Erro em '{step_name}': {str(e)[:50]}.", "error")
                action = wait_for_user_action(page)
                if action == "continue":
                    update_panel_status(page, f"Reexecutando: {step_name}...", "running")
                    continue
                elif action == "skip":
                    print(f"Etapa '{step_name}' pulada pelo usuário.")
                    break
                elif action == "cancel":
                    raise Exception("Automação parada pelo usuário.")
                    
    return id_assigned

def print_summary_table(results):
    if not results:
        return
        
    print("\n" + "="*85)
    print("                      RELATÓRIO DE INSERÇÃO DE QUESTÕES")
    print("="*85)
    print(f"{'#':<4} | {'Identificação da Questão':<35} | {'Tipo de Questão':<15} | {'ID AVA':<10} | {'Status':<10}")
    print("-"*85)
    for r in results:
        ident_trunc = r['ident'] if len(r['ident']) <= 35 else r['ident'][:32] + "..."
        tipo_trunc = r['tipo'] if len(r['tipo']) <= 15 else r['tipo'][:12] + "..."
        print(f"{r['num']:<4} | {ident_trunc:<35} | {tipo_trunc:<15} | {r['id_ava']:<10} | {r['status']:<10}")
    print("="*85 + "\n")
    
    try:
        report_path = "/home/hamilcar/Antigravity/relatorio_insercao.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Relatório de Inserção de Questões AVA\n\n")
            f.write("| # | Identificação da Questão | Tipo de Questão | ID AVA | Status |\n")
            f.write("|---|---|---|---|---|\n")
            for r in results:
                f.write(f"| {r['num']} | {r['ident']} | {r['tipo']} | {r['id_ava']} | {r['status']} |\n")
        print(f"[Relatório] Tabela salva em arquivo markdown: {report_path}")
    except Exception as e:
        print(f"[Aviso] Não foi possível salvar o relatório em arquivo: {e}")

def display_summary_table_on_panel(page, results):
    if not results:
        return
        
    rows_html = ""
    for r in results:
        status_color = "#22c55e" if r['status'] == "Sucesso" else "#ef4444"
        ident_trunc = r['ident'] if len(r['ident']) <= 16 else r['ident'][:14] + "..."
        tipo_trunc = r['tipo'] if len(r['tipo']) <= 12 else r['tipo'][:10] + "..."
        rows_html += f"""
        <tr style='border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 10px;'>
            <td style='padding: 6px 4px; color: #94a3b8;'>{r['num']}</td>
            <td style='padding: 6px 4px;' title='{r['ident']}'>{ident_trunc}</td>
            <td style='padding: 6px 4px;' title='{r['tipo']}'>{tipo_trunc}</td>
            <td style='padding: 6px 4px; font-weight: 600; color: #38bdf8;'>{r['id_ava']}</td>
            <td style='padding: 6px 4px; color: {status_color}; font-weight: bold;'>{r['status']}</td>
        </tr>
        """
        
    panel_html = f"""
    <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;'>
        <span style='font-weight: 700; font-size: 13px; letter-spacing: 0.5px; color: #38bdf8;'>LOTE PROCESSADO</span>
        <span style='width: 8px; height: 8px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 8px #22c55e;'></span>
    </div>
    <div style='font-size: 11px; color: #e2e8f0; margin-bottom: 10px; line-height: 1.4;'>
        Resumo do lote inserido:
    </div>
    <div style='max-height: 200px; overflow-y: auto; background: rgba(30, 41, 59, 0.5); padding: 4px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);'>
        <table style='width: 100%; border-collapse: collapse; text-align: left; color: #f8fafc; font-family: sans-serif;'>
            <thead>
                <tr style='border-bottom: 1px solid rgba(255,255,255,0.15); font-size: 9px; text-transform: uppercase; color: #94a3b8;'>
                    <th style='padding: 4px;'>#</th>
                    <th style='padding: 4px;'>Ident.</th>
                    <th style='padding: 4px;'>Tipo</th>
                    <th style='padding: 4px;'>ID AVA</th>
                    <th style='padding: 4px;'>Status</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    <div style='margin-top: 12px;'>
        <button id='antigravity-btn-close-summary' style='
            width: 100%;
            background: rgba(255, 255, 255, 0.1);
            color: #f8fafc;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 6px;
            padding: 8px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
        '>Fechar Painel</button>
    </div>
    """
    
    js_code = f"""
    (() => {{
        const panel = document.getElementById('antigravity-panel');
        if (panel) {{
            panel.innerHTML = {json.dumps(panel_html)};
            panel.style.width = '350px';
            const closeBtn = document.getElementById('antigravity-btn-close-summary');
            if (closeBtn) {{
                closeBtn.addEventListener('click', () => panel.remove());
            }}
        }}
    }})()
    """
    try:
        page.evaluate(js_code)
    except Exception as e:
        print(f"[Aviso] Falha ao renderizar a tabela no painel do navegador: {e}")

def run_automation_flow(page, df, start_idx):
    print(f"\nIniciando inserção em massa a partir do índice {start_idx}...")
    success_count = 0
    total = len(df)
    results_list = []
    
    for i in range(start_idx, total):
        row = df.iloc[i]
        is_last = (i == total - 1)
        ident = str(row.get('Identificação da questão', ''))
        tipo = str(row.get('Tipo de Questão') or row.get('Tipo da questão', ''))
        
        try:
            update_panel_status(page, f"Processando questão {i+1} de {total}...", "running")
            ava_id = run_insertion_for_row(page, row, is_last, delay=1.0)
            success_count += 1
            update_panel_status(page, f"Questão {i+1}/{total} inserida com sucesso!", "success")
            
            results_list.append({
                "num": i + 1,
                "ident": ident,
                "tipo": tipo,
                "id_ava": ava_id if ava_id else "N/A",
                "status": "Sucesso"
            })
            page.wait_for_timeout(3000) # delay for page to settle/reload
        except Exception as e:
            print(f"Erro fatal ou interrupção na inserção: {e}")
            update_panel_status(page, f"Automação interrompida: {e}", "error")
            results_list.append({
                "num": i + 1,
                "ident": ident,
                "tipo": tipo,
                "id_ava": "N/A",
                "status": f"Falha: {str(e)[:50]}"
            })
            print_summary_table(results_list)
            display_summary_table_on_panel(page, results_list)
            page.wait_for_timeout(3000)
            set_panel_mode(page, "idle")
            return
            
    print_summary_table(results_list)
    display_summary_table_on_panel(page, results_list)
    page.wait_for_timeout(4000)
    set_panel_mode(page, "idle")

def run_test_flow(page, df, idx):
    if idx >= len(df):
        update_panel_status(page, "Índice inválido para teste.", "error")
        page.wait_for_timeout(2000)
        set_panel_mode(page, "idle")
        return
        
    row = df.iloc[idx]
    print(f"\nExecutando teste para questão no índice {idx}...")
    
    steps = [
        ("Identificação", lambda: fill_identificacao(page, str(row.get('Identificação da questão', '')))),
        ("Palavras-chave", lambda: fill_palavra_chave(page, str(row.get('Palavra chave', '')))),
        ("Tipo da Questão", lambda: select_tipo_questao(page, str(row.get('Tipo de Questão') or row.get('Tipo da questão', '')))),
        ("Nível Cognitivo", lambda: select_nivel_cognitivo(page, str(row.get('Nível cognitivo', '')))),
        ("Texto da Questão", lambda: fill_rich_text_editor(page, 'TextoQuestao', str(row.get('Texto da Questão', '')))),
        ("Alternativa A", lambda: fill_rich_text_editor(page, 'TextoAfirmativaA', str(row.get('Alternativa A', '')))),
        ("Alternativa B", lambda: fill_rich_text_editor(page, 'TextoAfirmativaB', str(row.get('Alternativa B', '')))),
        ("Alternativa C", lambda: fill_rich_text_editor(page, 'TextoAfirmativaC', str(row.get('Alternativa C', '')))),
        ("Alternativa D", lambda: fill_rich_text_editor(page, 'TextoAfirmativaD', str(row.get('Alternativa D', '')))),
        ("Remover Alternativa E", lambda: remove_alternative_e(page)),
        ("Marcar Resposta Correta", lambda: select_correct_answer_checkbox(page, extract_correct_answer_letter(row))),
        ("Padrão de Resposta", lambda: fill_rich_text_editor(page, 'TextoPadraoResposta', str(row.get('Feedback da questão', '')))),
        ("Feedback", lambda: fill_rich_text_editor(page, 'TextoFeedbackQuestao', str(row.get('Feedback da questão', ''))))
    ]
    
    set_panel_mode(page, "running")
    for step_name, step_fn in steps:
        update_panel_status(page, f"Testando: {step_name}...", "running")
        try:
            step_fn()
            page.wait_for_timeout(100)
        except Exception as e:
            print(f"Erro no teste em {step_name}: {e}")
            update_panel_status(page, f"Erro no teste: {step_name}", "error")
            page.wait_for_timeout(4000)
            set_panel_mode(page, "idle")
            return
            
    update_panel_status(page, "Teste finalizado com sucesso! (Campos preenchidos)", "success")
    page.wait_for_timeout(4000)
    set_panel_mode(page, "idle")

def main():
    global start_automation_requested, test_automation_requested, user_action, requested_start_idx, current_df, current_df_path
    print("===================================================================")
    print("   🤖 ANTIGRAVITY ACADEMIC AUTOMATION ASSISTANT v3 (INTERATIVO)")
    print("===================================================================")
    
    df, loaded_path = load_data()
    if df is None:
        print("Saindo...")
        return
        
    current_df_path = loaded_path
    
    print("\n-------------------------------------------------------------------")
    print(" 💡 CONFIGURAÇÃO DE DISCIPLINA")
    print("-------------------------------------------------------------------")
    discipline = input("Digite o nome da disciplina para aplicar nas questões\n(ou pressione ENTER para manter o nome original contido na planilha): ").strip()
    if discipline:
        def adjust_text(text):
            text_str = str(text).strip()
            if text_str.startswith("Disciplina:"):
                idx = text_str.find("\n")
                if idx != -1:
                    rest = text_str[idx+1:]
                    return f"Disciplina: {discipline}\n{rest}"
                else:
                    return f"Disciplina: {discipline}"
            else:
                return f"Disciplina: {discipline}\n{text_str}"
                
        col_name = None
        for col in df.columns:
            if str(col).strip().lower() in ["texto da questão", "texto da questao", "texto"]:
                col_name = col
                break
        if col_name:
            df[col_name] = df[col_name].apply(adjust_text)
            print(f"✨ Disciplina definida com sucesso: '{discipline}'")
            
    print("\n-------------------------------------------------------------------")
    print(" ⚡ MODO DE INÍCIO AUTOMÁTICO (AUTOSTART)")
    print("-------------------------------------------------------------------")
    autostart_input = input("Deseja ativar o início automático (5s) ao entrar no editor? (s/n, padrão 'n'): ").strip().lower()
    enable_autostart = (autostart_input == 's')
    
    current_df = df

    print("\n===================================================================")
    print(" 📌 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("-------------------------------------------------------------------")
    print(f"  📄 Arquivo:    {os.path.basename(loaded_path)}")
    print(f"  📊 Questões:   {len(df)} itens carregados")
    print(f"  📚 Disciplina: {discipline if discipline else 'Original da planilha'}")
    print(f"  🚀 Autostart:  {'Ativado (5s)' if enable_autostart else 'Desativado (Controle Manual)'}")
    print("-------------------------------------------------------------------")
    print(" 💡 INSTRUÇÃO NO NAVEGADOR:")
    print("    Quando o Chromium se abrir, o painel interativo da Antigravity no")
    print("    canto superior direito te guiará passo a passo até o Passo 4!")
    print("===================================================================\n")
    
    input("Pressione ENTER para abrir o navegador e iniciar...")
        
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            print("Conectado ao navegador ativo via CDP na porta 9222.")
        except Exception as cdp_err:
            user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"
            print(f"Abrindo Chromium com perfil persistente em: {user_data_dir}")
            context = p.chromium.launch_persistent_context(user_data_dir, headless=False, args=['--remote-debugging-port=9222'])
        page = context.pages[0] if context.pages else context.new_page()
        
        def setup_page_listeners(p):
            try:
                p.on("dialog", lambda dialog: (print(f"  [Dialog] Aceitando automaticamente: {dialog.message}"), dialog.accept()))
                p.on("console", lambda msg: print(f"  [Browser Console] {msg.text}") if msg.type != "debug" else None)
                p.on("pageerror", lambda err: print(f"  [Browser Error] {err}"))
                
                # Intercept network requests and responses to monitor AJAX calls
                def handle_req(request):
                    if request.method == "POST" or "Questao" in request.url:
                        print(f"  [Network Request] {request.method} {request.url}")
                        try:
                            if request.post_data:
                                print(f"    PostData: {request.post_data[:1000]}")
                        except:
                            pass
                def handle_res(response):
                    request = response.request
                    if request.method == "POST" or "Questao" in request.url:
                        print(f"  [Network Response] {request.method} {request.url} | Status: {response.status}")
                        try:
                            content_type = response.headers.get("content-type", "").lower()
                            if "json" in content_type or "text" in content_type:
                                print(f"    Response body: {response.text()[:2000]}")
                        except Exception as re:
                            print(f"    Failed to read response body: {re}")
                            
                p.on("request", handle_req)
                p.on("response", handle_res)
            except Exception as e:
                pass
                
        setup_page_listeners(page)
        context.on("page", setup_page_listeners)
        
        login_url = "https://avauni.grupoa.education/plataforma/auth/signin"
        print(f"Navegando para: {login_url}")
        try:
            page.goto(login_url, wait_until="commit", timeout=60000)
        except Exception as e:
            print(f"Aviso durante navegação inicial: {e}. Continuando...")
        
        # Expose Python callbacks
        page.expose_function("pyStartAutomation", on_start)
        page.expose_function("pyTestAutomation", on_test)
        page.expose_function("pyUserAction", on_user_action)
        
        print("\nPronto! O painel de controle foi integrado na página do navegador.")
        print("Faça login na plataforma e vá para a página de elaboração de questões.")
        
        # Main monitoring loop
        last_url = ""
        last_log_time = 0
        auto_started = False
        has_run_once = False
        while True:
            active_page = get_active_page(context)
            if active_page:
                try:
                    url = active_page.url
                    current_time = time.time()
                    is_elaboration = is_element_in_viewport(active_page, "#Questao_Nome")
                    if not is_elaboration:
                        auto_started = False
                    
                    if url != last_url or current_time - last_log_time > 5.0:
                        print(f"[Monitor] URL Ativa: {url} | Editor de Questão Detectado: {is_elaboration}")
                        last_url = url
                        last_log_time = current_time

                    # Expose callbacks on ALL open pages so panel works on any domain
                    for _p in context.pages:
                        try:
                            _p.expose_function("pyStartAutomation", on_start)
                        except: pass
                        try:
                            _p.expose_function("pyTestAutomation", on_test)
                        except: pass
                        try:
                            _p.expose_function("pyUserAction", on_user_action)
                        except: pass
                        
                    inject_control_panel(active_page, df)
                    
                    if enable_autostart and is_elaboration and not auto_started and not has_run_once:
                        auto_started = True
                        print("\n[AutoStart] Editor detectado! Iniciando contagem regressiva de 5 segundos...")
                        cancelled = False
                        for sec in range(5, 0, -1):
                            update_panel_status(active_page, f"Iniciando em {sec} segundos... (Clique 'Parar' se quiser cancelar)", "warning")
                            set_panel_mode(active_page, "error") # Show error area for Stop button
                            active_page.wait_for_timeout(1000)
                            
                            if user_action == "cancel":
                                cancelled = True
                                user_action = None
                                break
                                
                        if cancelled:
                            update_panel_status(active_page, "Autostart cancelado pelo usuário.", "info")
                            set_panel_mode(active_page, "idle")
                            print("[AutoStart] Cancelado pelo usuário.")
                            has_run_once = True
                        else:
                            try:
                                val = active_page.evaluate("document.getElementById('antigravity-start-idx').value")
                                requested_start_idx = int(val)
                            except:
                                pass
                            start_automation_requested = True
                except Exception as e:
                    pass
            
            # Check for requested actions
            if start_automation_requested:
                start_automation_requested = False
                if active_page:
                    set_panel_mode(active_page, "running")
                    try:
                        run_automation_flow(active_page, df, requested_start_idx)
                    finally:
                        auto_started = False
                        has_run_once = True
            elif test_automation_requested:
                test_automation_requested = False
                if active_page:
                    set_panel_mode(active_page, "running")
                    try:
                        run_test_flow(active_page, df, requested_start_idx)
                    finally:
                        auto_started = False
                        has_run_once = True
                    
            try:
                if active_page:
                    active_page.wait_for_timeout(500)
                else:
                    time.sleep(0.5)
            except Exception:
                # Browser or context might be closed
                break
                
        print("\nNavegador fechado. Encerrando automação.")
        context.close()

if __name__ == "__main__":
    main()
