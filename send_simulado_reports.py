import os
import base64
import json
import urllib.request
import urllib.error
import csv

BASE_URL = "http://localhost:8085"
GLOBAL_API_KEY = "multi_karambola_token_2026"
INSTANCE_NAME = "karambola"
REPORTS_DIR = "/home/hamilcar/Downloads/Relatório individual do Simulado ENADE"
CONTACTS_FILE = "/home/hamilcar/Downloads/contatos_whatsapp.csv"

# Mapping names from files to contacts
# We will use this dictionary to handle exact matching and manual overrides (e.g. two Pedro Augustos)
MAPPING_OVERRIDE = {
    "Pedro Augusto": "5521981313519", # Pedro Augusto Bizarelo da Silva (has history and GTI student context)
    "Mikaella": "5521976344988",      # Mikaella💜
    "Bruno Luis": "5521964090324",    # Bruno Luis Torres Gomes
    "Cosme": "5511952118377",         # Cosme Quintino
    "Kaua Oliveira": "5521980923477"  # Kauã Oliveira
}

def get_base64_file(filepath):
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def send_document(number, filepath, filename, caption):
    url = f"{BASE_URL}/message/sendMedia/{INSTANCE_NAME}"
    base64_data = get_base64_file(filepath)
    
    payload = {
        "number": number,
        "mediatype": "document",
        "mimetype": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "media": base64_data,
        "fileName": filename,
        "caption": caption
    }
    
    headers = {
        "apikey": GLOBAL_API_KEY,
        "Content-Type": "application/json"
    }
    
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode("utf-8")
            res_json = json.loads(res_data)
            return True, res_json
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        try:
            return False, json.loads(error_msg)
        except:
            return False, error_msg
    except Exception as e:
        return False, str(e)

def load_contacts():
    contacts = []
    if not os.path.exists(CONTACTS_FILE):
        return contacts
    with open(CONTACTS_FILE, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            contacts.append(row)
    return contacts

def main():
    import sys
    send_messages = "--send" in sys.argv

    if not os.path.exists(REPORTS_DIR):
        print(f"Diretório de relatórios não encontrado: {REPORTS_DIR}")
        return

    files = [f for f in os.listdir(REPORTS_DIR) if f.endswith(".docx")]
    contacts = load_contacts()
    
    print("=== Mapeamento de Relatórios para Envio ===")
    mapped_jobs = []
    
    # We will identify the name in the file name
    # e.g., Relatorio_Individual_ENADE_2026_Pedro_Augusto_COM_GABARITO.docx
    for filename in files:
        filepath = os.path.join(REPORTS_DIR, filename)
        # Extract student name between 'ENADE_2026_' and '_COM_GABARITO'
        name_part = filename.replace("Relatorio_Individual_ENADE_2026_", "").replace("_COM_GABARITO.docx", "")
        # Replace underscores with spaces
        name_key = name_part.replace("_", " ").strip()
        
        # Determine number
        number = MAPPING_OVERRIDE.get(name_key)
        contact_name = None
        
        if not number:
            # Fallback fuzzy matching in contacts if not in override
            for c in contacts:
                if name_key.lower() in c['Nome'].lower():
                    number = c['Numero']
                    contact_name = c['Nome']
                    break
        else:
            for c in contacts:
                if c['Numero'] == number:
                    contact_name = c['Nome']
                    break
                    
        if number:
            mapped_jobs.append({
                "student_name": name_key,
                "contact_name": contact_name or name_key,
                "number": number,
                "filename": filename,
                "filepath": filepath
            })
            print(f"- {name_key} -> {contact_name} ({number}) | Arquivo: {filename}")
        else:
            print(f"⚠️ Não foi possível mapear o contato para: {name_key} (Arquivo: {filename})")

    if not send_messages:
        print("\n[MODO SIMULAÇÃO/DRY-RUN] Nenhuma mensagem foi enviada.")
        print("Para enviar os relatórios de verdade, execute o script com o argumento '--send':")
        print("python3 send_simulado_reports.py --send")
        return

    print("\nExecutando envio real...")
    for job in mapped_jobs:
        student = job["student_name"]
        number = job["number"]
        filepath = job["filepath"]
        filename = job["filename"]
        
        # Message caption
        caption = f"Olá, {student}! Segue o seu Relatório Individual do Simulado ENADE 2026."
        
        print(f"Enviando para {job['contact_name']} ({number})...")
        success, response = send_document(number, filepath, filename, caption)
        if success:
            print(f"  -> Sucesso! ID da mensagem: {response.get('key', {}).get('id', 'N/A')}")
        else:
            print(f"  -> FALHA: {response}")

if __name__ == "__main__":
    main()
