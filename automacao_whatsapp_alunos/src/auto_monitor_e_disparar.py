import urllib.request
import json
import time
import subprocess
import threading
import http.server
import socketserver

PORT = 8090
DIRECTORY = "/home/hamilcar/Antigravity"
BASE_URL = "http://localhost:8085"
GLOBAL_API_KEY = "multi_karambola_token_2026"
INSTANCE_NAME = "karambola"

disparado = False

def monitor_conexao():
    global disparado
    print("🔍 Monitor de conexão WhatsApp iniciado...")
    while not disparado:
        try:
            url = f"{BASE_URL}/instance/connectionState/{INSTANCE_NAME}"
            req = urllib.request.Request(url, headers={"apikey": GLOBAL_API_KEY})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                state = data.get("instance", {}).get("state", "close")
                if state == "open":
                    print("\n🎉 WhatsApp Conectado com sucesso! Disparando mensagens de boas-vindas...")
                    disparado = True
                    subprocess.run(["python3", "/home/hamilcar/Antigravity/disparar_mensagens_boas_vindas.py"])
                    break
        except Exception as e:
            pass
        time.sleep(2)

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print(f"Servidor ativo em http://localhost:{PORT}/ver_qrcode.html")
        httpd.serve_forever()

if __name__ == "__main__":
    t_monitor = threading.Thread(target=monitor_conexao, daemon=True)
    t_monitor.start()
    run_server()
