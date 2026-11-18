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
        print(f"[{check_count}] Aguardando login... Por favor, faça login na janela do navegador aberta.")
        
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

def close_all_modals(page):
    try:
        modals = page.locator(".modal.show, .modal.in, [role='dialog']")
        for i in range(modals.count()):
            m = modals.nth(i)
            if m.is_visible():
                close_btn = m.locator("button:has-text('Fechar'), .close, [data-dismiss='modal']").first
                if close_btn.count() > 0 and close_btn.is_visible():
                    close_btn.click(force=True)
                    page.wait_for_timeout(500)
    except Exception:
        pass

def process_single_question(page):
    dismiss_toast_if_any(page)
    page.wait_for_selector("#myModal, .modal.show, .modal.in", timeout=10000)
    main_modal = page.locator("#myModal, .modal.show, .modal.in").first
    
    q_rows = main_modal.locator("tbody tr")
    if q_rows.count() == 0:
        return False
        
    first_q = q_rows.first
    status_btn = first_q.locator("button:has-text('Status'), .btn-success, button").first
    if status_btn.count() > 0:
        status_btn.scroll_into_view_if_needed()
        status_btn.click(force=True)
        page.wait_for_timeout(1200)

    desativar_btn = page.locator("[id*='btnDesativar'], a[href*='Desativar'], .fa-thumbs-down, i[class*='thumbs-down']").first
    if desativar_btn.count() > 0:
        desativar_btn.evaluate("el => el.click()")
        page.wait_for_timeout(1800)

    page.wait_for_selector(".modal:has-text('Cancelar'), [role='dialog']:has-text('Cancelar')", timeout=8000)
    cancel_modal = page.locator(".modal:has-text('Cancelar'), [role='dialog']:has-text('Cancelar')").last
    
    desc_input = cancel_modal.locator("textarea[name*='Descricao'], textarea[id*='Descricao'], textarea[placeholder*='Descrição'], textarea").first
    if desc_input.count() > 0:
        desc_input.fill("erro")
        page.wait_for_timeout(600)

    salvar_btn = cancel_modal.locator("button:has-text('Salvar'), input[value*='Salvar'], button:has-text('Confirmar')").first
    if salvar_btn.count() > 0 and salvar_btn.is_visible():
        salvar_btn.click(force=True)
        page.wait_for_timeout(1200)
    else:
        close_btn = cancel_modal.locator("button:has-text('Fechar'), .close, [data-dismiss='modal']").first
        if close_btn.count() > 0 and close_btn.is_visible():
            close_btn.click(force=True)
            page.wait_for_timeout(800)

    dismiss_toast_if_any(page)
    close_all_modals(page)
    return True

def get_disciplines_needing_action(page):
    page.goto(TARGET_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    try:
        length_select = page.locator("select[name*='length'], select[name*='Table']").first
        if length_select.is_visible():
            length_select.select_option("100")
            page.wait_for_timeout(2000)
    except Exception:
        pass

    page.wait_for_selector("table tbody tr", timeout=15000)
    rows = page.locator("table tbody tr")
    targets = []
    
    for i in range(rows.count()):
        row = rows.nth(i)
        tds = row.locator("td")
        if tds.count() > 12:
            disc_name = tds.nth(3).inner_text().strip()
            pre_val_text = tds.nth(12).inner_text().strip()
            if pre_val_text.isdigit() and int(pre_val_text) > 10:
                targets.append((disc_name, int(pre_val_text)))
    return targets

def process_discipline(page, disc_name):
    print(f"\n==================================================")
    print(f" Processando Disciplina: '{disc_name}'")
    print(f"==================================================")
    
    while True:
        page.goto(TARGET_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        try:
            length_select = page.locator("select[name*='length'], select[name*='Table']").first
            if length_select.is_visible():
                length_select.select_option("100")
                page.wait_for_timeout(1500)
        except Exception:
            pass

        rows = page.locator("table tbody tr")
        target_td = None
        current_count = 0
        
        for i in range(rows.count()):
            row = rows.nth(i)
            tds = row.locator("td")
            if tds.count() > 12:
                name = tds.nth(3).inner_text().strip()
                if name.lower() == disc_name.lower():
                    cnt_str = tds.nth(12).inner_text().strip()
                    if cnt_str.isdigit():
                        current_count = int(cnt_str)
                        target_td = tds.nth(12)
                    break
                    
        if not target_td or current_count <= 10:
            print(f"✓ Disciplina '{disc_name}' concluída! Restam {current_count} pré-validadas.")
            break
            
        print(f"   [Pré-validadas: {current_count}] Processando próxima questão...")
        link = target_td.locator("a, button").first
        if link.count() > 0:
            link.click(force=True)
            page.wait_for_timeout(2500)
            process_single_question(page)
        else:
            print("   Link não encontrado. Interrompendo disciplina.")
            break

def main():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--start-maximized']
        )
        
        page = wait_for_login(context)
        targets = get_disciplines_needing_action(page)
        
        print(f"\nTotal de disciplinas que precisam de ajuste (> 10 pré-validadas): {len(targets)}")
        for name, cnt in targets:
            print(f" - {name}: {cnt} pré-validadas")
            
        for name, _ in targets:
            process_discipline(page, name)
            
        print("\n==================================================")
        print(" TODAS AS DISCIPLINAS FORAM PROCESSADAS COM SUCESSO!")
        print("==================================================")
        time.sleep(5)
        context.close()

if __name__ == "__main__":
    main()
