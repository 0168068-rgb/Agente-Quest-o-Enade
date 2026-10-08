#!/usr/bin/env python3
"""
======================================================================
  🎓 AUTOMAÇÃO DE REGISTRO DE FREQUÊNCIA - PORTAL SOPHIA (UNIG / NEAD)
======================================================================
Script genérico e interativo desenvolvido para professores.
Permite informar qualquer planilha Excel, selecionar o intervalo de datas,
e realizar o lançamento das presenças no portal acadêmico SophiA.
"""

import os
import sys
import argparse
import getpass
import unicodedata
import pandas as pd
import asyncio
from difflib import SequenceMatcher
from playwright.async_api import async_playwright

# Configuração do caminho de navegadores do Playwright para executáveis (.exe)
if os.name == 'nt':
    local_appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~/AppData/Local'))
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.join(local_appdata, 'ms-playwright')
else:
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.expanduser('~/.cache/ms-playwright')

SOPHIA_URL = 'https://portal.sophia.com.br/SophiA_110/Acesso.aspx?escola=8262'

def print_header():
    print("=" * 75)
    print("  🎓 AUTOMAÇÃO DE REGISTRO DE FREQUÊNCIA - PORTAL SOPHIA (UNIVERSAL)")
    print("=" * 75)

def normalize_name(name: str) -> str:
    """Normaliza nomes removendo acentos, espaços extras e convertendo para maiúsculas."""
    if not isinstance(name, str) or not name.strip():
        return ''
    nfd_name = unicodedata.normalize('NFD', name.strip())
    ascii_name = ''.join(c for c in nfd_name if unicodedata.category(c) != 'Mn')
    return ' '.join(ascii_name.upper().split())

def match_score(name1: str, name2: str) -> float:
    """Calcula a pontuação de similaridade entre dois nomes normalizados."""
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    if norm1 == norm2:
        return 1.0
    
    if norm1 in norm2 or norm2 in norm1:
        return 0.95
        
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    common_words = words1.intersection(words2)
    
    if len(words1) > 0 and len(words2) > 0:
        token_similarity = (2.0 * len(common_words)) / (len(words1) + len(words2))
        seq_similarity = SequenceMatcher(None, norm1, norm2).ratio()
        return max(token_similarity, seq_similarity)
    
    return SequenceMatcher(None, norm1, norm2).ratio()

def auto_detect_sheet_and_columns(file_path: str):
    """Detecta automaticamente ou permite escolher a aba e colunas de Data e Nome do Aluno."""
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    
    selected_sheet = sheet_names[0]
    if len(sheet_names) > 1:
        # Se houver uma aba chamada 'Presenças' ou 'Respostas', seleciona por padrão
        for s in sheet_names:
            if 'presença' in s.lower() or 'resposta' in s.lower():
                selected_sheet = s
                break

    df = pd.read_excel(file_path, sheet_name=selected_sheet)
    cols = df.columns.tolist()
    
    # Identificar coluna de data
    date_col = None
    for c in cols:
        c_lower = str(c).lower()
        if 'carimbo' in c_lower or 'data' in c_lower:
            date_col = c
            break
            
    # Identificar coluna de nome
    name_col = None
    for c in cols:
        c_lower = str(c).lower()
        if 'nome' in c_lower or 'aluno' in c_lower:
            name_col = c
            break
            
    # Se não detectado automaticamente, solicita interação do usuário
    if not date_col or not name_col:
        print(f"\n📑 Colunas detectadas na aba '{selected_sheet}':")
        for idx, col in enumerate(cols, 1):
            print(f"  [{idx}] {col}")
            
        if not date_col:
            idx_d = input("👉 Escolha o número da coluna referente à DATA: ").strip()
            date_col = cols[int(idx_d)-1] if idx_d.isdigit() and 1 <= int(idx_d) <= len(cols) else cols[0]
            
        if not name_col:
            idx_n = input("👉 Escolha o número da coluna referente ao NOME DO ALUNO: ").strip()
            name_col = cols[int(idx_n)-1] if idx_n.isdigit() and 1 <= int(idx_n) <= len(cols) else cols[1]

    return selected_sheet, date_col, name_col

def load_student_courses(file_path: str) -> dict:
    """Carrega o mapa {nome_normalizado: curso} a partir da aba 'Alunos', se existir."""
    try:
        xls = pd.ExcelFile(file_path)
        if 'Alunos' in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name='Alunos')
            if 'Nome' in df.columns and 'Curso' in df.columns:
                course_map = {}
                for _, row in df.iterrows():
                    name = str(row['Nome']).strip()
                    course = str(row['Curso']).strip()
                    if name and course:
                        course_map[normalize_name(name)] = course
                return course_map
    except Exception as e:
        print(f"⚠️ Não foi possível carregar a aba Alunos: {e}")
    return {}

def get_student_course(student_name: str, course_map: dict) -> str:
    """Retorna o curso do aluno pelo mapa, utilizando busca exata ou por similaridade (fuzzy)."""
    if not student_name or not course_map:
        return ""
    
    norm_name = normalize_name(student_name)
    if norm_name in course_map:
        return course_map[norm_name]
    
    best_score = 0.0
    best_course = ""
    for a_norm, course in course_map.items():
        score = match_score(norm_name, a_norm)
        if score > best_score and score >= 0.70:
            best_score = score
            best_course = course
            
    return best_course

def courses_match(student_course: str, target_course: str) -> bool:
    """Verifica de forma genérica se o curso do aluno corresponde ao curso alvo (funciona para qualquer Nº de cursos)."""
    if not student_course or not target_course:
        return False
        
    sc_norm = normalize_name(student_course)
    tc_norm = normalize_name(target_course)
    
    if sc_norm == tc_norm:
        return True
        
    if sc_norm in tc_norm or tc_norm in sc_norm:
        return True
        
    score = match_score(sc_norm, tc_norm)
    return score >= 0.75

def load_dates_and_presents(file_path: str, sheet_name: str, date_col: str, name_col: str, course_filter: str = None) -> dict:
    """Lê a planilha e retorna um dicionário {data_str: [lista_de_alunos]} (filtrado por curso se especificado)."""
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df.dropna(subset=[date_col, name_col])
    
    course_map = load_student_courses(file_path)
    
    df['Data_Obj'] = pd.to_datetime(df[date_col], errors='coerce')
    mask_na = df['Data_Obj'].isna()
    if mask_na.any():
        df.loc[mask_na, 'Data_Formatada'] = df.loc[mask_na, date_col].astype(str)
    
    mask_not_na = ~df['Data_Obj'].isna()
    if mask_not_na.any():
        df.loc[mask_not_na, 'Data_Formatada'] = df.loc[mask_not_na, 'Data_Obj'].dt.strftime('%d/%m/%Y')
        
    summary = {}
    for d_str in df['Data_Formatada'].unique():
        if not d_str or str(d_str).strip() == '' or str(d_str).strip().lower() == 'nat':
            continue
        sub_df = df[df['Data_Formatada'] == d_str]
        presents = sub_df[name_col].dropna().astype(str).str.strip().unique().tolist()
        
        if course_filter and course_map:
            filtered_presents = []
            for p in presents:
                st_course = get_student_course(p, course_map)
                if st_course and courses_match(st_course, course_filter):
                    filtered_presents.append(p)
            presents = filtered_presents

        summary[str(d_str).strip()] = presents
        
    return summary

async def process_attendance_for_date(page, data_frequencia: str, present_students: list, args):
    """Aplica os filtros no portal SophiA e ativa os checkboxes dos alunos presentes."""
    print(f"\n" + "-"*70)
    print(f"📌 PROCESSANDO CHAMADA DO DIA: {data_frequencia}")
    print(f"🏫 Turma Alvo: {getattr(args, 'turma', 'N/A')}")
    print(f"-"*70)

    # Filtrar os alunos presentes para garantir que pertencem ao curso/turma selecionado em args.turma
    if hasattr(args, 'planilha') and args.planilha:
        course_map = load_student_courses(args.planilha)
        target_course = getattr(args, 'turma', '').strip()
        if course_map and target_course:
            filtered = []
            for s in present_students:
                st_course = get_student_course(s, course_map)
                if st_course and courses_match(st_course, target_course):
                    filtered.append(s)
            present_students = filtered

    if not present_students:
        print(f"⚠️ NENHUM aluno registrado para o curso '{getattr(args, 'turma', '')}' na data {data_frequencia}.")
        print("   O lançamento para esta turma nesta data será ignorado.")
        return
    
    # Navegação para a página Frequência
    try:
        await page.click('text=Frequência', timeout=5000)
    except:
        await page.goto('https://portal.sophia.com.br/SophiA_110/Frequencia.aspx', wait_until='networkidle')
    await page.wait_for_load_state('networkidle')
    await page.wait_for_timeout(1500)
    
    periodo_id = '#ctl00_ctl00_ContentPlaceHolder1_periodoLetivoDropDownList_primaDropDownList'
    unidade_id = '#ctl00_ctl00_ContentPlaceHolder1_unidadeDropDownList_primaDropDownList'
    turma_id = '#ctl00_ctl00_ContentPlaceHolder1_turmasDropDownList_primaDropDownList'
    disc_id = '#ctl00_ctl00_ContentPlaceHolder1_disciplinasGruposDropDownList_primaDropDownList'

    print("⚙️ Aplicando filtros (Período, Unidade, Turma, Disciplina)...")
    
    # 1. Período
    try:
        await page.select_option(periodo_id, label=args.periodo)
    except:
        await page.select_option(periodo_id, value='43')
    await page.wait_for_load_state('networkidle')

    # 2. Unidade
    try:
        await page.select_option(unidade_id, label=args.unidade)
    except:
        await page.select_option(unidade_id, value='1')
    await page.wait_for_load_state('networkidle')

    # 3. Turma
    try:
        await page.select_option(turma_id, label=args.turma)
    except:
        await page.select_option(turma_id, value='25582')
    await page.wait_for_load_state('networkidle')

    # 4. Disciplina
    try:
        await page.select_option(disc_id, label=args.disciplina)
    except:
        await page.select_option(disc_id, value='90;0;0')
    await page.wait_for_load_state('networkidle')

    # 5. Datas
    await page.fill('#ctl00_ctl00_ContentPlaceHolder1_dataInicialTextBox', data_frequencia)
    await page.fill('#ctl00_ctl00_ContentPlaceHolder1_dataFinalTextBox', data_frequencia)

    # Buscar
    print("🔍 Clicando em Buscar...")
    await page.evaluate('''() => {
        const btn = document.querySelector("input[value='Buscar']") || document.getElementById("ctl00_ctl00_ContentPlaceHolder1_listarButton");
        if (btn) btn.click();
    }''')
    await page.wait_for_load_state('networkidle')
    await page.wait_for_timeout(3000)

    # Mapear tabela de alunos
    mapping = await page.evaluate('''() => {
        const tables = Array.from(document.querySelectorAll("table"));
        const nameTable = tables.find(t => t.rows.length >= 20 && t.innerText.includes("Angelo"));
        const inputTable = tables.find(t => t.rows.length >= 20 && t.querySelector("input[id*='falta']"));
        
        if (!nameTable || !inputTable) return [];
        
        const nameRows = Array.from(nameTable.rows);
        const inputRows = Array.from(inputTable.rows);
        
        const result = [];
        for (let i = 0; i < Math.min(nameRows.length, inputRows.length); i++) {
            const nameText = nameRows[i].innerText.replace(/\\s+/g, " ").trim();
            const faltaInput = inputRows[i].querySelector("input[id*='falta']");
            if (nameText && faltaInput) {
                result.push({
                    idx: i,
                    fullText: nameText,
                    faltaId: faltaInput.id,
                    checked: faltaInput.checked
                });
            }
        }
        return result;
    }''')
    
    if not mapping:
        print(f"❌ Não foi possível carregar a lista de alunos para a data {data_frequencia}.")
        return

    print(f"✅ Lista carregada: {len(mapping)} alunos encontrados no portal.")
    
    normalized_presents = {normalize_name(name): name for name in present_students}
    presents_count = 0
    absents_count = 0
    unmatched_present_students = list(present_students)
    
    print("\n📝 MARCAÇÃO DE FREQUÊNCIA:")
    for item in mapping:
        portal_text = item['fullText']
        portal_name_norm = normalize_name(portal_text)
        
        is_present = False
        matched_orig_name = None
        
        for p_name_norm, p_name_orig in normalized_presents.items():
            score = match_score(portal_name_norm, p_name_norm)
            if score >= 0.65:
                is_present = True
                matched_orig_name = p_name_orig
                if p_name_orig in unmatched_present_students:
                    unmatched_present_students.remove(p_name_orig)
                break
        
        falta_id = item['faltaId']
        
        if is_present:
            # REGRA: ATIVAR CHECKBOX (MARCAR) PARA PRESENTES
            await page.evaluate(f'''() => {{
                const el = document.getElementById("{falta_id}");
                if (el && !el.checked) {{
                    el.checked = true;
                    el.dispatchEvent(new Event('change', {{bubbles: true}}));
                    el.dispatchEvent(new Event('click', {{bubbles: true}}));
                }}
            }}''')
            print(f"   🟢 PRESENTE (☑️ CHECK ATIVADO) : {portal_text[:42]:<42} | (Planilha: '{matched_orig_name}')")
            presents_count += 1
        else:
            # ALUNO AUSENTE -> DESATIVAR CHECKBOX
            await page.evaluate(f'''() => {{
                const el = document.getElementById("{falta_id}");
                if (el && el.checked) {{
                    el.checked = false;
                    el.dispatchEvent(new Event('change', {{bubbles: true}}));
                    el.dispatchEvent(new Event('click', {{bubbles: true}}));
                }}
            }}''')
            print(f"   🔴 AUSENTE  (☐ DESATIVADO)    : {portal_text[:42]:<42}")
            absents_count += 1

    print(f"\n📊 RESUMO DA DATA {data_frequencia}:")
    print(f"   • Total de alunos na turma : {len(mapping)}")
    print(f"   • Presenças ativadas (☑️): {presents_count}")
    print(f"   • Ausentes desativados (☐): {absents_count}")
    if unmatched_present_students:
        print(f"   ⚠️ Nomes na planilha não associados na turma: {unmatched_present_students}")
        
    try:
        import tempfile
        temp_dir = tempfile.gettempdir()
        screenshot_file = os.path.join(temp_dir, f"sophia_frequencia_{data_frequencia.replace('/', '_')}.png")
        await page.screenshot(path=screenshot_file)
        print(f"📸 Foto da tela salva em: {screenshot_file}")
    except Exception as err_ss:
        print(f"⚠️ Não foi possível salvar captura de tela: {err_ss}")

    # Salvar
    if args.dry_run:
        print("\n⚠️ MODO SIMULAÇÃO (DRY-RUN): O botão Salvar NÃO foi clicado no portal.")
    else:
        print("\n💾 Clicando em Salvar no portal SophiA...")
        saved = await page.evaluate('''() => {
            const btn = document.querySelector("input[value*='Salvar'], input[id*='salvar']") || 
                        Array.from(document.querySelectorAll("input, button, a")).find(e => (e.value || e.innerText || '').includes('Salvar'));
            if (btn) {
                btn.click();
                return true;
            }
            return false;
        }''')
        
        if saved:
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(3000)
            try:
                saved_screenshot = os.path.join(temp_dir, f"sophia_salvo_{data_frequencia.replace('/', '_')}.png")
                await page.screenshot(path=saved_screenshot)
            except Exception:
                pass
            print(f"🎉 FREQUÊNCIA DE {data_frequencia} SALVA COM SUCESSO NO PORTAL SOPHIA!")
        else:
            print("⚠️ Botão Salvar não localizado via automação JS.")

async def run_automation(usuario: str, senha: str, dates_dict: dict, dates_to_process: list, args):
    """Executa a automação no navegador."""
    async with async_playwright() as p:
        print("\n🚀 Conectando ao navegador...")
        browser = await p.chromium.launch(headless=args.headless)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()
        
        try:
            # Aceitar alertas nativos do SophiA (ex: "Sessão já ativa em outro local")
            async def handle_dialog(dialog):
                print(f"💬 Alerta do Portal: '{dialog.message}' (confirmado automaticamente)")
                await dialog.accept()

            page.on('dialog', lambda d: asyncio.create_task(handle_dialog(d)))

            print(f"🌐 Acessando {SOPHIA_URL}...")
            await page.goto(SOPHIA_URL, wait_until='networkidle')
            
            print(f"🔑 Autenticando usuário '{usuario}' no portal SophiA...")
            await page.fill('#txtCodigo', usuario)
            await page.fill('#txtSenha', senha)
            await page.click('#btnEntrar')
            
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(3000)
            
            # Aguarda o campo de código sumir (indicando login bem sucedido)
            try:
                await page.wait_for_selector('#txtCodigo', state='detached', timeout=5000)
            except Exception:
                pass

            # Se a caixa de código ainda existe na tela, o login falhou
            if await page.query_selector('#txtCodigo'):
                err_elem = await page.query_selector('#lblMensagem, .mensagem-erro, span[id*="Erro"], td[style*="color:Red"], div[class*="error"]')
                err_text = await err_elem.inner_text() if err_elem else ""
                
                print(f"\n❌ FALHA NA AUTENTICAÇÃO NO PORTAL SOPHIA!")
                if err_text:
                    print(f"   Mensagem do Portal: \"{err_text.strip()}\"")
                else:
                    print("   O portal não avançou após clicar em Entrar. Verifique se o Código de Usuário e a Senha digitados estão corretos.")
                
                await page.wait_for_timeout(3000)
                await browser.close()
                return

            print("✅ Login realizado com sucesso no portal SophiA!")
            
            for date_str in dates_to_process:
                present_students = dates_dict.get(date_str, [])
                if present_students:
                    await process_attendance_for_date(page, date_str, present_students, args)
                else:
                    print(f"\n⚠️ Nenhuma presença registrada para a data {date_str}. Pulando.")
                    
        except Exception as e:
            err_msg = str(e)
            print(f"\n❌ Ocorreu um erro durante a execução: {err_msg}")
            if "Executable doesn't exist" in err_msg or "playwright install" in err_msg:
                print("⚠️ O navegador Chromium do Playwright ainda não foi instalado neste computador.")
                print("👉 Dica: Execute 'python -m playwright install chromium' no Prompt/CMD.")
            try:
                import tempfile
                err_ss = os.path.join(tempfile.gettempdir(), 'sophia_error.png')
                await page.screenshot(path=err_ss)
            except Exception:
                pass
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()
            print("\n👋 Navegador encerrado com segurança.")

def interactive_wizard(args):
    """Wizard totalmente interativo para qualquer professor configurar o lançamento."""
    print_header()
    
    # 1. SOLICITAR PLANILHA
    print("\n📂 PASSO 1: CAMINHO DA PLANILHA EXCEL DE RESPOSTAS")
    print("----------------------------------------------------------------------")
    file_path = input("👉 Digite ou cole o caminho completo da planilha [.xlsx]: ").strip()
    # Remover aspas se o usuário arrastar e soltar o arquivo no terminal
    file_path = file_path.strip("'\"")
    
    if not file_path:
        default_file = '/home/hamilcar/Antigravity/Formulário sem título (respostas).xlsx'
        if os.path.exists(default_file):
            print(f"ℹ️ Nenhum caminho informado. Utilizando o caminho padrão:\n   {default_file}")
            file_path = default_file
        else:
            print("❌ Caminho da planilha não informado. Encerrando.")
            sys.exit(1)
            
    while not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: '{file_path}'")
        file_path = input("👉 Por favor, digite um caminho válido para o arquivo [.xlsx]: ").strip().strip("'\"")
        if not file_path:
            sys.exit(1)
            
    print(f"✅ Arquivo localizado com sucesso: {os.path.basename(file_path)}")
    args.planilha = file_path

    # Auto-detectar aba e colunas
    sheet_name, date_col, name_col = auto_detect_sheet_and_columns(file_path)
    print(f"  • Aba selecionada  : {sheet_name}")
    print(f"  • Coluna de Data   : {date_col}")
    print(f"  • Coluna de Aluno  : {name_col}")
    
    # Ler datas e presenças
    dates_dict = load_dates_and_presents(file_path, sheet_name, date_col, name_col)
    if not dates_dict:
        print("❌ Nenhuma data ou registro de presença válido foi encontrado na planilha.")
        sys.exit(1)

    # 2. SOLICITAR INTERVALO DE SELEÇÃO DE DIAS
    print("\n📅 PASSO 2: SELEÇÃO DAS DATAS/AULAS PARA REGISTRO")
    print("----------------------------------------------------------------------")
    date_list = list(dates_dict.keys())
    for idx, d_str in enumerate(date_list, 1):
        count = len(dates_dict[d_str])
        print(f"  [{idx}] Data: {d_str} ({count} alunos presentes na planilha)")
    print(f"  [A] Processar TODAS as {len(date_list)} datas acima em lote")
    print("----------------------------------------------------------------------")
    print("💡 Dica: Você pode escolher uma única data (ex: 1), várias (ex: 1,2) ou um intervalo (ex: 1-3).")
    
    user_date_input = input("👉 Digite sua opção de data [ex: 1, 1-2, A]: ").strip().upper()
    
    selected_dates = []
    if user_date_input == 'A' or user_date_input == '':
        selected_dates = date_list
    elif '-' in user_date_input:
        try:
            start_i, end_i = map(int, user_date_input.split('-'))
            selected_dates = date_list[start_i-1 : end_i]
        except:
            selected_dates = date_list
    elif ',' in user_date_input:
        try:
            idxs = [int(i.strip()) for i in user_date_input.split(',')]
            selected_dates = [date_list[i-1] for i in idxs if 1 <= i <= len(date_list)]
        except:
            selected_dates = date_list
    elif user_date_input.isdigit() and 1 <= int(user_date_input) <= len(date_list):
        selected_dates = [date_list[int(user_date_input)-1]]
    else:
        selected_dates = [user_date_input]

    print(f"✅ Data(s) selecionada(s) para registro: {', '.join(selected_dates)}")

    # 3. SOLICITAR LOGIN E SENHA DO PROFESSOR
    print("\n👤 PASSO 3: CREDENCIAIS DE ACESSO AO PORTAL SOPHIA")
    print("----------------------------------------------------------------------")
    usuario = input("👉 Código/Usuário do portal SophiA: ").strip()
    while not usuario:
        usuario = input("👉 O código de usuário é obrigatório: ").strip()
        
    senha = getpass.getpass("👉 Senha do portal SophiA: ").strip()
    while not senha:
        senha = getpass.getpass("👉 A senha é obrigatória: ").strip()

    # 4. MODO DE EXECUÇÃO
    print("\n🛡️  PASSO 4: MODO DE EXECUÇÃO DA AUTOMAÇÃO")
    print("----------------------------------------------------------------------")
    print("  [1] Modo Oficial (Registra e SALVA a chamada no SophiA)")
    print("  [2] Modo Simulação / Teste (Navega e marca na tela sem clicar em Salvar)")
    opt_m = input("👉 Escolha o modo [1 ou 2, Padrão=1]: ").strip()
    if opt_m == '2':
        args.dry_run = True
        print("  -> Modo Simulação ativado.")
    else:
        args.dry_run = False
        print("  -> Modo Oficial ativado (os lançamentos serão salvos).")

    # CONFIRMAÇÃO FINAL
    print("\n" + "="*75)
    print("📋 CONFIRMAÇÃO DOS DADOS DE LANÇAMENTO:")
    print(f"  • Planilha Utilizada : {os.path.basename(file_path)}")
    print(f"  • Datas a Registrar  : {', '.join(selected_dates)}")
    print(f"  • Usuário SophiA     : {usuario}")
    print(f"  • Turma              : {args.turma}")
    print(f"  • Disciplina         : {args.disciplina}")
    print(f"  • Modo de Operação   : {'SIMULAÇÃO (sem salvar)' if args.dry_run else 'OFICIAL (salvar no SophiA)'}")
    print("="*75)
    
    conf = input("🚀 Iniciar lançamento automatizado agora? [S/n]: ").strip().lower()
    if conf and not conf.startswith('s'):
        print("🛑 Operação cancelada pelo usuário.")
        sys.exit(0)

    return usuario, senha, dates_dict, selected_dates

def main():
    parser = argparse.ArgumentParser(description="Automação de Frequência SophiA - Para Professores")
    parser.add_argument("--usuario", type=str, help="Código/Usuário do portal SophiA")
    parser.add_argument("--senha", type=str, help="Senha do portal SophiA")
    parser.add_argument("--data", type=str, help="Data(s) da frequência (ex: 20/08/2026 ou 20/08/2026,27/08/2026)")
    parser.add_argument("--planilha", type=str, help="Caminho completo da planilha Excel")
    parser.add_argument("--periodo", type=str, default="2026.2", help="Período acadêmico")
    parser.add_argument("--unidade", type=str, default="Nova Iguaçu", help="Unidade da instituição")
    parser.add_argument("--turma", type=str, default="S - 2026.2.1P - Análise e Des. de Sistemas", help="Turma")
    parser.add_argument("--disciplina", type=str, default="065 - Programação em PYTHON", help="Disciplina")
    parser.add_argument("--headless", action="store_true", default=True, help="Executa o navegador em modo invisível (padrão: True)")
    parser.add_argument("--headful", dest="headless", action="store_false", help="Exibe a janela do navegador")
    parser.add_argument("--dry-run", action="store_true", help="Executa em modo simulação (sem salvar)")
    
    args = parser.parse_args()
    
    # Se usuário, senha, planilha e data foram passados via linha de comando (modo CLI direto)
    if args.usuario and args.senha and args.planilha and args.data:
        file_path = args.planilha
        sheet_name, date_col, name_col = auto_detect_sheet_and_columns(file_path)
        dates_dict = load_dates_and_presents(file_path, sheet_name, date_col, name_col)
        selected_dates = [d.strip() for d in args.data.split(',')]
        usuario = args.usuario
        senha = args.senha
    else:
        # Modo Wizard Interativo (ideal para qualquer professor)
        usuario, senha, dates_dict, selected_dates = interactive_wizard(args)
        
    asyncio.run(run_automation(usuario, senha, dates_dict, selected_dates, args))

if __name__ == '__main__':
    main()
