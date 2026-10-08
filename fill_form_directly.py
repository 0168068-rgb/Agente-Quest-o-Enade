import os
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"
    form_url = "https://forms.gle/kMvaxTTtBrSAgCFn9"
    if len(sys.argv) > 1:
        form_url = sys.argv[1]
    
    print("Iniciando o Chromium para preencher o formulário diretamente...")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--remote-debugging-port=9222'
            ]
        )
        page = context.new_page()
        print(f"Navegando para o formulário: {form_url}")
        page.goto(form_url)
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        email_val = "0168068@professor.unig.edu.br"
        nome_val = "Hamilcar Pereira da Silva"
        
        # 1. Fill Email
        email_filled = False
        email_inputs = page.locator("input[type='email']").all()
        if email_inputs:
            email_inputs[0].fill(email_val)
            email_filled = True
            print("E-mail preenchido no campo do tipo email.")
            
        # Try finding other text inputs
        inputs = page.locator("input[type='text']").all()
        print(f"Encontrados {len(inputs)} campos de texto adicionais.")
        
        name_filled = False
        for inp in inputs:
            try:
                aria_label = inp.get_attribute("aria-label") or ""
                parent_text = page.evaluate("el => { const parent = el.closest('[role=\"listitem\"], div'); return parent ? parent.innerText : ''; }", inp.element_handle()) or ""
                combined_text = (aria_label + " " + parent_text).lower()
                
                print(f"Campo detectado - Aria Label: '{aria_label}', Texto adjacente: '{parent_text[:60].strip()}'")
                
                if not email_filled and ("email" in combined_text or "e-mail" in combined_text or "correio" in combined_text):
                    inp.fill(email_val)
                    email_filled = True
                    print("E-mail preenchido.")
                elif not name_filled and ("nome" in combined_text or "name" in combined_text or "completo" in combined_text):
                    inp.fill(nome_val)
                    name_filled = True
                    print("Nome completo preenchido.")
            except Exception as e:
                print(f"Erro ao analisar campo de texto: {e}")
                
        # Fallback if not filled
        if not email_filled and len(inputs) >= 1:
            inputs[0].fill(email_val)
            email_filled = True
            print("Fallback: E-mail preenchido no primeiro campo de texto.")
        if not name_filled and len(inputs) >= 2:
            inputs[1].fill(nome_val)
            name_filled = True
            print("Fallback: Nome completo preenchido no segundo campo de texto.")
            
        # 2. Select Radio Option: UNIG-Nova Iguaçu
        # Let's inspect the options and find the correct one
        option_clicked = False
        print("Procurando pela opção 'UNIG-Nova Iguaçu'...")
        
        # Method A: Look for divs with role="radio" and check their label/text
        radios = page.locator('[role="radio"]').all()
        print(f"Encontrados {len(radios)} botões de rádio (role='radio').")
        for rad in radios:
            try:
                label = rad.get_attribute("aria-label") or ""
                text = rad.inner_text() or ""
                parent_text = page.evaluate("el => el.parentElement.innerText", rad.element_handle()) or ""
                combined = (label + " " + text + " " + parent_text).lower()
                print(f"Rádio - Label: '{label}', Text: '{text}', Parent Text: '{parent_text.strip()}'")
                
                if "unig" in combined and ("nova" in combined or "igua" in combined):
                    print(f"Opção de rádio encontrada! Clicando...")
                    rad.click()
                    option_clicked = True
                    break
            except Exception as e:
                print(f"Erro ao verificar rádio: {e}")
                
        # Method B: Search for spans or labels containing the text and click them
        if not option_clicked:
            print("Tentando Método B (busca por span/div com texto exato)...")
            options = page.locator("span, div, label").all()
            for opt in options:
                try:
                    text = opt.inner_text().strip()
                    # We match only if it is a short text, to avoid clicking parent containers!
                    if len(text) < 40 and "unig" in text.lower() and ("nova" in text.lower() or "igua" in text.lower()):
                        # Check if it's visible and click it
                        if opt.is_visible():
                            print(f"Opção encontrada por texto curto ('{text}'). Clicando...")
                            opt.click()
                            option_clicked = True
                            break
                except:
                    continue
                    
        if not option_clicked:
            print("AVISO: Não foi possível selecionar 'UNIG-Nova Iguaçu' automaticamente.")
            
        time.sleep(2)
        page.screenshot(path="form_filled_fixed.png")
        print("Screenshot da página preenchida salvo em 'form_filled_fixed.png'.")
        
        # 3. Click Submit
        submit_btn = None
        submit_selectors = [
            'div[role="button"]:has-text("Enviar")',
            'div[role="button"]:has-text("Submit")',
            'span:has-text("Enviar")',
            'span:has-text("Submit")',
            'button:has-text("Enviar")',
            'button:has-text("Submit")'
        ]
        for sel in submit_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible():
                    submit_btn = btn
                    break
            except:
                continue
                
        if submit_btn:
            print("Clicando no botão de envio (Enviar/Submit)...")
            submit_btn.click()
            time.sleep(5)
            page.screenshot(path="form_submitted_fixed.png")
            print("Screenshot pós-envio salvo em 'form_submitted_fixed.png'.")
        else:
            print("Botão de envio não encontrado.")
            
        context.close()

if __name__ == "__main__":
    main()
