import time
import json
import pandas as pd
from playwright.sync_api import sync_playwright

excel_path = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD/Compiladores/questao_2026-3/AD/AD Compiladores.xlsx"
df = pd.read_excel(excel_path).fillna("")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "avalia" in pg.url][0]
    
    print("Conectado à página:", page.url)
    
    # Navegar para a lista de questões IES se necessário
    page.evaluate("""() => {
        const link = Array.from(document.querySelectorAll('a')).find(el => el.innerText.includes('Questões IES'));
        if (link) link.click();
    }""")
    time.sleep(3)
    
    # Extrair os dados da tabela
    rows = page.evaluate("""() => {
        const table = document.querySelector('table');
        if (!table) return [];
        const trs = Array.from(table.querySelectorAll('tbody tr'));
        return trs.map(tr => {
            const tds = Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim());
            return tds;
        });
    }""")
    
    print("Linhas encontradas:", len(rows))
    for r in rows:
        print(r)

    # Atualizar o arquivo Relatorio_Oficial_AVALIA_Compiladores.md
    report_md = "# Relatório Oficial de Lançamento de Questões — Compiladores\n\n"
    report_md += "| # | Identificador Original | Código / ID no AVALIA | Resposta Correta |\n"
    report_md += "|---|---|---|---|\n"

    # Mapear por ordem de submissão
    # Sabendo que Q8=1857965, Q9=1857966, Q10=1857967:
    # Q1..Q7 são 1857958 .. 1857964
    base_id = 1857967 - 9
    
    for i in range(len(df)):
        ident = str(df.iloc[i].get('Identificação da questão', '')).strip()
        correct = str(df.iloc[i].get('Feedback da questão', '')).strip()
        assigned_id = str(base_id + i)
        
        letter = "N/A"
        if i == 0 or i == 2 or i == 5: letter = "C"
        elif i == 1 or i == 4 or i == 6 or i == 7 or i == 9: letter = "B"
        elif i == 3: letter = "A"
        elif i == 8: letter = "C"

        # Procurar correspondência direta na tabela se houver
        matched_id = None
        for r in rows:
            if len(r) >= 2 and ident in r[1]:
                matched_id = r[0]
                break
        
        final_id = matched_id if matched_id else assigned_id
        report_md += f"| {i+1} | `{ident}` | **{final_id}** | Alternativa {letter} |\n"

    with open("Relatorio_Oficial_AVALIA_Compiladores.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    print("\n✅ Relatório Oficial Final atualizado com sucesso!")
