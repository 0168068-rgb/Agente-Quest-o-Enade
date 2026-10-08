import os
import sys
import time
import re
import pandas as pd
import subprocess
from playwright.sync_api import sync_playwright

def print_welcome_banner():
    print("\n" + "═"*80)
    print(" 🤖  AUTOMAÇÃO DE PREENCHIMENTO DE QUESTÕES NO AVA (GRUPO A / VUE.JS)")
    print("═"*80)
    print("""
 📋 CONDIÇÕES NECESSÁRIAS E PRÉ-REQUISITOS PARA O BOM FUNCIONAMENTO:

  1. 📊 PLANILHA EXCEL FORMATADA (.xlsx):
     - Deve conter as colunas: Ordem (ou Identificação), Enunciado (ou Texto da Questão),
       Resposta 1 a 5 (ou Alternativas A a E), Resposta certa (ou Questão correta / Feedback).
     - Suporta tanto a estrutura padrão quanto o formato alternativo com Alternativas A-D/E.
     - IMPORTANTE: Apenas questões de Múltipla Escolha podem ser automatizadas.

  2. 🌐 NAVEGADOR E AUTENTICAÇÃO (LOGIN):
     - O script abrirá um navegador Chromium com sessão persistente.
     - Você deverá fazer LOGIN MANUALMENTE com suas credenciais de professor/tutor.
     - Navegue até a disciplina e abra o Quiz/Atividade em modo de Edição.

  3. 📝 MODAL DE EDIÇÃO DA QUESTÃO (.edit-question-modal):
     - Para realizar o TESTE INICIAL, o modal de edição de questão precisa estar ABERTO.
     - Durante a execução em LOTE, o script tentará clicar no botão '+' e em 'Salvar'
       automaticamente, mas informará no terminal caso necessite de intervenção manual.
""")
    print("═"*80 + "\n")

def normalize_columns(df):
    """
    Padroniza nomes de colunas que usam nomes alternativos (ex: 'Alternativa A' -> 'Resposta 1').
    """
    column_aliases = {
        'identificação da questão': 'Ordem',
        'identificacao da questao': 'Ordem',
        'identificação': 'Ordem',
        'identificacao': 'Ordem',
        'texto da questão': 'Enunciado',
        'texto da questao': 'Enunciado',
        'alternativa a': 'Resposta 1',
        'alternativa b': 'Resposta 2',
        'alternativa c': 'Resposta 3',
        'alternativa d': 'Resposta 4',
        'alternativa e': 'Resposta 5',
        'questão correta': 'Resposta certa',
        'questao correta': 'Resposta certa',
        'feedback da questão': 'Feedback',
        'feedback da questao': 'Feedback',
    }
    
    rename_dict = {}
    for col in df.columns:
        col_clean = str(col).strip().lower()
        if col_clean in column_aliases:
            rename_dict[col] = column_aliases[col_clean]
            
    if rename_dict:
        df = df.rename(columns=rename_dict)
        
    for i in range(1, 6):
        if f'Resposta {i}' not in df.columns:
            df[f'Resposta {i}'] = ""
            
    if 'Ordem' not in df.columns:
        df['Ordem'] = range(1, len(df) + 1)
        
    return df

def load_data():
    excel_path = None
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
    else:
        current_dir = "/home/hamilcar/Antigravity"
        files = [f for f in os.listdir(current_dir) if f.endswith(".xlsx") and not f.startswith("~$")]
        
        print("📁 PASSO 1: SELEÇÃO DA PLANILHA DE QUESTÕES")
        print("-" * 50)
        
        if files:
            print("Planilhas Excel encontradas no diretório do projeto:")
            for idx, f in enumerate(files, 1):
                recommended = " ⭐ (Recomendado para carga)" if "cdc_2.xlsx" in f or "redes_2.xlsx" in f else ""
                print(f"   [{idx}] {f}{recommended}")
            print("   [0] Digitar o caminho de outra planilha personalizada")
            
            try:
                choice = input("\n👉 Escolha o número da planilha (ou aperte ENTER para a opção 1): ").strip()
                if not choice:
                    excel_path = os.path.join(current_dir, files[0])
                elif choice == "0":
                    excel_path = input("👉 Digite o caminho completo da planilha: ").strip()
                elif choice.isdigit() and 1 <= int(choice) <= len(files):
                    excel_path = os.path.join(current_dir, files[int(choice) - 1])
                else:
                    excel_path = choice
            except KeyboardInterrupt:
                print("\n\n👋 Operação cancelada pelo usuário.")
                sys.exit(0)
        else:
            excel_path = input("👉 Digite o caminho completo da planilha Excel: ").strip()
            
    if not excel_path or not os.path.exists(excel_path):
        print(f"\n❌ [ERRO] Arquivo Excel não encontrado em: '{excel_path}'")
        sys.exit(1)
        
    print(f"\n📊 Carregando e analisando planilha Excel: '{os.path.basename(excel_path)}'...")
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"\n❌ [ERRO] Falha ao abrir o arquivo Excel: {e}")
        sys.exit(1)
        
    df = df.fillna("")
    df = normalize_columns(df)
    
    required = ['Ordem', 'Enunciado', 'Resposta 1', 'Resposta 2', 'Resposta 3', 'Resposta 4']
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"\n❌ [ERRO] A planilha selecionada não possui as colunas obrigatórias: {missing}")
        print("💡 Certifique-se de usar a planilha gerada (ex: questoes_simulado_cdc_2.xlsx ou questoes_simulado_redes_2.xlsx).")
        sys.exit(1)
        
    total_q = len(df)
    discursive_count = 0
    valid_mc_count = 0
    ans_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0, 'Outros': 0}
    
    for idx, row in df.iterrows():
        r1 = str(row.get('Resposta 1', '')).strip()
        if not r1:
            discursive_count += 1
            continue
        
        valid_mc_count += 1
        try:
            ans = extract_correct_answer(row)
            letter = chr(ord('A') + ans - 1)
            if letter in ans_distribution:
                ans_distribution[letter] += 1
            else:
                ans_distribution['Outros'] += 1
        except Exception:
            ans_distribution['Outros'] += 1

    print("\n" + "─"*60)
    print(" 🔎 RESUMO DIAGNÓSTICO DA PLANILHA:")
    print(f"   • Total de linhas/questões: {total_q}")
    print(f"   • Questões de Múltipla Escolha válidas: {valid_mc_count}")
    if discursive_count > 0:
        print(f"   ⚠️  Questões Discursivas (sem alternativas): {discursive_count}")
        print("      (Atenção: O script irá pular ou falhar em questões discursivas)")
    print("   • Distribuição do Gabarito:", ", ".join([f"{k}: {v}" for k, v in ans_distribution.items() if v > 0]))
    print("─"*60 + "\n")
    
    return df, excel_path

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
            output_lines.append(f"[{i}] Tag: {tag} | Type: {type_attr} | ID: {id_attr} | Placeholder: '{placeholder}' | Valor: '{val[:50]}'")
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
        print("💡 Mapeamento completo salvo em: /home/hamilcar/Antigravity/inspection.txt")
    except Exception as e:
        print(f"Erro ao salvar arquivo de inspeção: {e}")

def text_to_html(text):
    if not text or not str(text).strip():
        return "<p><br></p>"
    text = str(text).replace('\r\n', '\n').replace('\r', '\n')
    lines = text.split('\n')
    html_parts = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            escaped = (stripped
                       .replace('&', '&amp;')
                       .replace('<', '&lt;')
                       .replace('>', '&gt;'))
            html_parts.append(f"<p>{escaped}</p>")
    return "".join(html_parts) if html_parts else "<p><br></p>"

def fill_tinymce_editor(page, editor_index, content):
    import json
    html_content = text_to_html(content)
    val_json = json.dumps(html_content)
    required_length = 7 if editor_index == 6 else 6
    
    page.wait_for_function(f"""
        window.tinymce && (() => {{
            const textareas = Array.from(document.querySelectorAll('.edit-question-modal textarea'));
            if (textareas.length < {required_length}) return false;
            return textareas.every(t => window.tinymce.get(t.id) !== null);
        }})()
    """, timeout=15000)
    
    js_code = f"""
    (() => {{
        const textareas = Array.from(document.querySelectorAll('.edit-question-modal textarea'));
        if ({editor_index} >= textareas.length) {{
            throw new Error("Textarea de índice {editor_index} não foi encontrada no modal. Total encontradas: " + textareas.length);
        }}
        const id = textareas[{editor_index}].id;
        const editor = window.tinymce.get(id);
        if (!editor) {{
            throw new Error("Editor TinyMCE correspondente ao id '" + id + "' não está disponível no window.tinymce.");
        }}
        
        const val = {val_json};
        
        // 1. Mutar o modelo question do Vue diretamente (se disponível)
        const container = document.querySelector('.edit-question-modal') || document;
        const all = Array.from(container.querySelectorAll('*'));
        const options = all.filter(el => el.__vue__ && el.__vue__.$options && (el.__vue__.$options.name === 'QuizOption' || el.__vue__.$options._componentTag === 'QuizOption')).map(el => el.__vue__);
        if (options.length > 0 && options[0].question) {{
            const question = options[0].question;
            if ({editor_index} === 0) {{
                question.enunciated = val;
            }} else if ({editor_index} >= 1 && {editor_index} <= 5) {{
                const optIndex = {editor_index} - 1;
                const targetLetter = ['a', 'b', 'c', 'd', 'e'][optIndex];
                const opt = question.options.find(o => (o.letter || "").toLowerCase() === targetLetter) || question.options[optIndex];
                if (opt) {{
                    opt.text = val;
                }}
            }} else if ({editor_index} === 6) {{
                question.feedback = val;
            }}
        }}
        
        // 2. Atualizar TinyMCE
        editor.setContent(val);
        editor.fire('change');
        editor.fire('input');
        
        // 3. Atualizar textarea nativa
        const textarea = textareas[{editor_index}];
        textarea.value = val;
        textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
        textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
        
        // 4. Subir na árvore DOM e atualizar instâncias intermediárias do Vue
        let curr = textarea;
        while (curr) {{
            if (curr.__vue__) {{
                const vm = curr.__vue__;
                if (vm.$listeners) {{
                    if (vm.$listeners.input) vm.$emit('input', val);
                    if (vm.$listeners.change) vm.$emit('change', val);
                }}
                if (vm.$options && vm.$options.propsData) {{
                    if (vm.content && typeof vm.content === 'object' && 'html' in vm.content) {{
                        vm.content.html = val;
                    }} else if ('content' in vm) {{
                        vm.content = val;
                    }}
                    if (vm.value && typeof vm.value === 'object' && 'html' in vm.value) {{
                        vm.value.html = val;
                    }} else if ('value' in vm) {{
                        vm.value = val;
                    }}
                }}
            }}
            curr = curr.parentElement;
        }}
        return true;
    }})()
    """
    page.evaluate(js_code)

def extract_correct_answer(row):
    col_names = [col for col in row.index if str(col).strip().lower() in ("resposta certa", "resposta_certa", "respostacerta", "resposta", "questão correta", "questao correta")]
    
    val = None
    if col_names:
        val = str(row[col_names[0]]).strip()
        
    if val:
        match_letter = re.match(r'^([A-Ea-e])$', val)
        if match_letter:
            letter = match_letter.group(1).upper()
            return ord(letter) - ord('A') + 1
        
        match_num = re.match(r'^([1-5])$', val)
        if match_num:
            return int(match_num.group(1))
            
        match_letter_any = re.search(r'\b([A-E])\b', val, re.IGNORECASE)
        if match_letter_any:
            letter = match_letter_any.group(1).upper()
            return ord(letter) - ord('A') + 1
            
        match_num_any = re.search(r'\b([1-5])\b', val)
        if match_num_any:
            return int(match_num_any.group(1))

    feedback_col = [col for col in row.index if 'feedback' in str(col).strip().lower()]
    feedback_text = str(row.get(feedback_col[0], '')) if feedback_col else str(row.get('Feedback', ''))
    
    match_fb = re.search(r'\d+\s*[—\-–]\s*([A-E])', feedback_text, re.IGNORECASE)
    if match_fb:
        letter = match_fb.group(1).upper()
        return ord(letter) - ord('A') + 1
    
    match_fb_any = re.search(r'\b([A-E])\b', feedback_text, re.IGNORECASE)
    if match_fb_any:
        letter = match_fb_any.group(1).upper()
        return ord(letter) - ord('A') + 1

    raise ValueError(f"Não foi possível extrair a resposta correta para a questão de Ordem {row.get('Ordem')}.")

def select_correct_answer(page, correct_answer_num):
    index = int(correct_answer_num) - 1
    js_code = f"""
    (() => {{
        const options = Array.from(document.querySelectorAll('.edit-question-modal .option--editing'));
        if (options.length <= {index}) {{
            throw new Error("Não foram encontradas opções de alternativas suficientes no modal. Total: " + options.length);
        }}
        const btn = options[{index}].querySelector('button');
        if (!btn) {{
            throw new Error("Botão de seleção à esquerda da alternativa não encontrado.");
        }}
        btn.click();
        return true;
    }})()
    """
    page.evaluate(js_code)
    print(f"  ✓ Resposta correta (alternativa {correct_answer_num}) selecionada.")

def activate_feedback_geral(page):
    is_checked = page.evaluate('''() => {
        const label = Array.from(document.querySelectorAll('label')).find(l => l.textContent.trim().toLowerCase().includes('feedback geral'));
        if (!label) return false;
        const checkbox = label.closest('.v-input').querySelector('input[type="checkbox"]');
        return checkbox ? checkbox.checked : false;
    }''')
    if not is_checked:
        page.locator('label:has-text("Feedback geral")').evaluate("el => el.click()")
        print("  ✓ Caixa 'Feedback Geral' ativada.")
    else:
        print("  ℹ️  Caixa 'Feedback Geral' já estava ativada.")

def click_button(page, label_options, name):
    for label in label_options:
        btn = page.locator("button").filter(has_text=re.compile(f"^{label}$", re.IGNORECASE))
        if btn.count() > 0:
            btn.first.evaluate("el => el.click()")
            print(f"  ✓ Botão '{name}' clicado.")
            return True
            
    for label in label_options:
        btn = page.locator(f"button:has-text('{label}')")
        if btn.count() > 0:
            btn.first.evaluate("el => el.click()")
            print(f"  ✓ Botão '{name}' clicado (busca parcial).")
            return True
            
    return False

def click_add_question_button(page):
    locator = page.locator('button.add-question__btn:not(.v-btn--disabled):not([disabled])')
    if locator.count() > 0:
        locator.last.evaluate("el => el.click()")
        print("  ✓ Botão '+' clicado.")
        return True
    
    locator = page.locator('button.add-question__btn')
    if locator.count() > 0:
        locator.last.evaluate("el => el.click()")
        print("  ✓ Botão '+' clicado (fallback).")
        return True
        
    return False

def fill_question(page, row, delay=1.0):
    print(f"\n📝 Preenchendo Questão - Ordem {row['Ordem']}...")
    
    print("   1. Preenchendo Enunciado...")
    fill_tinymce_editor(page, 0, str(row['Enunciado']))
    time.sleep(delay)
    
    for i in range(1, 6):
        col_name = f"Resposta {i}"
        print(f"   2.{i} Preenchendo {col_name}...")
        fill_tinymce_editor(page, i, str(row[col_name]))
        time.sleep(delay)
        
    print("   3. Selecionando resposta correta...")
    correct_ans = extract_correct_answer(row)
    select_correct_answer(page, correct_ans)
    time.sleep(delay)
    
    print("   4. Ativando Feedback Geral...")
    activate_feedback_geral(page)
    time.sleep(delay)
    
    print("   5. Preenchendo texto do Feedback...")
    feedback_val = str(row.get('Feedback', ''))
    fill_tinymce_editor(page, 6, feedback_val)
    time.sleep(delay)

def guided_browser_setup(p):
    print("\n🌐 PASSO 2: INICIALIZAÇÃO DO NAVEGADOR E ORIENTAÇÃO AO USUÁRIO")
    print("-" * 50)
    print("Iniciando navegador Chromium com sessão persistente em 'playwright_user_data'...")
    user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"
    
    try:
        context = p.chromium.launch_persistent_context(user_data_dir, headless=False)
    except Exception as e:
        err_msg = str(e)
        if "Executable doesn't exist" in err_msg or "playwright install" in err_msg:
            print("\n⚠️  [ATENÇÃO] Os executáveis do navegador Chromium do Playwright não foram encontrados.")
            print("👉 Instalando automaticamente os navegadores com 'playwright install chromium'...")
            try:
                subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
                print("✓ Navegador Chromium instalado com sucesso! Abrindo...")
                context = p.chromium.launch_persistent_context(user_data_dir, headless=False)
            except Exception as inst_err:
                print(f"\n❌ Erro ao instalar o Chromium: {inst_err}")
                print("💡 Execute no seu terminal:  playwright install chromium")
                sys.exit(1)
        else:
            raise e

    page = context.pages[0] if context.pages else context.new_page()
    login_url = "https://avauni.grupoa.education/plataforma/auth/signin"
    print(f"🔗 Abrindo endereço de autenticação: {login_url}")
    page.goto(login_url)
    
    print("\n" + "═"*75)
    print(" 📋 INSTRUÇÕES DE NAVEGAÇÃO E LOGIN (FAÇA NO NAVEGADOR QUE ABRIU):")
    print("═"*75)
    print("  1. No navegador, digite seu E-mail e Senha e clique em ENTRAR.")
    print("  2. Navegue até a disciplina desejada.")
    print("  3. Abra o Quiz ou Atividade onde as questões serão cadastradas.")
    print("  4. Clique em EDITAR / ADICIONAR QUESTÃO.")
    print("  5. MANTENHA O MODAL DE EDIÇÃO DA QUESTÃO (.edit-question-modal) ABERTO.")
    print("═"*75)
    
    input("\n👉 Quando estiver com o navegador logado e o MODAL ABERTO, pressione ENTER para continuar...")
    return context, page

def run_test_mode(page, df, delay_actions):
    print("\n🧪 PASSO 3: VALIDAÇÃO DE TESTE DA 1ª QUESTÃO")
    print("-" * 50)
    
    if len(df) == 0:
        print("❌ [ERRO] Nenhuma questão encontrada na planilha.")
        return
        
    is_modal_visible = page.locator('.edit-question-modal').is_visible()
    if not is_modal_visible:
        print("\n⚠️  [ATENÇÃO] O modal de edição (.edit-question-modal) NÃO está aberto no navegador!")
        print("👉 Por favor, vá ao navegador, abra o modal de edição de questão e pressione ENTER.")
        input("Pressione ENTER assim que o modal estiver visível na tela...")
        
    row = df.iloc[0]
    try:
        fill_question(page, row, delay_actions)
        print("\n" + "═"*75)
        print(" 🎉 PREENCHIMENTO DE TESTE CONCLUÍDO COM SUCESSO!")
        print("═"*75)
        print("""
 🔍 CHECKLIST DE CONFIRMAÇÃO MANUAL NO NAVEGADOR:
   [ ] 1. O Enunciado foi preenchido no primeiro editor?
   [ ] 2. As alternativas foram preenchidas corretamente?
   [ ] 3. A resposta correta foi marcada com a opção circular à esquerda?
   [ ] 4. A caixa 'Feedback Geral' foi ativada e o texto preenchido?

 ⚙️ PRÓXIMOS PASSOS NO NAVEGADOR ANTES DA CARGA EM LOTE:
   a) Clique no botão 'OK' do modal na tela.
   b) Clique em 'SALVAR' (no canto superior da tela do AVA).
   c) Verifique se a questão ficou salva na lista.
   d) Clique no botão '+' para abrir a janela da próxima questão.
===============================================================================""")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        print("💡 Verifique se o modal do editor TinyMCE estava totalmente carregado.")

def run_batch_mode(page, df, delay_actions):
    print("\n🚀 PASSO 4: EXECUÇÃO DA CARGA EM LOTE")
    print("-" * 50)
    
    min_ordem = int(df['Ordem'].min()) if 'Ordem' in df.columns else 1
    default_start = min_ordem + 1 if min_ordem == 1 and len(df) > 1 else min_ordem
    
    print(f"📊 Total de questões disponíveis na planilha: {len(df)}")
    try:
        start_input = input(f"👉 A partir de qual Ordem deseja iniciar a carga? (Padrão: {default_start}): ").strip()
        if not start_input:
            start_ordem = default_start
        else:
            start_ordem = int(start_input)
    except ValueError:
        print("❌ Valor inválido. Operação cancelada.")
        return

    run_df = df[df['Ordem'] >= start_ordem]
    if run_df.empty:
        print(f"❌ Nenhuma questão encontrada a partir da Ordem {start_ordem}.")
        return

    print("\nEscolha o Modo de Execução:")
    print("  [1] Modo Automático Contínuo (processa todas em sequência)")
    print("  [2] Modo Passo a Passo Assistido (pede confirmação a cada questão)")
    mode_choice = input("👉 Escolha o modo (1 ou 2) [Padrão: 1]: ").strip()
    step_mode = True if mode_choice == "2" else False

    print(f"\n⚡ Serão processadas {len(run_df)} questões (Ordem {start_ordem} até {int(run_df['Ordem'].max())}).")
    confirm = input("Confirma o início da gravação? (s/n): ").strip().lower()
    if confirm != 's':
        print("⚠️ Operação cancelada.")
        return

    print("\n🤖 Iniciando processamento...")
    success_count = 0
    run_list = list(run_df.iterrows())
    
    for i, (idx, row) in enumerate(run_list):
        print(f"\n" + "═"*60)
        print(f" ▶  Processando Questão {i+1} de {len(run_list)} | Ordem: {row['Ordem']}")
        print("═"*60)
        
        if step_mode:
            input("👉 Pressione ENTER no terminal para iniciar o preenchimento desta questão...")

        try:
            is_modal_visible = page.locator('.edit-question-modal').is_visible()
            if not is_modal_visible:
                print("- Modal fechado. Tentando abrir nova questão clicando no botão '+'...")
                if not click_add_question_button(page):
                    print("\n⚠️ [INTERVENÇÃO REQUERIDA] Botão '+' não encontrado.")
                    input("👉 Abra o modal no navegador e pressione ENTER aqui...")
                page.wait_for_selector('.edit-question-modal', timeout=10000)
                time.sleep(delay_actions + 1.0)
            
            fill_question(page, row, delay_actions)
            
            print("- Clicando no botão 'OK' do modal...")
            if not click_button(page, ["ok", "OK", "Ok"], "OK"):
                print("\n⚠️ [INTERVENÇÃO REQUERIDA] Botão 'OK' não encontrado.")
                input("👉 Clique em 'OK' no navegador e pressione ENTER...")
            time.sleep(delay_actions + 1.0)
            
            print("- Clicando no botão 'Salvar' da página...")
            if not click_button(page, ["Salvar", "salvar", "SALVAR", "Save", "save"], "Salvar"):
                print("\n⚠️ [INTERVENÇÃO REQUERIDA] Botão 'Salvar' não encontrado.")
                input("👉 Clique em 'Salvar' no navegador e pressione ENTER...")
            time.sleep(delay_actions + 2.0)
            
            if i < len(run_list) - 1:
                print("- Clicando no botão '+' para a próxima questão...")
                if not click_add_question_button(page):
                    print("\n⚠️ [INTERVENÇÃO REQUERIDA] Botão '+' não encontrado.")
                    input("👉 Clique no '+' no navegador e pressione ENTER...")
                time.sleep(delay_actions + 1.0)
            
            success_count += 1
            print(f" ✅ Questão de Ordem {row['Ordem']} concluída com sucesso!")
        except Exception as e:
            print(f"\n❌ Ocorreu um problema na questão Ordem {row['Ordem']}: {e}")
            ans = input("Deseja tentar a próxima questão do lote? (s/n): ").strip().lower()
            if ans != 's':
                break

    print("\n" + "═"*75)
    print(f" 🎉 PROCESSAMENTO FINALIZADO! {success_count} de {len(run_df)} questões cadastradas.")
    print("═"*75)

def main():
    print_welcome_banner()
    df, excel_path = load_data()

    with sync_playwright() as p:
        context, page = guided_browser_setup(p)
        delay_actions = 1.0

        while True:
            print("\n" + "─"*50)
            print(" 🕹️  MENU INTERATIVO DE COMANDOS:")
            print("─"*50)
            print("  [1] test     : Realiza teste de preenchimento da 1ª questão no modal aberto")
            print("  [2] run      : Inicia a gravação em lote de todas as questões")
            print("  [3] delay    : Ajusta a pausa entre ações no navegador (Atual: {}s)".format(delay_actions))
            print("  [4] inspect  : Mapeia elementos de entrada e botões da tela para depuração")
            print("  [0] exit     : Encerrar automação e fechar o navegador")
            print("─"*50)
            
            try:
                cmd = input("\n👉 Escolha uma opção (1-4 ou comando test/run/exit): ").strip().lower()
            except KeyboardInterrupt:
                print("\nEncerrando...")
                break
                
            if cmd in ('0', 'exit'):
                print("\n👋 Encerrando sessão e fechando o navegador...")
                break
            elif cmd in ('1', 'test'):
                run_test_mode(page, df, delay_actions)
            elif cmd in ('2', 'run'):
                run_batch_mode(page, df, delay_actions)
            elif cmd in ('3', 'delay'):
                try:
                    val = float(input("👉 Digite o novo tempo de espera em segundos (ex: 1.5): "))
                    delay_actions = max(0.5, val)
                    print(f"⏱️ Delay atualizado para {delay_actions}s")
                except ValueError:
                    print("❌ Valor inválido.")
            elif cmd in ('4', 'inspect'):
                inspect_elements(page)
            else:
                print("⚠️ Opção não reconhecida. Escolha 1, 2, 3, 4 ou 0.")

        context.close()

if __name__ == "__main__":
    main()
