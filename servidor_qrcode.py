import http.server
import socketserver
import urllib.request
import json
import subprocess
import os

PORT = 8090
DIRECTORY = "/home/hamilcar/Antigravity"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        if self.path == "/api/disparar":
            print("\n🚀 Instância conectada! Executando disparo automático das mensagens...")
            subprocess.Popen(["python3", "/home/hamilcar/Antigravity/disparar_mensagens_boas_vindas.py"])
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "disparo_iniciado"}).encode("utf-8"))
        else:
            self.send_error(404)

print(f"Servidor do QR Code iniciado em http://localhost:{PORT}/ver_qrcode.html")
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
