import time
import os
import sys
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "/home/hamilcar/Antigravity/playwright_user_data"
TARGET_URL = "https://avalia.grupoa.com.br/Professor"

def get_logged_in_page(context):
    for p in reversed(context.pages):
        try:
            url = p.url
            if "Login" not in url and "avalia.grupoa.com.br" in url:
                return p
        except Exception:
            pass
    return None

def wait_for_login(context):
    print("\n==================================================")
    print(" Verificando autenticação no AVALIA...")
    print("==================================================")
    
    page = context.pages[0] if context.pages else context.new_page()
    try:
        if "avalia.grupoa.com.br" not in page.url or "Login" in page.url:
            page.goto(TARGET_URL, wait_until="domcontentloaded")
    except Exception:
        pass
    time.sleep(2)
    
    check_count = 0
    while True:
        logged_page = get_logged_in_page(context)
        if logged_page:
            print(f"✓ Sessão autenticada detectada! URL atual: {logged_page.url}")
            return logged_page
            
        check_count += 1
        print(f"[{check_count}] Por favor, faça login na janela do navegador aberta...")
        
        if check_count % 3 == 0:
            try:
                page.goto(TARGET_URL, wait_until="domcontentloaded")
                time.sleep(2)
                if "Login" not in page.url and "avalia.grupoa.com.br" in page.url:
                    print(f"✓ Login confirmado! URL: {page.url}")
                    return page
            except Exception:
                pass
                
        time.sleep(3)

def dismiss_toast_if_any(page):
    try:
        toasts = page.locator(".toast, .toast-error, .alert-danger, .toast-warning")
        if toasts.count() > 0:
            for i in range(toasts.count()):
                t = toasts.nth(i)
                if t.is_visible():
                    txt = t.inner_text().replace('\n', ' ')
                    print(f"   [Alerta do Sistema Fechado] {txt[:120]}...")
                    close_btn = t.locator(".toast-close-button, .close, [data-dismiss='alert']").first
                    if close_btn.count() > 0 and close_btn.is_visible():
                        close_btn.click(force=True)
    except Exception:
        pass

def select_ensino_a_distancia_via_ui(page):
    print(" Ajustando filtro de modalidade para 'Ensino a distância'...")
    try:
        page.evaluate("""() => {
            const chks = Array.from(document.querySelectorAll('input[type="checkbox"]'));
            const matrChk = chks.find(c => {
                const txt = c.parentElement ? c.parentElement.innerText.toLowerCase() : '';
                return txt.includes('somente disciplinas') || txt.includes('matrículas') || txt.includes('matriculas');
            });
            if (matrChk && matrChk.checked) matrChk.click();
        }""")
        page.wait_for_timeout(1000)
    except Exception:
        pass

    try:
        updated = page.evaluate("""() => {
            const selects = Array.from(document.querySelectorAll('select')).filter(s => 
                !s.name.includes('length') && !s.id.includes('length') &&
                !s.name.includes('Table') && !s.id.includes('Table')
            );
            const modSelect = selects.find(s => 
                Array.from(s.options).some(o => o.text.toLowerCase().includes('semipresencial') || o.text.toLowerCase().includes('distância') || o.text.toLowerCase().includes('distancia'))
            );
            if (modSelect) {
                const semipOpt = Array.from(modSelect.options).find(o => o.text.toLowerCase().includes('semipresencial'));
                const eadOpt = Array.from(modSelect.options).find(o => o.text.toLowerCase().includes('distância') || o.text.toLowerCase().includes('distancia'));
                
                const $ = window.jQuery;
                if ($ && typeof $(modSelect).multiselect === 'function') {
                    if (semipOpt) try { $(modSelect).multiselect('deselect', [semipOpt.value]); } catch(e){}
                    if (eadOpt) $(modSelect).multiselect('select', [eadOpt.value]);
                    $(modSelect).multiselect('refresh');
                }
                return true;
            }
            return false;
        }""")
        print(f"   Modalidade 'Ensino a distância' aplicada: {updated}")
        page.wait_for_timeout(2500)
    except Exception as e:
        print(f"   [Aviso ao selecionar modalidade]: {e}")

def ensure_100_per_page_and_get_target(page):
    select_ensino_a_distancia_via_ui(page)
    
    try:
        search_box = page.locator("input[type='search'], .dataTables_filter input, input[placeholder*='busca'], input[placeholder*='Busca']").first
        if search_box.count() > 0 and search_box.is_visible():
            search_box.fill("Infraestrutura e Serviços")
            page.wait_for_timeout(1500)
            print(" Digitado 'Infraestrutura e Serviços' no campo de busca.")
    except Exception:
        pass

    try:
        length_select = page.locator("select[name*='length'], select[name*='Table']").first
        if length_select.count() > 0 and length_select.is_visible():
            length_select.select_option("100")
            page.wait_for_timeout(2500)
            print(" Exibição configurada para 100 registros por página.")
    except Exception as e:
        print(f" [Aviso ao ajustar 100 por página]: {e}")

    try:
        page.wait_for_selector("table tbody tr td", timeout=15000)
        page.wait_for_timeout(1000)
    except Exception:
        pass

    rows = page.locator("table tbody tr")
    print(f" Total de disciplinas encontradas na página atual: {rows.count()}")
    
    for i in range(rows.count()):
        row = rows.nth(i)
        tds = row.locator("td")
        if tds.count() > 3:
            disc_name = tds.nth(3).inner_text().strip()
            name_lower = disc_name.lower()
            if "infraestrutura" in name_lower and ("serviços" in name_lower or "servicos" in name_lower):
                pre_val_td = tds.nth(12) if tds.count() > 12 else tds.last
                text = pre_val_td.inner_text().strip()
                return disc_name, text, pre_val_td
    return None, None, None

def close_submodals_except_my_modal(page):
    try:
        page.evaluate("""() => {
            const modals = Array.from(document.querySelectorAll('.modal, [role="dialog"]'));
            modals.forEach(m => {
                if (m.id !== 'myModal' && (m.classList.contains('show') || m.classList.contains('in') || m.style.display === 'block')) {
                    const closeBtn = m.querySelector('button.close, .close, [data-dismiss="modal"]');
                    if (closeBtn) {
                        try { closeBtn.click(); } catch(e){}
                    } else {
                        m.style.display = 'none';
                        m.classList.remove('show', 'in');
                    }
                }
            });
            const backdrops = document.querySelectorAll('.modal-backdrop');
            if (backdrops.length > 1) {
                for (let i = 1; i < backdrops.length; i++) {
                    backdrops[i].remove();
                }
            }
        }""")
        page.wait_for_timeout(400)
    except Exception:
        pass

def process_single_question(page, q_idx):
    dismiss_toast_if_any(page)
    close_submodals_except_my_modal(page)
    
    # 1. Localizar modal principal das questões (#myModal)
    page.wait_for_selector("#myModal, .modal.show, .modal.in", timeout=10000)
    main_modal = page.locator("#myModal, .modal.show, .modal.in").first
    
    # 2. Clicar no botão verde Status da questão de índice q_idx
    print(f"   PASSO 1: Clicando no botão 'Status' da questão #{q_idx + 1}...")
    q_rows = main_modal.locator("tbody tr")
    if q_idx >= q_rows.count():
        print(f"   [Aviso] Índice {q_idx + 1} excede o número de questões visíveis ({q_rows.count()}).")
        return False
        
    target_q = q_rows.nth(q_idx)
    status_btn = target_q.locator("button:has-text('Status'), .btn-success, button").first
    if status_btn.count() > 0:
        status_btn.scroll_into_view_if_needed()
        status_btn.click(force=True)
        page.wait_for_timeout(1500)

    # 3. Clicar no botão vermelho de desativação (btnDesativar) NO MODAL DE STATUS RECÉM-ABERTO
    print("   PASSO 2: Clicando no botão vermelho de desativação (Desativar)...")
    # Buscar especificamente no modal que não seja #myModal
    status_modal = page.locator(".modal.show:not(#myModal), .modal.in:not(#myModal), [role='dialog']:not(#myModal)").last
    desativar_btn = status_modal.locator("[id*='btnDesativar'], a[href*='Desativar'], .fa-thumbs-down, i[class*='thumbs-down']").first
    if desativar_btn.count() > 0:
        desativar_btn.evaluate("el => el.click()")
        page.wait_for_timeout(1800)

    # 4. Aguardar janela "Cancelar a questão"
    print("   PASSO 3: Aguardando abertura da janela 'Cancelar a questão'...")
    page.wait_for_selector(".modal:has-text('Cancelar'), [role='dialog']:has-text('Cancelar'), .modal:has-text('Descrição')", timeout=8000)
    
    # 5. Preencher "erro" no campo Descrição
    print("   PASSO 4: Preenchendo 'erro' na caixa 'Descrição'...")
    desc_filled = page.evaluate("""() => {
        const modals = Array.from(document.querySelectorAll('.modal, [role="dialog"]'));
        const cancelModal = modals.find(m => m.innerText.includes('Cancelar') || m.innerText.includes('Descrição') || m.innerText.includes('Motivo'));
        if (!cancelModal) return false;
        
        const ta = cancelModal.querySelector('textarea, input[type="text"]');
        if (ta) {
            ta.value = "erro";
            ta.dispatchEvent(new Event('input', { bubbles: true }));
            ta.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        }
        return false;
    }""")
    print(f"   Descrição preenchida: {desc_filled}")
    page.wait_for_timeout(800)

    # 6. EXECUTAR A SUBMISSÃO REAL DO CANCELAMENTO
    print("   PASSO 5: Executando a submissão e salvamento no banco de dados...")
    submit_log = page.evaluate("""() => {
        const modals = Array.from(document.querySelectorAll('.modal, [role="dialog"]'));
        const cancelModal = modals.find(m => m.innerText.includes('Cancelar') || m.innerText.includes('Descrição') || m.innerText.includes('Motivo'));
        if (!cancelModal) return 'NO_CANCEL_MODAL';
        
        // 1. Verificar se existe um formulário explicitamente
        const form = cancelModal.querySelector('form');
        if (form) {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"], .btn-primary, .btn-danger, .btn-success') ||
                              Array.from(form.querySelectorAll('button, input, a')).find(b => {
                                  const txt = (b.innerText || b.value || '').toLowerCase();
                                  return (txt.includes('salvar') || txt.includes('confirmar') || txt.includes('desativar') || txt.includes('gravar') || txt.includes('enviar') || txt.includes('cancelar')) && !txt.includes('fechar') && !b.getAttribute('data-dismiss');
                              });
            if (submitBtn) {
                submitBtn.click();
                return 'CLICKED_FORM_SUBMIT_BTN: ' + (submitBtn.innerText || submitBtn.value);
            }
            form.submit();
            return 'SUBMITTED_FORM_DIRECTLY';
        }

        // 2. Se não houver form, procurar botões no cancelModal
        const allBtns = Array.from(cancelModal.querySelectorAll('button, input, a'));
        const actionBtn = allBtns.find(b => {
            const txt = (b.innerText || b.value || '').toLowerCase();
            const isDismiss = b.getAttribute('data-dismiss') === 'modal' || b.classList.contains('close') || txt.includes('fechar');
            return !isDismiss && (txt.includes('salvar') || txt.includes('confirmar') || txt.includes('desativar') || txt.includes('gravar') || txt.includes('enviar') || txt.includes('ok') || txt.includes('sim') || txt.includes('cancelar'));
        });

        if (actionBtn) {
            actionBtn.click();
            return 'CLICKED_ACTION_BTN: ' + (actionBtn.innerText || actionBtn.value);
        }

        // 3. Fallback: procurar qualquer botão que não seja o 'x' de fechar nem 'Fechar'
        const nonCloseBtn = allBtns.find(b => {
            const txt = (b.innerText || b.value || '').toLowerCase();
            const isDismiss = b.getAttribute('data-dismiss') === 'modal' || b.classList.contains('close') || txt === 'fechar' || txt === '×';
            return !isDismiss;
        });
        if (nonCloseBtn) {
            nonCloseBtn.click();
            return 'CLICKED_FALLBACK_BTN: ' + (nonCloseBtn.innerText || nonCloseBtn.value);
        }

        return 'NO_SUBMIT_BTN_FOUND';
    }""")
    print(f"   Log da submissão: {submit_log}")
    page.wait_for_timeout(2500)

    # Fechar submodais e deixar apenas #myModal
    close_submodals_except_my_modal(page)
    dismiss_toast_if_any(page)
    return True

def main():
    print("==================================================")
    print(" Automação AVALIA - Disciplina: Infraestrutura e Serviços de TI (Ensino a distância)")
    print("==================================================")
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--start-maximized']
        )
        
        page = wait_for_login(context)
        
        # Monitorar requisições para logar chamadas de desativação
        def log_request(req):
            if "desativar" in req.url.lower() or "cancelar" in req.url.lower() or "salvar" in req.url.lower():
                print(f"   >>> REQUISIÇÃO DISPARADA: {req.method} {req.url}")
        page.on("request", log_request)

        disc_name, count_str, pre_val_td = ensure_100_per_page_and_get_target(page)
        if not disc_name:
            print("\n[Aviso] Retestando localização de 'Infraestrutura e Serviços de TI'...")
            page.wait_for_timeout(3000)
            disc_name, count_str, pre_val_td = ensure_100_per_page_and_get_target(page)
            
        if not disc_name:
            print("\n[Erro Final] Disciplina não localizada.")
            context.close()
            return
            
        print(f"\n>>> DISCIPLINA ENCONTRADA: '{disc_name}' <<<")
        print(f"Contagem inicial de pré-validadas: {count_str}")
        
        if not count_str.isdigit() or int(count_str) <= 10:
            print(f"✓ A disciplina já possui 10 ou menos questões pré-validadas ({count_str}). Encerrando.")
            context.close()
            return
            
        total_initial = int(count_str)
        target_remaining = 10
        needed_deactivations = total_initial - target_remaining
        
        print(f"Meta: Reduzir de {total_initial} para {target_remaining} (Desativar {needed_deactivations} questões).")
        
        print(f"Clicando na célula de pré-validadas ({count_str}) para abrir a lista de questões...")
        link = pre_val_td.locator("a, button").first
        if link.count() > 0:
            link.click(force=True)
            page.wait_for_timeout(3000)
        else:
            print("[Erro] Link da célula de pré-validadas não encontrado.")
            context.close()
            return

        for q_idx in range(needed_deactivations):
            print(f"--------------------------------------------------")
            print(f" [QUESTÃO {q_idx + 1}/{needed_deactivations}] Desativando questão...")
            print(f"--------------------------------------------------")
            
            success = process_single_question(page, q_idx)
            if success:
                print(f"   ✓ Processamento da questão {q_idx + 1}/{needed_deactivations} concluído!")
            else:
                print(f"   [Aviso] Falha ao processar questão {q_idx + 1}.")
                
            page.wait_for_timeout(1500)
            
        print("\n==================================================")
        print(f" Meta Atingida! Processadas as {needed_deactivations} questões em '{disc_name}'.")
        print("==================================================")
        time.sleep(5)
        context.close()

if __name__ == "__main__":
    main()
