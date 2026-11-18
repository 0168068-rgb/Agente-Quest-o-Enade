import urllib.request
import urllib.parse
import json
import base64
import os
import sys

# Configurações padrão da Evolution API local
BASE_URL = "http://localhost:8085"
GLOBAL_API_KEY = "multi_karambola_token_2026"
INSTANCE_NAME = "karambola"

def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    
    headers["apikey"] = GLOBAL_API_KEY
    headers["Content-Type"] = "application/json"
    
    req_data = None
    if data:
        req_data = json.dumps(data).encode("utf-8")
        
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode("utf-8")
            return json.loads(res_data)
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        try:
            return json.loads(error_msg)
        except:
            return {"error": True, "message": error_msg}
    except Exception as e:
        return {"error": True, "message": str(e)}

def test_connection():
    print("Testando conexão com a Evolution API...")
    url = f"{BASE_URL}/instance/fetchInstances"
    res = make_request(url)
    if isinstance(res, list):
        print(" -> Conexão bem-sucedida! A API está online.")
        return True
    else:
        print(" -> Erro: Não foi possível conectar à API. Verifique se o contêiner Docker está rodando e se a API_KEY está correta.")
        print(f" -> Detalhes: {res}")
        return False

def create_instance():
    print(f"Criando instância '{INSTANCE_NAME}'...")
    url = f"{BASE_URL}/instance/create"
    data = {
        "instanceName": INSTANCE_NAME,
        "token": "karambola_token",
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }
    res = make_request(url, method="POST", data=data)
    
    if "instance" in res or (isinstance(res, dict) and "instanceName" in res.get("instance", {})):
        print(f" -> Instância '{INSTANCE_NAME}' criada com sucesso!")
        return True
    elif isinstance(res, dict) and "instance" in res and res["instance"].get("status") == "created":
        print(f" -> Instância '{INSTANCE_NAME}' já existia ou foi criada.")
        return True
    else:
        # Tratar erro de instância já existente
        error_msg = ""
        if isinstance(res, dict):
            response_obj = res.get("response", {})
            if isinstance(response_obj, dict):
                messages = response_obj.get("message", [])
                if isinstance(messages, list) and len(messages) > 0:
                    error_msg = str(messages[0])
            if not error_msg:
                error_msg = str(res.get("message", ""))
                
        if "already in use" in error_msg.lower() or "already exists" in error_msg.lower():
            print(f" -> Instância '{INSTANCE_NAME}' já existe e está pronta para uso.")
            return True
            
        print(f" -> Falha ao criar instância: {res}")
        return False

def get_qrcode():
    print("Buscando o QR Code de conexão...")
    url = f"{BASE_URL}/instance/connect/{INSTANCE_NAME}"
    res = make_request(url, method="GET")
    
    if isinstance(res, dict) and "base64" in res:
        qr_base64 = res["base64"]
        if qr_base64.startswith("data:image"):
            # Remover o cabeçalho base64 data:image/png;base64,
            qr_base64 = qr_base64.split(",")[-1]
            
        # Decodificar e salvar imagem local
        qr_bytes = base64.b64decode(qr_base64)
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qrcode.png")
        
        with open(output_path, "wb") as f:
            f.write(qr_bytes)
            
        print(" -> QR Code gerado e salvo com sucesso!")
        print(f" -> ARQUIVO SALVO EM: {output_path}")
        print(" -> Abra a imagem 'qrcode.png' no seu computador e escaneie com o WhatsApp do seu celular (Aparelhos Conectados).")
        return True
    elif isinstance(res, dict) and res.get("status") == "CONNECTED":
        print(" -> O celular já está conectado e a sessão está ativa!")
        return True
    else:
        print(f" -> Não foi possível obter o QR Code: {res}")
        return False

def send_message(number, text):
    print(f"Enviando mensagem para {number}...")
    url = f"{BASE_URL}/message/sendText/{INSTANCE_NAME}"
    
    # Garantir o formato simples do número (apenas números, DDD + número)
    clean_number = "".join(filter(str.isdigit, number))
    
    data = {
        "number": clean_number,
        "options": {
            "delay": 1200,
            "presence": "composing",
            "linkPreview": False
        },
        "text": text
    }
    
    res = make_request(url, method="POST", data=data)
    
    # Se retornar mensagem enviada
    if isinstance(res, dict) and "key" in res:
        print(" -> Mensagem enviada com sucesso!")
        return True
    else:
        print(f" -> Falha ao enviar mensagem: {res}")
        return False

if __name__ == "__main__":
    print("=== CLIENTE DE WHATSAPP - EVOLUTION API ===")
    
    if not test_connection():
        sys.exit(1)
        
    if not create_instance():
        sys.exit(1)
        
    # Verificar se o usuário quer gerar o QR Code ou enviar mensagem
    print("\nEscolha uma opção:")
    print("1. Gerar QR Code para conectar meu celular")
    print("2. Enviar uma mensagem de teste")
    
    try:
        opcao = input("Opção (1 ou 2): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nSaindo...")
        sys.exit(0)
        
    if opcao == "1":
        get_qrcode()
    elif opcao == "2":
        try:
            num = input("Digite o número com DDI e DDD (ex: 5521999999999): ").strip()
            msg = input("Digite o texto do aviso: ").strip()
            if num and msg:
                send_message(num, msg)
            else:
                print("Número ou mensagem inválidos.")
        except (KeyboardInterrupt, EOFError):
            print("\nCancelado.")
    else:
        print("Opção inválida.")
