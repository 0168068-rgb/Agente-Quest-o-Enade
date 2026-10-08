import urllib.request
import json
import time

BASE_URL = "http://localhost:8085"
GLOBAL_API_KEY = "multi_karambola_token_2026"
INSTANCE_NAME = "unig_ead"

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

def send_whatsapp_message(number, text):
    url = f"{BASE_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {
        "apikey": GLOBAL_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "number": number,
        "options": {
            "delay": 1200,
            "presence": "composing",
            "linkPreview": True
        },
        "text": text
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        if hasattr(e, 'read'):
            return {"error": True, "details": e.read().decode("utf-8")}
        return {"error": True, "details": str(e)}

def main():
    results = []
    print(f"Iniciando envio das mensagens via instância '{INSTANCE_NAME}'...\n")
    
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
        
        print(f"Enviando para {contato['nome']} ({contato['numero']})...")
        res = send_whatsapp_message(contato['numero'], mensagem)
        print("Resultado:", json.dumps(res, ensure_ascii=False))
        results.append({"contato": contato['nome'], "numero": contato['numero'], "resposta": res})
        time.sleep(2)
        
    with open("relatorio_envio_boas_vindas.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print("\nProcesso de envio finalizado. Relatório salvo em 'relatorio_envio_boas_vindas.json'.")

if __name__ == "__main__":
    main()
