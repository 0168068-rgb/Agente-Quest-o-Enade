import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = '/home/hamilcar/Downloads/token_drive.json'
FOLDER_ID = '1xD0CO5tEvR0UjJFyPAyQSvravvbhG8G5'  # Pasta HAMILCAR para as PSs

# Todas as 22 disciplinas
disciplinas_pastas = [
    "Cabeamento estruturado II (seg)",
    "Compiladores",
    "Desenvolvimento de Dispositivos Móveis",
    "Estrutura de dados(seg)",
    "Gerenciamento de Redes",
    "Infraestrutura de rede (seg)",
    "Infraestrutura de TI (4º per Redes)",
    "Infraestrutura e Serviços de TI",
    "Interação Humano-Computador",
    "Programação em Python(seg)",
    "Programação WEB II- Desenvolvimento Back-end",
    "Projetos de Redes de Computadores (seg)",
    "Redes Convergentes",
    "Redes de Alta disponibilidade (4º Per redes)",
    "Redes de Computadores(seg)",
    "Redes de Longa Distância",
    "Redes sem Fio (4º Per Redes)",
    "Segurança da Informação",
    "Segurança da Informação e Legislação",
    "Segurança de Redes de Computadores",
    "Servidores e computação na Nuvem",
    "Sistemas Operacionais de Redes Abertas"
]

def autenticar():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        else:
            print("Token não encontrado ou inválido. Execute a autenticação primeiro.")
            return None
    return creds

def fazer_upload(creds):
    if not creds:
        return
    service = build('drive', 'v3', credentials=creds)
    root_dir = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD"
    
    print("Iniciando upload dos arquivos PS (DOCX) para o Google Drive...")
    print(f"Pasta de destino: HAMILCAR (ID: {FOLDER_ID})\n")
    
    enviados = 0
    for pasta in disciplinas_pastas:
        caminho_ps = os.path.join(root_dir, pasta, "questao_2026-3", "PS")
        if not os.path.exists(caminho_ps):
            print(f"⚠️ Pasta não encontrada: {caminho_ps}")
            continue
        
        arquivos = [f for f in os.listdir(caminho_ps) if f.startswith('PS ') and f.endswith('.docx')]
        if not arquivos:
            print(f"⚠️ Nenhum DOCX de PS encontrado em: {caminho_ps}")
            continue
        
        filename = arquivos[0]
        filepath = os.path.join(caminho_ps, filename)
        print(f"Enviando '{filename}'...")
        
        try:
            file_metadata = {
                'name': filename,
                'parents': [FOLDER_ID]
            }
            media = MediaFileUpload(
                filepath,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                resumable=True
            )
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(f" -> Sucesso! ID no Drive: {file.get('id')}")
            enviados += 1
        except Exception as e:
            print(f"❌ Erro ao enviar {filename}: {e}")
    
    print(f"\nUpload concluído!")
    print(f"Total de arquivos enviados para o Google Drive: {enviados}/22")

if __name__ == "__main__":
    creds = autenticar()
    fazer_upload(creds)
