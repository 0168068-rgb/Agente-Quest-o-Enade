import time
import urllib.parse
from playwright.sync_api import sync_playwright

contatos = [
    {
        "nome": "Ricardo Rodrigo de Almeida",
        "primeiro_nome": "Ricardo",
        "numero": "5521979900622"
    },
    {
        "nome": "Rodholfo Barboza Silveira Silva",
        "primeiro_nome": "Rodholfo",
        "numero": "5521964570371"
    },
    {
        "nome": "Verismaldo Ferreira Nascimento",
        "primeiro_nome": "Verismaldo",
        "numero": "5521984125493"
    }
]

def main():
    print("🚀 Automação de Envio no WhatsApp Web Oficial iniciada...\n")

    with sync_playwright() as p:
        # Tenta usar o contexto já existente ou abre novo navegador persistente
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--no-sandbox"]
        )
        context = browser.new_context(viewport=None)
        page = context.new_page()

        print("Navegando para https://web.whatsapp.com...")
        page.goto("https://web.whatsapp.com")

        print("Aguardando carregamento da sessão do WhatsApp Web...")
        # Aguarda a tela inicial do WhatsApp Web estar pronta (pesquisa ou lista de chats)
        try:
            page.wait_for_selector("div[contenteditable='true'], #pane-side, header", timeout=90000)
            print("✅ WhatsApp Web conectado e pronto!")
        except Exception as e:
            print("⚠️ Aguardando leitura do QR code...")
            page.wait_for_selector("#pane-side, div[contenteditable='true']", timeout=120000)

        time.sleep(3)

        for contato in contatos:
            mensagem = (
                f"Olá, {contato['primeiro_nome']}! Tudo bem?\n\n"
                f"Seja muito bem-vindo(a) ao curso EAD de ADS, GTI e Redes da *4ª entrada da UNIG*! 🎓✨\n\n"
                f"Meu nome é *Hamilcar Silva* e sou o coordenador dos cursos. Gostaria de convidar você para a nossa *Aula Inaugural*, onde apresentaremos a forma de avaliação, o funcionamento do Ambiente Virtual de Aprendizado (AVA) e tiraremos todas as suas dúvidas.\n\n"
                f"📅 *Detalhes da Aula Inaugural:*\n"
                f"• *Data:* Terça-feira, 29 de setembro\n"
                f"• *Horário:* 16:00 – 17:00 (4:00 – 5:00pm)\n"
                f"• *Fuso horário:* America/Sao_Paulo\n"
                f"• *Link da videochamada (Google Meet):* https://meet.google.com/xmr-bxni-vza\n\n"
                f"Sua participação é fundamental para começar com o pé direito! Conto com você.\n\n"
                f"Atenciosamente,\n"
                f"*Hamilcar Silva*\n"
                f"Coordenador dos Cursos EAD (ADS, GTI e Redes) - UNIG"
            )

            msg_encoded = urllib.parse.quote(mensagem)
            url_chat = f"https://web.whatsapp.com/send?phone={contato['numero']}&text={msg_encoded}"

            print(f"\nAbrindo conversa com {contato['nome']} ({contato['numero']})...")
            page.goto(url_chat)

            # Aguarda a caixa de texto ou tela da conversa carregar
            time.sleep(5)
            
            try:
                # Procura caixa de digitação
                chat_box = page.wait_for_selector('div[contenteditable="true"][data-tab="10"], footer div[contenteditable="true"]', timeout=15000)
                if chat_box:
                    chat_box.focus()
                    time.sleep(1)
                    page.keyboard.press("Enter")
                    print(f"✅ Mensagem enviada com SUCESSO para {contato['nome']}!")
                    time.sleep(4)
            except Exception as e:
                print(f"⚠️ Tentando clique no botão de envio para {contato['nome']}...")
                try:
                    send_btn = page.wait_for_selector('button span[data-icon="send"], span[data-icon="send"]', timeout=5000)
                    if send_btn:
                        send_btn.click()
                        print(f"✅ Mensagem enviada via clique para {contato['nome']}!")
                        time.sleep(4)
                except Exception as ex:
                    print(f"❌ Não foi possível enviar para {contato['nome']}: {ex}")

        print("\n🎉 Todas as mensagens foram entregues!")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    main()
