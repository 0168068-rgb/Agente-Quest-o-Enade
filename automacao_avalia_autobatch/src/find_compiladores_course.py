import time
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    pages = [pg for pg in b.contexts[0].pages if "avalia" in pg.url]
    if not pages:
        print("Nenhuma página AVALIA encontrada.")
        exit(1)

    page = pages[0]
    
    # 1. Obter todas as opções do dropdown de Cursos
    cursos = page.evaluate("""() => {
        const select = document.getElementById('idCurso');
        return Array.from(select.options).map(o => ({ value: o.value, text: o.text })).filter(o => o.value);
    }""")
    
    print(f"Buscando 'Compiladores' entre {len(cursos)} cursos registrados...")
    
    found_course = None
    for c in cursos:
        # Selecionar o curso
        page.evaluate("""(cVal) => {
            const select = document.getElementById('idCurso');
            select.value = cVal;
            select.dispatchEvent(new Event('change', { bubbles: true }));
            if (typeof $ !== 'undefined') $(select).trigger('change');
        }""", c['value'])
        time.sleep(1.2)
        
        # Verificar grades
        grades = page.evaluate("""() => {
            const select = document.getElementById('idGrade');
            return Array.from(select.options).map(o => ({ value: o.value, text: o.text })).filter(o => o.value);
        }""")
        
        for g in grades:
            page.evaluate("""(gVal) => {
                const select = document.getElementById('idGrade');
                select.value = gVal;
                select.dispatchEvent(new Event('change', { bubbles: true }));
                if (typeof $ !== 'undefined') $(select).trigger('change');
            }""", g['value'])
            time.sleep(1.2)
            
            # Verificar se Compiladores está no dropdown de disciplinas
            disciples = page.evaluate("""() => {
                const select = document.getElementById('idDisciplina');
                return Array.from(select.options).map(o => ({ value: o.value, text: o.text })).filter(o => o.text.toLowerCase().includes('compiladores'));
            }""")
            
            if disciples:
                found_course = {
                    "curso": c['text'],
                    "idCurso": c['value'],
                    "grade": g['text'],
                    "idGrade": g['value'],
                    "compiladores": disciples
                }
                print(f"\n🎉 ENCONTRADO! Curso: '{c['text']}' | Grade: '{g['text']}' | Disciplina: {disciples}")
                break
        if found_course:
            break

    if not found_course:
        print("\n⚠️ 'Compiladores' não foi encontrado nos dropdowns de associação de curso.")
