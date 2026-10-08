import time
import re
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    
    pages = [pg for pg in ctx.pages if "Elaborador" in pg.url or "avalia" in pg.url]
    if not pages:
        print("Nenhuma página AvaliA encontrada.")
        exit(1)
        
    page = pages[-1] # Usar a última aba do AvaliA
    print(f"Conectado à página: {page.url}")

    # 1. Se o formulário já está visível
    if page.locator("#Questao_Nome").count() > 0 and page.locator("#Questao_Nome").first.is_visible():
        print("🎉 Formulário do Passo 4 já está visível e pronto!")
        exit(0)

    # 2. Clicar em "Elabore Novas Questões" se estiver na dashboard
    btn_elab = page.locator("a, button").filter(has_text=re.compile(r"Elabore Novas Questões", re.IGNORECASE))
    if btn_elab.count() > 0 and btn_elab.first.is_visible():
        print("Clicando em 'Elabore Novas Questões'...")
        btn_elab.first.click()
        page.wait_for_timeout(2000)

    # 3. Passo 1 - Selecionar fonte AvaliA
    avalia_btn = page.locator("button, a, div").filter(has_text=re.compile(r"^AvaliA$", re.IGNORECASE))
    if avalia_btn.count() > 0 and avalia_btn.first.is_visible():
        print("[Passo 1] Clicando em 'AvaliA'...")
        avalia_btn.first.click()
        page.wait_for_timeout(1000)

    # Passo 1 -> Passo 2
    btn_prox = page.locator("#buttonProximo")
    if btn_prox.count() > 0 and btn_prox.first.is_visible():
        print("[Passo 1 -> 2] Clicando em 'Próximo'...")
        btn_prox.first.click()
        page.wait_for_timeout(1500)

    # Passo 2 -> Passo 3
    if btn_prox.count() > 0 and btn_prox.first.is_visible():
        print("[Passo 2 -> 3] Clicando em 'Próximo'...")
        btn_prox.first.click()
        page.wait_for_timeout(1500)

    # 4. Passo 3 - Selecionar Disciplina Compiladores e Tag
    res = page.evaluate("""() => {
        // Limpar alertas antigos
        document.querySelectorAll('.toast, .toast-warning, .toast-error, .toast-info').forEach(t => t.remove());

        const selectDiscip = Array.from(document.querySelectorAll('select')).find(s => {
            return Array.from(s.options).some(o => o.text.toLowerCase().includes('compiladores'));
        });

        if (!selectDiscip) return { success: false, msg: 'Select de disciplina não encontrado' };

        let compiladoresOpt = Array.from(selectDiscip.options).find(o => o.text.toLowerCase().includes('compiladores'));
        if (compiladoresOpt) {
            selectDiscip.value = compiladoresOpt.value;
            selectDiscip.dispatchEvent(new Event('change', { bubbles: true }));
            if (typeof $ !== 'undefined') $(selectDiscip).trigger('change');
        }

        // Selecionar tag (ex: AP1, AE2, ou primeira checkbox visível)
        let chk = document.querySelector('input[type="checkbox"][name*="Tag"], input[type="checkbox"][value*="AP1"], input[type="checkbox"]');
        if (chk && !chk.checked) {
            chk.checked = true;
            chk.dispatchEvent(new Event('change', { bubbles: true }));
        }

        // Clicar no botão +Adicionar
        const btnAdd = Array.from(document.querySelectorAll('button, a, input[type="button"]')).find(b => b.innerText.includes('Adicionar'));
        if (btnAdd) btnAdd.click();

        return {
            success: true,
            discip: compiladoresOpt ? compiladoresOpt.text : null
        };
    }""")
    print("[Passo 3] Seleção de Disciplina:", res)
    page.wait_for_timeout(1500)

    # Clicar em Próximo para ir ao Passo 4
    if btn_prox.count() > 0 and btn_prox.first.is_visible():
        print("[Passo 3 -> 4] Clicando em 'Próximo'...")
        btn_prox.first.click()
        page.wait_for_timeout(2500)

    if page.locator("#Questao_Nome").count() > 0 and page.locator("#Questao_Nome").first.is_visible():
        print("🎉 SUCESSO! Tela do Passo 4 (Elaboração da Questão - Compiladores) está aberta e pronta!")
    else:
        print("⚠️ Tela do Passo 4 ainda não visível, verificando estado...")
