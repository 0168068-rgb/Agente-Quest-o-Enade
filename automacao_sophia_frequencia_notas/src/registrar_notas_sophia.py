#!/usr/bin/env python3
"""
======================================================================
  🎓 AUTOMAÇÃO DE LANÇAMENTO DE NOTAS - PORTAL SOPHIA (UNIVERSAL)
======================================================================
Script genérico e interativo para professores e secretarias acadêmicas.
Lê uma planilha Excel com as notas dos alunos e realiza o lançamento
automático das avaliações (AD, AI, PS, AE) no portal acadêmico SophiA.

Fluxo:
 1. Carrega a planilha Excel e inspeciona a estrutura das colunas.
 2. Pergunta ao usuário qual o seu Curso (valida com a planilha).
 3. Pergunta qual nota será lançada (AD, AI, PS ou AE).
 4. Abre o navegador (visível) no Portal SophiA para o usuário fazer login.
 5. Navega até a aba 'Notas' (LancNotas.aspx).
 6. Percorre as Unidades, Turmas filtradas pelo Curso, e Disciplinas.
 7. Lança as notas com correspondência exata dos alunos.
 8. Salva no portal e gera o relatório final em Excel (Lançados vs Não Lançados).
======================================================================
"""

import os
import sys
import re
import argparse
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

SOPHIA_URL = 'https://portal.sophia.com.br/SophiA_111/Acesso.aspx?escola=8262'

def print_header():
    print("=" * 75)
    print("  🎓 AUTOMAÇÃO DE LANÇAMENTO DE NOTAS - PORTAL SOPHIA")
    print("=" * 75)

def normalize_text(text: str) -> str:
    """Normaliza strings removendo acentos, caracteres especiais e espaços extras (caixa alta)."""
    if not isinstance(text, str) or not text.strip():
        return ''
    nfd_text = unicodedata.normalize('NFD', text.strip())
    ascii_text = ''.join(c for c in nfd_text if unicodedata.category(c) != 'Mn')
    return ' '.join(ascii_text.upper().split())

def match_score(name1: str, name2: str) -> float:
    """Calcula a similaridade entre dois nomes normalizados."""
    norm1 = normalize_text(name1)
    norm2 = normalize_text(name2)
    if norm1 == norm2:
        return 1.0
    if norm1 in norm2 or norm2 in norm1:
        return 0.95
    return SequenceMatcher(None, norm1, norm2).ratio()

def format_grade_value(grade_val) -> str:
    """Formata o valor da nota para a entrada no SophiA (ex: '10,000' -> '10', '8.5' -> '8,5')."""
    if pd.isna(grade_val):
        return ""
    val_str = str(grade_val).strip()
    if not val_str or val_str.lower() == 'nan':
        return ""
    
    # Se for tipo '10,000' ou '9,000' vindo do CSV
    if ',' in val_str and val_str.replace(',', '').isdigit():
        try:
            num = float(val_str.replace(',', '.'))
            if num.is_integer():
                return str(int(num))
            return f"{num:.1f}".replace('.', ',')
        except ValueError:
            pass

    try:
        num = float(val_str.replace(',', '.'))
        if num.is_integer():
            return str(int(num))
        return f"{num:.1f}".replace('.', ',')
    except ValueError:
        return val_str

def load_and_inspect_spreadsheet(file_path: str):
    """Carrega o arquivo Excel/CSV e detecta a aba e colunas principais de forma robusta."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    if file_path.endswith('.csv'):
        df = None
        # Testar diferentes combinações de separadores e codificações para CSVs brasileiros/Excel
        encodings = ['utf-8-sig', 'utf-8', 'latin1', 'cp1252', 'iso-8859-1']
        separators = [';', ',', '\t']
        
        for enc in encodings:
            for sep in separators:
                try:
                    temp_df = pd.read_csv(file_path, sep=sep, encoding=enc, nrows=5)
                    # Se tiver mais de 1 coluna, encontrou o separador correto!
                    if len(temp_df.columns) > 1:
                        df = pd.read_csv(file_path, sep=sep, encoding=enc, on_bad_lines='skip')
                        print(f"✅ CSV lido com sucesso usando separador '{sep}' e codificação '{enc}'")
                        break
                except Exception:
                    continue
            if df is not None:
                break
                
        if df is None:
            # Fallback para engine python
            df = pd.read_csv(file_path, sep=None, engine='python', on_bad_lines='skip')
            
        sheet_name = "CSV"
    else:
        xls = pd.ExcelFile(file_path)
        sheet_name = xls.sheet_names[0]
        for s in xls.sheet_names:
            if any(k in s.lower() for k in ['nota', 'lançamento', 'lancamento', 'resposta', 'aluno']):
                sheet_name = s
                break
        df = pd.read_excel(xls, sheet_name=sheet_name)

    cols = df.columns.tolist()
    print(f"\n📑 Planilha carregada: '{file_path}' (Aba: '{sheet_name}')")
    print(f"📊 Total de registros: {len(df)}")
    print(f"📋 Colunas encontradas: {cols}")

    return df, cols

def find_column(cols: list, keywords: list) -> str:
    """Busca por palavra-chave na lista de colunas com prioridade para correspondência exata."""
    # 1ª Passada: Correspondência exata (case-insensitive)
    for k in keywords:
        for c in cols:
            if str(c).strip().lower() == k.lower():
                return c

    # 2ª Passada: Palavra completa / isolada no nome da coluna
    for k in keywords:
        for c in cols:
            words = [w.strip() for w in str(c).strip().lower().replace('_', ' ').split()]
            if k.lower() in words:
                return c

    # 3ª Passada: Substring genérica (apenas para termos com mais de 2 letras para evitar falsos positivos)
    for k in keywords:
        if len(k) <= 2:
            continue
        for c in cols:
            if k.lower() in str(c).lower():
                return c

    return None

async def wait_for_user_login(page):
    """Abre a tela de login e aguarda o usuário autenticar-se manualmente."""
    print(f"\n🌐 Abrindo Portal SophiA: {SOPHIA_URL}")
    await page.goto(SOPHIA_URL, wait_until='networkidle')

    print("\n" + "🔑 " + "="*65)
    print("👉 POR FAVOR, REALIZE O LOGIN NA JANELA DO NAVEGADOR QUE FOI ABERTA.")
    print("   O script detectará automaticamente quando você entrar no sistema...")
    print("="*67 + "\n")

    while True:
        await asyncio.sleep(2)
        try:
            url = page.url
            if 'Acesso.aspx' not in url:
                print("✅ Login detectado (navegação pós-autenticação)! Prosseguindo...")
                break
            
            content = await page.content()
            if any(term in content for term in ['Notas', 'Frequência', 'Trocar senha', 'Sair', 'Olát', 'Olá']):
                print("✅ Login detectado com sucesso! Prosseguindo...")
                break
        except Exception:
            # Durante o POST/Redirect a página pode estar mudando de estado. Ignora o erro temporário e tenta novamente.
            continue

async def navigate_to_notas(page):
    """Navega até a tela de lançamento de notas."""
    print("📌 Navegando para a aba 'Notas'...")
    try:
        await page.click('text=Notas', timeout=5000)
    except Exception:
        # Obter URL base (ex: https://portal.sophia.com.br/SophiA_111/)
        base_url = '/'.join(page.url.split('/')[:4])
        await page.goto(f"{base_url}/LancNotas.aspx", wait_until='networkidle')

    await page.wait_for_load_state('networkidle')
    await page.wait_for_timeout(2000)

    if 'LancNotas' not in page.url:
        base_url = '/'.join(page.url.split('/')[:4])
        await page.goto(f"{base_url}/LancNotas.aspx", wait_until='networkidle')
        await page.wait_for_timeout(2000)

async def reset_page_via_notas_tab(page):
    """Reseta a tela clicando na aba 'Notas' para restaurar o estado limpo do formulário e reaparecer o botão 'Buscar'."""
    print("🔄 Clicando na aba 'Notas' para restaurar a tela e o botão 'Buscar'...")
    await navigate_to_notas(page)

async def find_sophiA_selects(page):
    """Encontra dinamicamente os seletores CSS dos 5 dropdowns da tela LancNotas.aspx."""
    await page.wait_for_selector("select", timeout=15000)
    selectors = await page.evaluate('''() => {
        const selects = Array.from(document.querySelectorAll("select"));
        
        const findByKeyword = (kw, defaultIdx) => {
            let s = selects.find(el => (el.id || '').toLowerCase().includes(kw) || (el.name || '').toLowerCase().includes(kw));
            if (!s && selects[defaultIdx]) s = selects[defaultIdx];
            if (!s) return null;
            return s.id ? '#' + CSS.escape(s.id) : (s.name ? `select[name="${s.name}"]` : null);
        };

        return {
            periodo: findByKeyword('periodo', 0),
            unidade: findByKeyword('unidade', 1),
            turma: findByKeyword('turma', 2),
            etapa: findByKeyword('etapa', 3),
            disciplina: findByKeyword('disciplina', 4)
        };
    }''')
    return selectors

async def get_dropdown_options(page, selector):
    """Retorna a lista de opções ({text, value}) de um dropdown."""
    if not selector:
        return []
    try:
        return await page.evaluate(f'''(sel) => {{
            const el = document.querySelector(sel);
            if (!el) return [];
            return Array.from(el.options)
                .filter(o => o.value && o.value !== "0" && o.value !== "-1" && o.text.trim() !== "Selecione...")
                .map(o => ({{ text: o.text.trim(), value: o.value }}));
        }}''', selector)
    except Exception:
        return []

def turma_matches_course(turma_text: str, course_name_input: str) -> bool:
    """Verifica se a opção de Turma do SophiA corresponde ao Curso do usuário."""
    if not turma_text or not course_name_input:
        return False

    t_norm = normalize_text(turma_text)
    raw_courses = [c.strip() for c in course_name_input.replace(';', ',').replace('/', ',').split(',') if c.strip()]

    for c_raw in raw_courses:
        c_norm = normalize_text(c_raw)
        if not c_norm:
            continue

        if c_norm in t_norm or t_norm in c_norm:
            return True

        # Palavras-chave principais (ex: 'Análise e Des. de Sist' vs 'Superior de Tecnologia em Gestão de...')
        c_words = set(w for w in c_norm.split() if len(w) > 2 and w not in ['SUPERIOR', 'TECNOLOGIA', 'GRADUACAO', 'EAD', 'BACHARELADO', 'LICENCIATURA', 'DE', 'DOS', 'DAS', 'EM'])
        t_words = set(w for w in t_norm.split() if len(w) > 2 and w not in ['SUPERIOR', 'TECNOLOGIA', 'GRADUACAO', 'EAD', 'BACHARELADO', 'LICENCIATURA', 'DE', 'DOS', 'DAS', 'EM'])

        common = c_words.intersection(t_words)
        if len(common) >= 1:
            return True

    return False

def student_matches(excel_name: str, excel_ra: str, portal_name: str, portal_code: str, portal_title: str) -> bool:
    """Combina RA/Matrícula, Título completo e Nomes normalizados (mesmo truncados com '...')."""
    # 1. Correspondência por RA / Código
    if excel_ra and portal_code:
        ra_ex = ''.join(filter(str.isdigit, str(excel_ra)))
        ra_po = ''.join(filter(str.isdigit, str(portal_code)))
        if ra_ex and ra_po and (ra_ex == ra_po or ra_ex in ra_po or ra_po in ra_ex):
            return True

    n_excel = normalize_text(excel_name)
    n_portal = normalize_text(portal_name.replace('...', ''))
    n_title = normalize_text(portal_title) if portal_title else ""

    if not n_excel:
        return False

    # 2. Tentar pelo title do HTML
    if n_title:
        if n_excel == n_title or n_excel in n_title or n_title in n_excel:
            return True

    # 3. Se o nome do portal estiver cortado/truncado (ex: 'FABIANO HENRIQUE CARMINATTI JU...')
    if n_portal and len(n_portal) >= 5:
        if n_portal in n_excel or n_excel in n_portal:
            return True

    # 4. Score de similaridade
    score = match_score(n_excel, n_portal)
    return score >= 0.70

async def safe_select_option(page, selector, value):
    """Seleciona uma opção no dropdown garantindo a re-habilitação em controles ASP.NET WebForms."""
    if not selector or not value:
        return
    try:
        await page.evaluate(f'''(sel) => {{
            const el = document.querySelector(sel);
            if (el) {{
                el.removeAttribute('disabled');
                el.disabled = false;
            }}
        }}''', selector)
    except Exception:
        pass

    try:
        await page.select_option(selector, value=value, timeout=5000)
    except Exception:
        await page.evaluate(f'''({{sel, val}}) => {{
            const el = document.querySelector(sel);
            if (el) {{
                el.removeAttribute('disabled');
                el.disabled = false;
                el.value = val;
                el.dispatchEvent(new Event('change', {{bubbles: true}}));
                if (typeof __doPostBack === 'function') {{
                    const name = el.name || el.id;
                    try {{ __doPostBack(name, ''); }} catch(e) {{}}
                }}
            }}
        }}''', {'sel': selector, 'val': value})

    await page.wait_for_load_state('networkidle')
    await page.wait_for_timeout(1000)

async def process_grade_launch(page, df_grades: pd.DataFrame, course_name: str, grade_type: str, col_name: str, col_course: str, col_disc: str, col_grade: str, col_ra: str = None, col_polo: str = None, target_period_str: str = "2026.2", dry_run: bool = False):
    """Função principal de varredura e lançamento de notas no portal SophiA."""
    print("\n🔍 Inspecionando seletores da tela de Notas...")
    selects = await find_sophiA_selects(page)

    periodo_sel = selects['periodo']
    unidade_sel = selects['unidade']
    turma_sel = selects['turma']
    etapa_sel = selects['etapa']
    disc_sel = selects['disciplina']

    print(f"✅ Seletores identificados: Período ({periodo_sel}), Unidade ({unidade_sel}), Turma ({turma_sel}), Etapa ({etapa_sel}), Disciplina ({disc_sel})")

    relatorio_sucesso = []
    relatorio_nao_encontrado_web = []
    relatorio_nao_encontrado_planilha = []

    # 1. Selecionar o Período atual (ex: 2026.2 ou o mais recente da lista)
    target_periodo = None
    periodo_opts = await get_dropdown_options(page, periodo_sel)
    if periodo_opts:
        for p in periodo_opts:
            if target_period_str.lower() in p['text'].lower():
                target_periodo = p
                break

        if not target_periodo:
            target_periodo = sorted(periodo_opts, key=lambda x: x['text'], reverse=True)[0]

        print(f"📅 Selecionando Período: '{target_periodo['text']}'")
        await safe_select_option(page, periodo_sel, value=target_periodo['value'])

    # 2. Obter Unidades disponíveis
    unidades_opts = await get_dropdown_options(page, unidade_sel)
    if not unidades_opts:
        print("⚠️ Nenhuma unidade encontrada. Tentando selecionar unidade padrão...")
        unidades_opts = [{'text': 'Unidade Padrão', 'value': ''}]

    page_was_reset = False

    for un in unidades_opts:
        if un['value']:
            print(f"\n🏢 Selecionando Unidade: '{un['text']}'...")
            selects = await find_sophiA_selects(page)
            await safe_select_option(page, selects['unidade'], value=un['value'])

        # 3. Obter Turmas e filtrar pelo Curso informado pelo usuário
        turmas_opts = await get_dropdown_options(page, selects['turma'])
        matching_turmas = [t for t in turmas_opts if turma_matches_course(t['text'], course_name)]

        if not matching_turmas:
            print(f"ℹ️ Nenhuma turma referente ao curso '{course_name}' encontrada na unidade '{un['text']}'.")
            continue

        print(f"✅ Encontrada(s) {len(matching_turmas)} turma(s) para o curso em '{un['text']}': {[t['text'] for t in matching_turmas]}")

        for turma in matching_turmas:
            print(f"\n👥 Selecionando Turma: '{turma['text']}'...")

            if page_was_reset:
                selects = await find_sophiA_selects(page)
                if target_periodo:
                    await safe_select_option(page, selects['periodo'], value=target_periodo['value'])
                if un['value']:
                    await safe_select_option(page, selects['unidade'], value=un['value'])
                page_was_reset = False

            await safe_select_option(page, selects['turma'], value=turma['value'])

            # 4. Selecionar Etapa = "Semestre"
            etapa_opts = await get_dropdown_options(page, selects['etapa'])
            semestre_etapa = next((e for e in etapa_opts if 'semestre' in e['text'].lower()), None)
            if semestre_etapa:
                await safe_select_option(page, selects['etapa'], value=semestre_etapa['value'])

            # 5. Obter Disciplinas disponíveis para esta turma
            disc_opts = await get_dropdown_options(page, selects['disciplina'])
            if not disc_opts:
                print(f"⚠️ Nenhuma disciplina cadastrada para a turma '{turma['text']}'.")
                continue

            for disc_idx, disc in enumerate(disc_opts):
                # Se a tela foi resetada anteriormente pela aba 'Notas', re-selecionar os filtros no SophiA
                if page_was_reset:
                    selects = await find_sophiA_selects(page)
                    if target_periodo:
                        await safe_select_option(page, selects['periodo'], value=target_periodo['value'])
                    if un['value']:
                        await safe_select_option(page, selects['unidade'], value=un['value'])
                    await safe_select_option(page, selects['turma'], value=turma['value'])

                    etapa_opts = await get_dropdown_options(page, selects['etapa'])
                    semestre_etapa = next((e for e in etapa_opts if 'semestre' in e['text'].lower()), None)
                    if semestre_etapa:
                        await safe_select_option(page, selects['etapa'], value=semestre_etapa['value'])

                    disc_opts_updated = await get_dropdown_options(page, selects['disciplina'])
                    if disc_idx < len(disc_opts_updated):
                        disc = disc_opts_updated[disc_idx]

                    page_was_reset = False

                # 🔍 FILTRAGEM NA PLANILHA NA ORDEM EXATA: CURSOS => DISCIPLINA => POLO
                # Step 1: Cursos
                if col_course and col_course in df_grades.columns and course_name:
                    df_step1_cursos = df_grades[df_grades[col_course].apply(lambda x: turma_matches_course(str(x), course_name))]
                else:
                    df_step1_cursos = df_grades

                # Step 2: Disciplina
                if col_disc and col_disc in df_step1_cursos.columns:
                    disc_norm = normalize_text(disc['text'])
                    # 1º: correspondência EXATA do nome da disciplina (evita 'Projeto de Redes...' casar com 'Redes...')
                    df_step2_disc = df_step1_cursos[df_step1_cursos[col_disc].apply(lambda x: normalize_text(str(x)) == disc_norm)]
                    # 2º: fallback apenas por similaridade alta (pequenas diferenças de grafia), sem regra de "contido"
                    if df_step2_disc.empty:
                        df_step2_disc = df_step1_cursos[df_step1_cursos[col_disc].apply(
                            lambda x: SequenceMatcher(None, normalize_text(str(x)), disc_norm).ratio() >= 0.90)]
                else:
                    df_step2_disc = df_step1_cursos

                # Step 3: Polo / Unidade (Robusto contra descolamento de colunas do CSV)
                if un['text'] and un['text'] != 'Unidade Padrão':
                    polo_norm = normalize_text(un['text'])
                    def row_matches_polo(row):
                        if not polo_norm:
                            return True
                        for col_key in [col_polo, 'NotaExportadaAcademico', 'CampusPolo']:
                            if col_key and col_key in row:
                                val_norm = normalize_text(str(row[col_key]))
                                if polo_norm in val_norm or val_norm in polo_norm:
                                    return True
                        full_row_norm = normalize_text(' '.join(str(v) for v in row.values))
                        return polo_norm in full_row_norm

                    sub_df = df_step2_disc[df_step2_disc.apply(row_matches_polo, axis=1)]
                else:
                    sub_df = df_step2_disc

                if sub_df.empty:
                    print(f"\n📚 Disciplina: '{disc['text']}' - ℹ️ Nenhum aluno na planilha (após filtro Cursos => Disciplina => Polo). Avançando...")
                    continue

                print(f"\n📚 Selecionando Disciplina/Grupo: '{disc['text']}'")
                await safe_select_option(page, selects['disciplina'], value=disc['value'])
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(1000)

                # 6. Aguardar o botão 'Buscar' ser renderizado e ficar visível pós-PostBack
                print("⏳ Aguardando o botão 'Buscar' ser renderizado na tela...")
                try:
                    await page.wait_for_function('''() => {
                        let btn = document.querySelector("input[value*='Buscar']") || 
                                  document.querySelector("input[id*='buscar']") ||
                                  document.querySelector("input[id*='listar']") ||
                                  document.querySelector("input[id*='Listar']");
                        if (!btn) {
                            btn = Array.from(document.querySelectorAll("input, button, a")).find(el => {
                                const val = (el.value || el.innerText || '').trim();
                                return val.includes('Buscar') || val.includes('Listar');
                            });
                        }
                        return btn && btn.offsetWidth > 0 && btn.offsetHeight > 0 && !btn.disabled;
                    }''', timeout=15000)
                except Exception:
                    print("⚠️ O botão 'Buscar' demorou para responder, tentando forçar o clique...")

                print("🔍 Clicando em 'Buscar'...")
                await page.evaluate('''() => {
                    let btn = document.querySelector("input[value*='Buscar']") || 
                              document.querySelector("input[id*='buscar']") ||
                              document.querySelector("input[id*='listar']") ||
                              document.querySelector("input[id*='Listar']");
                    if (!btn) {
                        btn = Array.from(document.querySelectorAll("input, button, a")).find(el => {
                            const val = (el.value || el.innerText || '').trim();
                            return val.includes('Buscar') || val.includes('Listar');
                        });
                    }
                    if (btn) btn.click();
                }''')
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(3000)

                # 7. Mapear a tabela de alunos e identificar a coluna referente à avaliação (AD, AI, PS, AE)
                grid_info = await page.evaluate(f'''(targetGrade) => {{
                    const tables = Array.from(document.querySelectorAll("table"));
                    let mainTable = tables.find(t => t.innerText.includes("Código") && t.innerText.includes("Nome"));
                    if (!mainTable) mainTable = tables.find(t => t.rows.length >= 2);
                    if (!mainTable) return null;

                    const rows = Array.from(mainTable.rows);
                    if (rows.length < 2) return null;

                    const headerRow = rows[0];
                    const headerCells = Array.from(headerRow.cells).map(c => c.innerText.trim().toUpperCase());

                    let gradeColIdx = -1;
                    for (let i = 0; i < headerCells.length; i++) {{
                        if (headerCells[i] === targetGrade.toUpperCase() || headerCells[i].includes(targetGrade.toUpperCase())) {{
                            gradeColIdx = i;
                            break;
                        }}
                    }}

                    const studentData = [];
                    for (let i = 1; i < rows.length; i++) {{
                        const cells = rows[i].cells;
                        if (cells.length <= 2) continue;

                        const textContent = rows[i].innerText.replace(/\\s+/g, ' ').trim();
                        let codeCellText = cells[0] ? cells[0].innerText.trim() : "";
                        let nameCellText = "";
                        let titleText = "";

                        if (cells.length > 2) {{
                            nameCellText = cells[2].innerText.trim();
                            titleText = cells[2].getAttribute("title") || 
                                        (cells[2].querySelector("*[title]") ? cells[2].querySelector("*[title]").getAttribute("title") : "");
                        }}

                        const inputs = Array.from(rows[i].querySelectorAll("input[type='text']"));
                        let targetInputId = null;
                        if (inputs.length > 0) {{
                            if (gradeColIdx !== -1 && inputs[gradeColIdx]) {{
                                targetInputId = inputs[gradeColIdx].id;
                            }} else {{
                                targetInputId = inputs[0].id;
                            }}
                        }}

                        studentData.push({{
                            rowIndex: i,
                            fullRowText: textContent,
                            studentCode: codeCellText,
                            studentName: nameCellText,
                            studentTitle: titleText,
                            inputId: targetInputId
                        }});
                    }}

                    return {{
                        headerFound: gradeColIdx !== -1,
                        gradeColIdx: gradeColIdx,
                        students: studentData
                    }};
                }}''', grade_type)

                # 📌 1ª SITUAÇÃO: Quando não aparecer aluno no portal WEB
                if not grid_info or not grid_info['students']:
                    print(f"⚠️ Não foi possível encontrar/mapear alunos no portal para a disciplina '{disc['text']}'.")
                    print("📌 SITUAÇÃO 1 DETECTADA (Nenhum aluno exibido): Clicando na aba 'Notas' para restaurar a tela e o botão 'Buscar'...")
                    await reset_page_via_notas_tab(page)
                    page_was_reset = True
                    continue

                print(f"📋 Alunos encontrados no portal: {len(grid_info['students'])}")

                # 8. Realizar o lançamento das notas
                launched_count = 0
                matched_web_indices = set()

                for _, row in sub_df.iterrows():
                    student_raw_name = str(row[col_name]).strip()
                    student_ra_val = row[col_ra] if (col_ra and col_ra in row) else None
                    grade_val = row[col_grade]

                    matched_portal_student = None

                    # Correspondência flexível + RA + Title + Nome Truncado
                    for idx_st, st in enumerate(grid_info['students']):
                        if student_matches(student_raw_name, student_ra_val, st['studentName'], st['studentCode'], st['studentTitle']):
                            matched_portal_student = st
                            matched_web_indices.add(idx_st)
                            break

                    if matched_portal_student:
                        if pd.isna(grade_val) or str(grade_val).strip() == '':
                            print(f"   ℹ️ ALUNO ENCONTRADO (SEM NOTA NA PLANILHA): {student_raw_name}")
                            relatorio_nao_encontrado_web.append({
                                'Aluno Planilha': student_raw_name,
                                'RA Planilha': student_ra_val,
                                'Turma': turma['text'],
                                'Disciplina': disc['text'],
                                'Avaliação': grade_type,
                                'Nota Planilha': grade_val,
                                'Motivo': 'Nota em branco/ausente na planilha'
                            })
                            continue

                        input_id = matched_portal_student['inputId']
                        grade_str = format_grade_value(grade_val)
                        if not grade_str:
                            relatorio_nao_encontrado_web.append({
                                'Aluno Planilha': student_raw_name,
                                'RA Planilha': student_ra_val,
                                'Turma': turma['text'],
                                'Disciplina': disc['text'],
                                'Avaliação': grade_type,
                                'Nota Planilha': grade_val,
                                'Motivo': 'Nota inválida/em branco'
                            })
                            continue

                        # Preencher o campo no portal
                        if input_id:
                            await page.evaluate(f'''({{id, val}}) => {{
                                const el = document.getElementById(id);
                                if (el) {{
                                    el.value = val;
                                    el.dispatchEvent(new Event('input', {{bubbles: true}}));
                                    el.dispatchEvent(new Event('change', {{bubbles: true}}));
                                    el.dispatchEvent(new Event('blur', {{bubbles: true}}));
                                }}
                            }}''', {'id': input_id, 'val': grade_str})

                            print(f"   🟢 NOTA LANÇADA ({grade_type}): {student_raw_name:<35} -> Nota: {grade_str}")
                            launched_count += 1
                            relatorio_sucesso.append({
                                'Aluno': student_raw_name,
                                'RA': student_ra_val,
                                'Turma': turma['text'],
                                'Disciplina': disc['text'],
                                'Avaliação': grade_type,
                                'Nota Lançada': grade_str,
                                'Status': 'Sucesso'
                            })
                    else:
                        if pd.isna(grade_val) or str(grade_val).strip() == '':
                            motivo_str = 'Aluno não localizado na Web e sem nota na planilha'
                        else:
                            motivo_str = 'Aluno não localizado na turma/disciplina do portal'

                        print(f"   🔴 NA PLANILHA, MAS NÃO NO PORTAL WEB: {student_raw_name}")
                        relatorio_nao_encontrado_web.append({
                            'Aluno Planilha': student_raw_name,
                            'RA Planilha': student_ra_val,
                            'Turma': turma['text'],
                            'Disciplina': disc['text'],
                            'Avaliação': grade_type,
                            'Nota Planilha': grade_val,
                            'Motivo': motivo_str
                        })

                # Rastrear alunos que existem no PORTAL WEB mas NÃO estavam na PLANILHA
                for idx_st, st in enumerate(grid_info['students']):
                    if idx_st not in matched_web_indices:
                        web_student_name = st['studentTitle'] or st['studentName'] or st['fullRowText']
                        print(f"   🟡 NO PORTAL WEB, MAS NÃO NA PLANILHA : {web_student_name}")
                        relatorio_nao_encontrado_planilha.append({
                            'Aluno Portal WEB': web_student_name,
                            'Código/RA WEB': st['studentCode'],
                            'Turma': turma['text'],
                            'Disciplina': disc['text'],
                            'Status Portal': 'Cadastrado no SophiA (Sem nota na planilha)'
                        })

                # 9. Salvar as notas no portal
                if launched_count > 0:
                    if dry_run:
                        print(f"⚠️ MODO SIMULAÇÃO: {launched_count} nota(s) preenchida(s) mas o botão 'Gravar'/'Salvar' não foi clicado.")
                    else:
                        print("\n💾 Clicando no botão 'Gravar'/'Salvar' no SophiA...")
                        saved = await page.evaluate('''() => {
                            let btn = document.querySelector("input[value*='Salvar']") ||
                                      document.querySelector("input[value*='Gravar']") ||
                                      document.querySelector("input[id*='salvar']") ||
                                      document.querySelector("input[id*='gravar']") ||
                                      document.querySelector("input[id*='Salvar']") ||
                                      document.querySelector("input[id*='Gravar']");
                            if (!btn) {
                                btn = Array.from(document.querySelectorAll("input, button, a")).find(el => {
                                    const val = (el.value || el.innerText || '').trim();
                                    return val.includes('Salvar') || val.includes('Gravar');
                                });
                            }
                            if (btn) {
                                btn.click();
                                return true;
                            }
                            return false;
                        }''')
                        if saved:
                            await page.wait_for_load_state('networkidle')
                            await page.wait_for_timeout(2000)
                            print("✅ Alterações gravadas/salvas com sucesso!")

                # 📌 2ª SITUAÇÃO: Resetar a tela pela aba 'Notas' após concluir o lançamento / gravação da disciplina
                print("📌 SITUAÇÃO 2 DETECTADA (Fim do lançamento da disciplina): Clicando na aba 'Notas' para restaurar a tela...")
                await reset_page_via_notas_tab(page)
                page_was_reset = True


    # Exportar relatório em 3 abas de Excel ao final
    output_report = "relatorio_lancamento_notas.xlsx"
    with pd.ExcelWriter(output_report, engine='openpyxl') as writer:
        df1 = pd.DataFrame(relatorio_sucesso) if relatorio_sucesso else pd.DataFrame(columns=['Aluno', 'RA', 'Turma', 'Disciplina', 'Avaliação', 'Nota Lançada', 'Status'])
        df2 = pd.DataFrame(relatorio_nao_encontrado_web) if relatorio_nao_encontrado_web else pd.DataFrame(columns=['Aluno Planilha', 'RA Planilha', 'Turma', 'Disciplina', 'Avaliação', 'Nota Planilha', 'Motivo'])
        df3 = pd.DataFrame(relatorio_nao_encontrado_planilha) if relatorio_nao_encontrado_planilha else pd.DataFrame(columns=['Aluno Portal WEB', 'Código/RA WEB', 'Turma', 'Disciplina', 'Status Portal'])

        df1.to_excel(writer, sheet_name='Lançados na Web', index=False)
        df2.to_excel(writer, sheet_name='Na Planilha (Sem Web)', index=False)
        df3.to_excel(writer, sheet_name='Na Web (Sem Planilha)', index=False)

    print("\n" + "="*75)
    print("📊 RESUMO CONSOLIDADO DO PROCESSAMENTO:")
    print("="*75)
    print(f"🟢 Alunos encontrados na planilha e LANÇADOS na WEB : {len(relatorio_sucesso)}")
    print(f"🔴 Alunos na planilha, mas NÃO encontrados na WEB  : {len(relatorio_nao_encontrado_web)}")
    print(f"🟡 Alunos no Portal WEB, mas NÃO na planilha       : {len(relatorio_nao_encontrado_planilha)}")
    print("-" * 75)
    print(f"📁 Relatório detalhado de auditoria gerado em: {os.path.abspath(output_report)}")
    print("="*75)

async def main():
    print_header()

    parser = argparse.ArgumentParser(description="Automação de Lançamento de Notas no Portal SophiA")
    parser.add_argument("--periodo", type=str, default="2026.2", help="Período letivo a selecionar (padrão: 2026.2)")
    parser.add_argument("--planilha", type=str, help="Caminho do arquivo Excel/CSV de notas")
    parser.add_argument("--curso", type=str, help="Nome do Curso a ser processado")
    parser.add_argument("--prova", type=str, choices=['AD', 'AI', 'PS', 'AE'], help="Tipo de nota a lançar (AD, AI, PS, AE)")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem clicar no botão Salvar")

    args = parser.parse_args()

    # Interatividade CLI para parâmetros ausentes
    file_path = args.planilha
    while not file_path or not os.path.exists(file_path):
        file_path = input("👉 Digite ou arraste o caminho da PLANILHA de notas (Excel/CSV): ").strip().strip('"').strip("'")
        if not os.path.exists(file_path):
            print("❌ Arquivo não encontrado. Tente novamente.")

    df_grades, cols = load_and_inspect_spreadsheet(file_path)

    # Identificar colunas
    col_name = find_column(cols, ['nome', 'aluno', 'estudante', 'matricula', 'ra'])
    if not col_name:
        print("\n📋 Colunas disponíveis na planilha:")
        for idx, c in enumerate(cols, 1):
            print(f"  [{idx}] {c}")
        idx_n = input("👉 Escolha o número da coluna referente ao NOME DO ALUNO: ").strip()
        col_name = cols[int(idx_n)-1] if idx_n.isdigit() and 1 <= int(idx_n) <= len(cols) else cols[0]

    col_course = find_column(cols, ['cursomatricula', 'cursoturma', 'curso', 'programa', 'habilitação'])
    col_disc = find_column(cols, ['disciplina', 'materia', 'modulo', 'grupo'])

    # Pergunta 3º: Curso
    course_name = args.curso
    cursos_unicos = []
    if col_course and col_course in df_grades.columns:
        cursos_unicos = [str(c).strip() for c in df_grades[col_course].dropna().unique() if str(c).strip()]

    if not course_name:
        if cursos_unicos:
            print("\n🎓 Cursos encontrados na planilha:")
            for idx, c in enumerate(cursos_unicos, 1):
                print(f"  [{idx:<2}] {c}")
            course_input = input("\n👉 Digite o NÚMERO ou NOME DO CURSO (ex: 17 ou 'Análise e Desenvolvimento'): ").strip()

            # Extrair qualquer número presente na entrada (ex: '17; 3;14 e 28' -> [17, 3, 14, 28])
            digits = [int(d) for d in re.findall(r'\d+', course_input)]
            valid_indices = [d for d in digits if 1 <= d <= len(cursos_unicos)]

            if valid_indices:
                # Manter ordem única preservando sequência digitada
                seen = set()
                selected_courses = [cursos_unicos[i-1] for i in valid_indices if not (i in seen or seen.add(i))]
                course_name = "; ".join(selected_courses)
                print(f"✅ Curso(s) selecionado(s): {selected_courses}")
            else:
                # Tentar correspondência flexível por nome/abreviação
                matched = [c for c in cursos_unicos if turma_matches_course(c, course_input)]
                if matched:
                    course_name = "; ".join(matched)
                    print(f"✅ Curso(s) identificado(s) na planilha: {matched}")
                else:
                    course_name = course_input
        else:
            course_name = input("👉 Informe o seu CURSO (conforme cadastrado no SophiA): ").strip()

    # Validar se curso existe na planilha
    if cursos_unicos:
        matched = [c for c in cursos_unicos if turma_matches_course(c, course_name)]
        if not matched:
            print(f"\n⚠️ ATENÇÃO: Nenhum curso na planilha coincidiu exatamente com '{course_name}'.")
            confirm = input("Deseja continuar mesmo assim? [s/N]: ").strip().lower()
            if confirm != 's':
                print("Operação cancelada pelo usuário.")
                sys.exit(0)

    # Pergunta 4º: Tipo de Prova (AD, AI, PS, AE)
    grade_type = args.prova
    if not grade_type:
        print("\n📝 Escolha o tipo de nota que deseja lançar:")
        print("  [1] AD (Avaliação Desempenho)")
        print("  [2] AI (Avaliação Integrada)")
        print("  [3] PS (Prova Substitutiva)")
        print("  [4] AE (Avaliação Especial)")
        opcao_prova = input("👉 Selecione a opção (1-4) [Padrão: 1 - AD]: ").strip()
        mapa_provas = {'1': 'AD', '2': 'AI', '3': 'PS', '4': 'AE'}
        grade_type = mapa_provas.get(opcao_prova, 'AD')

    # Identificar coluna da nota na planilha
    col_grade = find_column(cols, [grade_type.lower(), f"nota {grade_type.lower()}", f"nota_{grade_type.lower()}"])
    if not col_grade:
        print(f"\n⚠️ Não foi encontrada uma coluna exata chamada '{grade_type}' na planilha.")
        for idx, c in enumerate(cols, 1):
            print(f"  [{idx}] {c}")
        idx_g = input(f"👉 Escolha o número da coluna referente à NOTA DA {grade_type}: ").strip()
        col_grade = cols[int(idx_g)-1] if idx_g.isdigit() and 1 <= int(idx_g) <= len(cols) else cols[-1]

    # Pergunta Modo de Execução (Real vs Simulação)
    dry_run = args.dry_run
    if not dry_run:
        print("\n🧪 MODO DE EXECUÇÃO:")
        print("  [1] Lançamento Real (Preenche e Salva as notas no SophiA)")
        print("  [2] Simulação / Teste (Preenche na tela para você conferir, mas NÃO Clica em Salvar)")
        mod_opt = input("👉 Escolha a opção (1 ou 2) [Padrão: 2 - Simulação/Teste]: ").strip()
        dry_run = False if mod_opt == '1' else True

    modo_txt = "🧪 SIMULAÇÃO / TESTE (Sem Salvar)" if dry_run else "💾 REAL (Com Salvamento)"

    print("\n" + "🚀 " + "="*65)
    print("CONFIGURAÇÃO DE LANÇAMENTO:")
    print(f"  • Modo         : {modo_txt}")
    print(f"  • Planilha     : {file_path}")
    print(f"  • Coluna Nome  : {col_name}")
    print(f"  • Curso Alvo   : {course_name}")
    print(f"  • Prova/Nota   : {grade_type} (Coluna: '{col_grade}')")
    print("="*67 + "\n")

    # Iniciar Playwright e Automação Web
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--no-sandbox"]
        )
        context = await browser.new_context(viewport=None)
        page = await context.new_page()

        # Passo 5º: Solicitar login
        await wait_for_user_login(page)

        # Passo 6º: Ir para a tela de Notas
        await navigate_to_notas(page)

        col_ra = find_column(cols, ['ra', 'matricula', 'código', 'codigo'])
        col_polo = find_column(cols, ['campuspolo', 'polo', 'unidade', 'campus'])

        # Passos 7º a 12º: Processar lançamento e relatórios
        await process_grade_launch(
            page=page,
            df_grades=df_grades,
            course_name=course_name,
            grade_type=grade_type,
            col_name=col_name,
            col_course=col_course,
            col_disc=col_disc,
            col_grade=col_grade,
            col_ra=col_ra,
            col_polo=col_polo,
            target_period_str=args.periodo,
            dry_run=dry_run
        )

        await page.wait_for_timeout(3000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
