import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Escopo para acesso completo e gravação de arquivos no Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

CREDENTIALS_PATH = '/home/hamilcar/Downloads/credentials.json'
TOKEN_PATH = '/home/hamilcar/Downloads/token_drive.json'
FOLDER_ID = '1-qVfowV-gX_7CwWHOCDTTJVoZaylaGft' # ID da pasta AD-AVALIAÇÃO DIAGNÓSTICA fornecido pelo usuário

# Dicionário de disciplinas para localizar os arquivos locais
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
            print("Token expirado. Atualizando credenciais do Drive...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                print(f"Erro: O arquivo {CREDENTIALS_PATH} não foi encontrado na pasta de Downloads.")
                return None
                
            print("Iniciando fluxo de login no navegador para o Google Drive...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
            
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            print(f"Token do Google Drive gerado e salvo com sucesso!")
            
    return creds

def fazer_upload_arquivos(creds):
    if not creds:
        return
        
    service = build('drive', 'v3', credentials=creds)
    root_dir = "/home/hamilcar/onedrive- Hamilcar/Documentos/NEAD"
    
    print("\nIniciando o upload dos arquivos DOCX para a pasta do Google Drive...")
    print(f"ID da Pasta de Destino: {FOLDER_ID}\n")
    
    enviados = 0
    for pasta in disciplinas_pastas:
        # Monta o caminho local da pasta de questões AD
        caminho_local_ad = os.path.join(root_dir, pasta, "questao_2026-3", "AD")
        if not os.path.exists(caminho_local_ad):
            print(f"⚠️ Pasta local não encontrada: {caminho_local_ad}")
            continue
            
        # Procura o arquivo .docx na pasta
        arquivos = [f for f in os.listdir(caminho_local_ad) if f.endswith('.docx')]
        if not arquivos:
            print(f"⚠️ Nenhum arquivo DOCX encontrado na pasta: {caminho_local_ad}")
            continue
            
        filename = arquivos[0]
        filepath = os.path.join(caminho_local_ad, filename)
        
        print(f"Enviando '{filename}'...")
        
        try:
            # Configuração dos metadados do arquivo no Drive
            file_metadata = {
                'name': filename,
                'parents': [FOLDER_ID]
            }
            
            # Realiza o upload binário
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
            
    print(f"\nUpload concluído com sucesso!")
    print(f"Total de arquivos enviados para o Google Drive: {enviados}/22")

if __name__ == "__main__":
    creds = autenticar()
    fazer_upload_arquivos(creds)
