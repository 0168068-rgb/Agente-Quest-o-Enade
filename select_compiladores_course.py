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
    print("Conectado à página:", page.url)

    # 1. Selecionar Curso (Análise e Desenvolv. de Sistemas)
    res_curso = page.evaluate("""() => {
        const selectCurso = document.getElementById('idCurso');
        if (!selectCurso) return 'idCurso não encontrado';

        for (let opt of selectCurso.options) {
            if (opt.text.toLowerCase().includes('análise') || opt.text.toLowerCase().includes('analise')) {
                selectCurso.value = opt.value;
                selectCurso.dispatchEvent(new Event('change', { bubbles: true }));
                if (typeof $ !== 'undefined') $(selectCurso).trigger('change');
                return { value: opt.value, text: opt.text };
            }
        }
        return 'Nenhum curso correspondente encontrado';
    }""")
    print("1. Curso Selecionado:", res_curso)
    time.sleep(2)

    # 2. Selecionar Grade (primeira opção válida)
    res_grade = page.evaluate("""() => {
        const selectGrade = document.getElementById('idGrade');
        if (!selectGrade || selectGrade.options.length <= 1) return 'Grade ainda não carregou';

        selectGrade.options[1].selected = true;
        selectGrade.dispatchEvent(new Event('change', { bubbles: true }));
        if (typeof $ !== 'undefined') $(selectGrade).trigger('change');
        return { value: selectGrade.value, text: selectGrade.options[1].text };
    }""")
    print("2. Grade Selecionada:", res_grade)
    time.sleep(2)

    # 3. Selecionar Disciplina Compiladores
    res_discip = page.evaluate("""() => {
        const selectDiscip = document.getElementById('idDisciplina');
        if (!selectDiscip || selectDiscip.options.length <= 1) return 'Disciplinas ainda não carregaram';

        for (let opt of selectDiscip.options) {
            if (opt.text.toLowerCase().includes('compiladores')) {
                selectDiscip.value = opt.value;
                selectDiscip.dispatchEvent(new Event('change', { bubbles: true }));
                if (typeof $ !== 'undefined') $(selectDiscip).trigger('change');
                return { value: opt.value, text: opt.text };
            }
        }
        return 'Compiladores não encontrado nas opções de disciplina';
    }""")
    print("3. Disciplina Selecionada:", res_discip)

    # 4. Clicar em Pesquisar
    print("4. Clicando no botão 'Pesquisar'...")
    page.evaluate("""() => {
        const btnSearch = document.querySelector('button[type="submit"], input[type="submit"]');
        if (btnSearch) btnSearch.click();
    }""")
    time.sleep(3)

    # Inspect results
    res_results = page.evaluate("""() => {
        const trs = Array.from(document.querySelectorAll('table tbody tr')).map(tr => {
            return Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim());
        }).filter(arr => arr.length > 0);
        return trs;
    }""")
    print("Resultados da busca:")
    print(json.dumps(res_results, indent=2, ensure_ascii=False))
