import urllib.request
import json
import csv
import os
import sys

# Configurações da Evolution API
BASE_URL = "http://localhost:8085"
GLOBAL_API_KEY = "multi_karambola_token_2026"
INSTANCE_NAME = "karambola"

# Diretório padrão de Downloads do usuário
DOWNLOADS_DIR = "/home/hamilcar/Downloads"
OUTPUT_FILE = os.path.join(DOWNLOADS_DIR, "contatos_whatsapp.csv")

def get_contacts():
    print("Buscando contatos da agenda do WhatsApp...")
    url = f"{BASE_URL}/chat/findContacts/{INSTANCE_NAME}"
    
    headers = {
        "apikey": GLOBAL_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Body vazio para retornar todos os contatos
    data = json.dumps({}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode("utf-8")
            return json.loads(res_data)
    except Exception as e:
        print(f"Erro ao conectar com a API: {e}")
        return None

def export_to_csv(contacts):
    if not contacts or not isinstance(contacts, list):
        print("Nenhum contato encontrado para exportação.")
        return False
        
    print(f"Processando {len(contacts)} registros encontrados...")
    
    # Filtrar contatos (ignorar grupos e formatar número)
    filtered_contacts = []
    for c in contacts:
        # Pega apenas contatos individuais (isGroup == False)
        if c.get("isGroup") is True or c.get("type") == "group":
            continue
            
        jid = c.get("remoteJid", "")
        # Extrai o número do JID (ex: "5521999999999@s.whatsapp.net" -> "5521999999999")
        number = jid.split("@")[0] if jid else ""
        
        # Pega o nome do contato
        name = c.get("pushName") or c.get("name") or "Sem Nome"
        
        filtered_contacts.append({
            "Nome": name,
            "Numero": number,
            "WhatsApp_ID": jid
        })
        
    if not filtered_contacts:
        print("Nenhum contato individual (não-grupo) encontrado.")
        return False
        
    # Garantir que a pasta de downloads existe
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    
    try:
        # Grava em CSV delimitado por ponto e vírgula (formato brasileiro compatível direto com Excel)
        # utf-8-sig garante que o Excel do Windows abra com acentos corretos
        with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["Nome", "Numero", "WhatsApp_ID"], delimiter=";")
            writer.writeheader()
            writer.writerows(filtered_contacts)
            
        print("--------------------------------------------------------")
        print(" Contatos exportados com sucesso!")
        print(f" Total de contatos individuais: {len(filtered_contacts)}")
        print(f" Arquivo gerado em: {OUTPUT_FILE}")
        print("--------------------------------------------------------")
        print("Você pode abrir este arquivo diretamente no Excel ou LibreOffice!")
        return True
    except Exception as e:
        print(f"Erro ao gravar o arquivo CSV: {e}")
        return False

if __name__ == "__main__":
    print("=== EXPORTADOR DE CONTATOS DO WHATSAPP ===")
    contacts = get_contacts()
    if contacts:
        export_to_csv(contacts)
    else:
        print("Falha ao exportar contatos. Verifique se o contêiner Docker está ativo.")
