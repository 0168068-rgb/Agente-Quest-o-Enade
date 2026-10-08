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
    print("🚀 Iniciando WhatsApp Web Oficial via Playwright (Navegador Real)...")
    print("Isso usará o site oficial web.whatsapp.com onde o QR Code funciona 100% sem erros de conexão.\n")

    with sync_playwright() as p:
        # Abre o navegador com interface gráfica visível
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--start-maximized",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = browser.new_context(viewport=None)
        page = context.new_page()

        print("Acessando https://web.whatsapp.com...")
        page.goto("https://web.whatsapp.com")

        print("\n=======================================================")
        print("👉 POR FAVOR, ESCANEIE O QR CODE NA TELA DO NAVEGADOR")
        print("=======================================================\n")

        # Aguarda o WhatsApp Web carregar após o escaneamento (procura pela barra lateral de conversas)
        page.wait_for_selector("div[contenteditable='true']", timeout=120000)
        print("✅ WhatsApp Web conectado com sucesso!")
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

            print(f"\nEnviando mensagem para {contato['nome']} ({contato['numero']})...")
            page.goto(url_chat)

            try:
                # Aguarda o botão de enviar (ícone de avião de papel / enviar no WhatsApp Web)
                page.wait_for_selector('span[data-icon="send"]', timeout=20000)
                time.sleep(1)
                page.click('span[data-icon="send"]')
                print(f"✅ Mensagem enviada para {contato['nome']}!")
                time.sleep(3)
            except Exception as e:
                print(f"⚠️ Tentando pressionar ENTER para enviar...")
                try:
                    page.keyboard.press("Enter")
                    print(f"✅ Mensagem enviada via Enter para {contato['nome']}!")
                    time.sleep(3)
                except Exception as ex:
                    print(f"❌ Erro ao enviar para {contato['nome']}: {ex}")

        print("\n🎉 Todas as mensagens de boas-vindas foram disparadas!")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    main()
