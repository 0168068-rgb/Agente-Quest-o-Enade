import os
import sys
import time
from playwright.sync_api import sync_playwright

def main():
    user_data_dir = "/home/hamilcar/Antigravity/playwright_user_data"
    print("=== ASSISTENTE DE LOGIN DO GOOGLE ===")
    print("Uma janela do navegador Chromium vai se abrir na sua tela.")
    print("Por favor, faça login com o seu e-mail: 0168068@professor.edu.br")
    print("Após fazer login com sucesso e ver a página da sua conta, feche a janela do navegador ou pressione Enter aqui para finalizar.")
    print("=====================================")
    
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
        page.goto("https://accounts.google.com/signin")
        
        # We wait for the user to login.
        # We can monitor if the url changes to something like myaccount.google.com or has signin/v2/challenge
        try:
            # Wait up to 5 minutes (300 seconds)
            for i in range(300):
                if "myaccount.google.com" in page.url:
                    print("\n[Sucesso] Login detectado! Você está conectado.")
                    time.sleep(3)
                    break
                print(f"Aguardando login... URL atual: {page.url}", end="\r")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nProcesso interrompido pelo usuário.")
        
        print("\nFechando o navegador e salvando a sessão...")
        context.close()
        print("Sessão salva com sucesso!")

if __name__ == "__main__":
    main()
