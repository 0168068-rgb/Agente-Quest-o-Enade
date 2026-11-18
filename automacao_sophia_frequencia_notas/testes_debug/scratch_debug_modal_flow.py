import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "/home/hamilcar/Antigravity/playwright_user_data"
TARGET_URL = "https://avalia.grupoa.com.br/Professor"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(USER_DATA_DIR, headless=False)
    page = context.pages[0] if context.pages else context.new_page()
    
    print("Navegando para o Professor...")
    page.goto(TARGET_URL, wait_until="domcontentloaded")
    time.sleep(3)
    
    if "Login" in page.url:
        print("Aguardando login...")
        while "Login" in page.url:
            time.sleep(2)
            
    if page.url != TARGET_URL:
        page.goto(TARGET_URL, wait_until="networkidle")
        time.sleep(3)

    # Pegar 1ª disciplina com pré-validadas
    table = page.locator("table").nth(1)
    row = table.locator("tbody tr").first
    td_12 = row.locator("td").nth(12)
    print("Clicando na célula de pré-validadas:", td_12.inner_text())
    td_12.locator("a").first.click()
    page.wait_for_timeout(3000)
    
    # Screenshot do modal de questões abertas (#myModal)
    page.screenshot(path="/home/hamilcar/Antigravity/debug_step1_questions_modal.png")
    
    # Inspecionar todos os botões da primeira questão no modal
    modal = page.locator("#myModal, .modal.show").first
    buttons_info = modal.evaluate("""(m) => {
        const trs = Array.from(m.querySelectorAll('tbody tr'));
        if (trs.length === 0) return { error: 'sem linhas no modal' };
        const firstRow = trs[0];
        const btns = Array.from(firstRow.querySelectorAll('a, button')).map(b => ({
            tag: b.tagName,
            text: b.innerText.trim(),
            id: b.id,
            class: b.className,
            title: b.getAttribute('title'),
            href: b.getAttribute('href'),
            visible: b.offsetWidth > 0 && b.offsetHeight > 0
        }));
        return { firstRowButtons: btns };
    }""")
    print("\nBotões na 1ª questão do modal:", buttons_info)
    
    # Clicar no botão verde "Status" da 1ª questão
    print("\nClicando no botão verde Status...")
    status_btn = modal.locator("button:has-text('Status'), .btn-success").first
    status_btn.click()
    page.wait_for_timeout(2000)
    
    # Screenshot após clicar em Status
    page.screenshot(path="/home/hamilcar/Antigravity/debug_step2_after_status_click.png")
    
    # Inspecionar elementos visíveis no DOM agora
    after_status_info = page.evaluate("""() => {
        const modals = Array.from(document.querySelectorAll('.modal')).map(m => ({
            id: m.id,
            class: m.className,
            titleText: m.querySelector('.modal-title') ? m.querySelector('.modal-title').innerText : '',
            display: window.getComputedStyle(m).display,
            isShown: m.classList.contains('in') || m.classList.contains('show')
        }));
        const dangerBtns = Array.from(document.querySelectorAll('.btn-danger, [id*="btnDesativar"], [id*="btnCancelar"], .fa-thumbs-down')).map(b => ({
            tag: b.tagName,
            text: b.innerText.trim(),
            id: b.id,
            class: b.className,
            title: b.getAttribute('title'),
            href: b.getAttribute('href'),
            display: window.getComputedStyle(b).display,
            visible: b.offsetWidth > 0 && b.offsetHeight > 0
        }));
        return { modals, dangerBtns };
    }""")
    print("\nModais e botões perigosos após Status click:", after_status_info)
    
    context.close()
