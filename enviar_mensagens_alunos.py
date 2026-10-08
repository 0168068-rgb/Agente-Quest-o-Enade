import urllib.request
import json
import time

BASE_URL = "http://localhost:8085"
GLOBAL_API_KEY = "multi_karambola_token_2026"
INSTANCE_NAME = "karambola"

alunos = [
    {
        "nome": "Fabiano da Silva Pereira Junior",
        "primeiro_nome": "Fabiano",
        "numero": "5521981497448"
    },
    {
        "nome": "Gabriel de Souza Matheus",
        "primeiro_nome": "Gabriel",
        "numero": "5521991659791"
    },
    {
        "nome": "Gustavo de Oliveira",
        "primeiro_nome": "Gustavo",
        "numero": "5521967779019"
    },
    {
        "nome": "Verismaldo Ferreira Nascimento",
        "primeiro_nome": "Verismaldo",
        "numero": "5521984125493"
    },
    {
        "nome": "Vinicius Pontes de Laia",
        "primeiro_nome": "Vinicius",
        "numero": "5521995937048"
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
            "linkPreview": False
        },
        "text": text
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": True, "details": str(e)}

results = []

for aluno in alunos:
    msg = (
        f"Olá, {aluno['primeiro_nome']}! Tudo bem?\n\n"
        f"Seja muito bem-vindo! Sou o Coordenador do Curso de Redes e estou entrando em contato para lhe dar as boas-vindas oficiais.\n\n"
        f"Gostaria de ressaltar a necessidade da sua participação na nossa Aula Inaugural, que será um momento fundamental para apresentarmos a estrutura do curso, tirarmos dúvidas e alinharmos os primeiros passos da sua jornada acadêmica.\n\n"
        f"Além disso, é essencial mantermos este contato direto com a coordenação. Estou totalmente à disposição para ajudá-lo no que for preciso durante todo o seu curso.\n\n"
        f"Conto com a sua presença na Aula Inaugural! Qualquer dúvida, pode me responder por aqui.\n\n"
        f"Atenciosamente,\n"
        f"Coordenação do Curso de Redes"
    )
    
    print(f"Enviando para {aluno['nome']} ({aluno['numero']})...")
    res = send_whatsapp_message(aluno['numero'], msg)
    print("Resultado:", res)
    results.append({"aluno": aluno['nome'], "numero": aluno['numero'], "resposta": res})
    time.sleep(2) # Pequeno intervalo entre envios para evitar flood

with open("relatorio_envio_whatsapp.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\nEnvio concluído!")
