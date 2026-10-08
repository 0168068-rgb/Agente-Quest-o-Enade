import os
import sys
import time
import re
from playwright.sync_api import sync_playwright

def fill_google_form(context, url):
    print(f"\n[Formulário] Abrindo nova aba para o formulário: {url}")
    page = context.new_page()
    try:
        page.goto(url)
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        page.screenshot(path="form_loaded.png")
        print("[Formulário] Formulário carregado. Analisando campos...")
        
        email_val = "0168068@professor.unig.edu.br"
        nome_val = "Hamilcar Pereira da Silva"
        
        # Google Forms usually uses input[type="text"] or input[type="email"]
        inputs = page.locator("input[type='text'], input[type='email']").all()
        print(f"[Formulário] Encontrados {len(inputs)} campos de texto.")
        
        email_filled = False
        name_filled = False
        
        # Try filling email by input type first
        email_inputs = page.locator("input[type='email']").all()
        if email_inputs:
            email_inputs[0].fill(email_val)
            email_filled = True
            print("[Formulário] E-mail preenchido no campo de tipo email.")
            
        for inp in inputs:
            try:
                aria_label = inp.get_attribute("aria-label") or ""
                # Get close container text to identify the question label
                parent_text = page.evaluate("el => { const parent = el.closest('[role=\"listitem\"], div'); return parent ? parent.innerText : ''; }", inp.element_handle()) or ""
                
                combined_text = (aria_label + " " + parent_text).lower()
                print(f"[Formulário] Campo detectado - Aria Label: '{aria_label}', Texto adjacente: '{parent_text[:60].strip()}'")
                
                if not email_filled and ("email" in combined_text or "e-mail" in combined_text or "correio" in combined_text):
                    inp.fill(email_val)
                    email_filled = True
                    print("[Formulário] E-mail preenchido.")
                elif not name_filled and ("nome" in combined_text or "name" in combined_text or "completo" in combined_text):
                    inp.fill(nome_val)
                    name_filled = True
                    print("[Formulário] Nome completo preenchido.")
            except Exception as e:
                print(f"[Formulário] Erro ao processar campo individual: {e}")
                
        # Fallback if not filled
        if not email_filled and len(inputs) >= 1:
            inputs[0].fill(email_val)
            email_filled = True
            print("[Formulário] Fallback: E-mail preenchido no primeiro campo.")
        if not name_filled and len(inputs) >= 2:
            inputs[1].fill(nome_val)
            name_filled = True
            print("[Formulário] Fallback: Nome completo preenchido no segundo campo.")
            
        # Select Institution: UNIG-NOva iguaçu
        print("[Formulário] Procurando pela opção 'UNIG-NOva iguaçu'...")
        option_clicked = False
        
        # 1. Search for role="radio" and click the correct one
        radios = page.locator('[role="radio"]').all()
        for rad in radios:
            try:
                label = rad.get_attribute("aria-label") or ""
                text = rad.inner_text() or ""
                parent_text = page.evaluate("el => el.parentElement.innerText", rad.element_handle()) or ""
                combined = (label + " " + text + " " + parent_text).lower()
                if "unig" in combined and ("nova" in combined or "igua" in combined):
                    print(f"[Formulário] Opção de rádio encontrada! Clicando...")
                    rad.click()
                    option_clicked = True
                    break
            except:
                continue

        # 2. Fallback: Search for spans or labels containing the text
        if not option_clicked:
            options = page.locator("span, div, label").all()
            for opt in options:
                try:
                    text = opt.inner_text().strip()
                    if len(text) < 40 and "unig" in text.lower() and ("nova" in text.lower() or "igua" in text.lower()):
                        if opt.is_visible():
                            print(f"[Formulário] Opção por texto curto ('{text}'). Clicando...")
                            opt.click()
                            option_clicked = True
                            break
                except:
                    continue
                    
        # 3. Dropdown listbox check (role="listbox")
        if not option_clicked:
            listboxes = page.locator("[role='listbox']").all()
            if listboxes:
                print("[Formulário] Encontrado listbox (dropdown). Clicando para abrir opções...")
                listboxes[0].click()
                time.sleep(2)
                options = page.locator("[role='option'], div, span").all()
                for opt in options:
                    try:
                        text = opt.inner_text().strip()
                        if "unig" in text.lower():
                            print(f"[Formulário] Opção no dropdown encontrada: '{text}'. Clicando...")
                            opt.click()
                            option_clicked = True
                            break
                    except:
                        continue
                        
        if not option_clicked:
            print("[Formulário] AVISO: Não foi possível selecionar 'UNIG-NOva iguaçu' automaticamente.")
            
        time.sleep(2)
        page.screenshot(path="form_filled.png")
        print("[Formulário] Formulário preenchido. Screenshot salvo em 'form_filled.png'.")
        
        # Click submit button
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
            print("[Formulário] Clicando no botão de envio...")
            submit_btn.click()
            time.sleep(5)
            page.screenshot(path="form_submitted.png")
            print("[Formulário] Screenshot pós-envio salvo em 'form_submitted.png'.")
            return True
        else:
            print("[Formulário] Botão de envio não encontrado. Por favor, clique manualmente no navegador.")
            return False
            
    except Exception as e:
        print(f"[Formulário] Erro ao preencher: {e}")
        page.screenshot(path="form_error.png")
        return False

def main():
    user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"
    meet_url = "https://meet.google.com/bno-piai-vuq"
    if len(sys.argv) > 1:
        meet_url = sys.argv[1]
    
    print("Iniciando o Chromium com Playwright...")
    with sync_playwright() as p:
        # Launch persistent context to reuse existing login session if any
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=[
                '--use-fake-ui-for-media-stream',
                '--use-fake-device-for-media-stream',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--remote-debugging-port=9222'
            ],
            permissions=['microphone', 'camera']
        )
        
        page = context.new_page()
        print(f"Navegando para o Google Meet: {meet_url}")
        page.goto(meet_url)
        
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            print("[Aviso] Timeout ao esperar networkidle, continuando...")
        time.sleep(5)
        page.screenshot(path="meet_landing.png")
        print("Página do Meet carregada. Screenshot salvo em 'meet_landing.png'.")
        
        # Desativar câmera e microfone na tela de entrada se estiverem ativos
        print("Verificando se câmera e microfone estão ativos...")
        try:
            # 1. Encontrar botão do microfone
            mic_btn = page.locator('div[role="button"][aria-label*="microfone" i], div[role="button"][aria-label*="microphone" i]').first
            if mic_btn.is_visible():
                label = mic_btn.get_attribute("aria-label") or ""
                # Se o label contiver "desativar" ou "silenciar" ou "mute", significa que está ATIVO, então clicamos para desativar.
                if any(w in label.lower() for w in ["desativar", "silenciar", "mute", "desligar"]):
                    print(f"Microfone ativo (Aria Label: '{label}'). Clicando para desativar...")
                    mic_btn.click()
                    time.sleep(1)
                else:
                    print(f"Microfone já está desativado (Aria Label: '{label}').")
            else:
                # Se não encontrar o botão visível, tenta o atalho Ctrl+D como garantia
                print("Botão de microfone não encontrado. Enviando Ctrl+D...")
                page.keyboard.press("Control+d")
                time.sleep(1)

            # 2. Encontrar botão da câmera
            cam_btn = page.locator('div[role="button"][aria-label*="câmera" i], div[role="button"][aria-label*="camera" i]').first
            if cam_btn.is_visible():
                label = cam_btn.get_attribute("aria-label") or ""
                if any(w in label.lower() for w in ["desativar", "desligar", "turn off", "mute"]):
                    print(f"Câmera ativa (Aria Label: '{label}'). Clicando para desativar...")
                    cam_btn.click()
                    time.sleep(1)
                else:
                    print(f"Câmera já está desativada (Aria Label: '{label}').")
            else:
                print("Botão de câmera não encontrado. Enviando Ctrl+E...")
                page.keyboard.press("Control+e")
                time.sleep(1)
        except Exception as e:
            print(f"Erro ao desativar áudio/vídeo: {e}")
            
        page.screenshot(path="meet_muted.png")
        print("Áudio e vídeo desativados. Screenshot salvo em 'meet_muted.png'.")
        
        joined = False
        print("Tentando entrar na reunião...")
        for attempt in range(6):
            # Dismiss tooltip if any (e.g. click "Entendi" or "Got it")
            try:
                tooltip_btn = page.locator('button:has-text("Entendi"), div[role="button"]:has-text("Entendi")').first
                if tooltip_btn.is_visible():
                    print("Dispensando tooltip informativa...")
                    tooltip_btn.click()
                    time.sleep(1)
            except:
                pass

            # Check if Participar agora is visible
            btn_participar_agora = page.locator('button:has-text("Participar agora"), button:has-text("Join now")').first
            if btn_participar_agora.is_visible():
                print("Botão 'Participar agora' encontrado e visível. Clicando...")
                btn_participar_agora.click()
                joined = True
                break

            # Check if Mudar para este dispositivo / Outras formas de participar is visible
            btn_outras_formas = page.locator('button:has-text("Outras formas de participar"), div[role="button"]:has-text("Outras formas de participar")').first
            if btn_outras_formas.is_visible():
                print("Botão 'Outras formas de participar' encontrado. Clicando para expandir...")
                btn_outras_formas.click()
                time.sleep(1.5)
                # Now try to find 'Participar por aqui também'
                btn_por_aqui = page.locator('button:has-text("Participar por aqui também"), span:has-text("Participar por aqui também")').first
                if btn_por_aqui.is_visible():
                    print("Botão 'Participar por aqui também' encontrado. Clicando...")
                    btn_por_aqui.click()
                    joined = True
                    break
                else:
                    # check all buttons inside the expanded menu
                    buttons = page.locator("button, [role='button'], [role='menuitem']").all()
                    for btn in buttons:
                        try:
                            text = btn.inner_text().strip().lower()
                            if "participar por aqui" in text or "entrar também" in text or "join here too" in text:
                                if btn.is_visible():
                                    print(f"Botão no menu encontrado: '{btn.inner_text()}'. Clicando...")
                                    btn.click()
                                    joined = True
                                    break
                        except:
                            continue
                if joined:
                    break

            # Fallback to search all visible buttons
            buttons = page.locator("button, [role='button']").all()
            join_button = None
            for btn in buttons:
                try:
                    text = btn.inner_text().strip().lower()
                    if any(phrase in text for phrase in ["participar", "pedir para", "join", "ask to", "entrar"]):
                        if btn.is_visible():
                            join_button = btn
                            break
                except:
                    continue
            
            if join_button:
                print(f"Botão de participação fallback encontrado: '{join_button.inner_text()}'. Clicando...")
                join_button.click()
                joined = True
                break
                
            time.sleep(2)
            
        if not joined:
            print("Não foi possível entrar na reunião automaticamente. Se necessário, clique manualmente.")
            
        print("Aguardando entrada...")
        time.sleep(10)
        page.screenshot(path="meet_joined.png")
        print("Screenshot pós-participação salvo em 'meet_joined.png'.")
        
        print("Tentando abrir a janela de chat...")
        chat_button = None
        selectors = [
            'button[aria-label*="chat" i]',
            'button[aria-label*="conversar" i]',
            '[aria-label*="chat" i]',
            '[aria-label*="conversar" i]',
            'button:has-text("Chat")',
            'button:has-text("Conversar")'
        ]
        for sel in selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible():
                    chat_button = btn
                    break
            except Exception:
                continue
                
        if chat_button:
            print("Botão do chat encontrado. Clicando...")
            chat_button.click()
            time.sleep(3)
            page.screenshot(path="meet_chat_open.png")
            print("Chat aberto. Screenshot salvo em 'meet_chat_open.png'.")
        else:
            print("Não foi possível abrir o chat automaticamente. Se necessário, abra-o manualmente no navegador.")
            
        print("\n=== Monitorando chat por links de formulário do Google ===")
        detected_links = set()
        form_filled = False
        
        max_duration = 10800  # 3 horas
        start_time = time.time()
        
        while time.time() - start_time < max_duration and not form_filled:
            try:
                # Find all links
                links = page.locator("a").all()
                for link_loc in links:
                    try:
                        href = link_loc.get_attribute("href")
                        if href and ("forms.gle" in href or "docs.google.com/forms" in href):
                            if href not in detected_links:
                                print(f"\n[!] Novo formulário detectado no chat: {href}")
                                detected_links.add(href)
                                form_filled = fill_google_form(context, href)
                                if form_filled:
                                    break
                    except Exception:
                        continue
            except Exception as e:
                print(f"Erro ao escanear chat: {e}")
                
            if form_filled:
                break
                
            elapsed = int(time.time() - start_time)
            print(f"Escanando chat... {elapsed}s. Links encontrados: {len(detected_links)}", end="\r")
            time.sleep(5)
            
        if form_filled:
            print("\n[Sucesso] Script finalizado com sucesso!")
        else:
            print("\n[Aviso] Script finalizado sem preencher o formulário ou tempo limite atingido.")
            
        # Keeping it running for a bit to let the user review
        print("Mantendo o navegador aberto por mais 60 segundos antes de fechar...")
        time.sleep(60)
        context.close()

if __name__ == "__main__":
    main()
