import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Escopo para leitura no Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

CREDENTIALS_PATH = 'credentials_gmail.json'
TOKEN_PATH = 'token_drive.json'

# IDs obtidos do caminho
TARGET_FOLDER_ID = '1QkWPHMFTkCLKbavnLrSMgjausB_AwwMq'
SHARED_DRIVE_ID = '0AKC7IF9fTUDgUk9PVA'

def autenticar():
    creds = None
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception as e:
            print(f"Erro ao carregar token existente: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Token expirado. Atualizando token do Google Drive...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Erro ao atualizar token: {e}. Solicitando nova autenticação...")
                creds = None

        if not creds:
            if not os.path.exists(CREDENTIALS_PATH):
                print(f"Erro: O arquivo de credenciais '{CREDENTIALS_PATH}' não foi encontrado.")
                return None

            print("Iniciando fluxo de login no navegador para o Google Drive...")
            print("Importante: Faça login com a conta 0168068@professor.unig.edu.br")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)

        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
            print(f"Token salvo com sucesso em: {TOKEN_PATH}")

    return creds

def listar_arquivos_pasta(creds, folder_id):
    service = build('drive', 'v3', credentials=creds)
    print(f"\nListing items inside folder ID: {folder_id}...\n")

    query = f"'{folder_id}' in parents and trashed = false"

    try:
        results = service.files().list(
            q=query,
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()

        items = results.get('files', [])

        if not items:
            print("Nenhum item encontrado nesta pasta.")
            return []

        print(f"Total de itens encontrados: {len(items)}\n")
        print(f"{'NOME':<45} | {'TIPO':<30} | {'ID':<35}")
        print("-" * 115)
        for item in items:
            name = item.get('name')
            mime = item.get('mimeType').split('.')[-1] if '.' in item.get('mimeType') else item.get('mimeType')
            item_id = item.get('id')
            print(f"{name:<45} | {mime:<30} | {item_id:<35}")

        return items

    except Exception as e:
        print(f"Erro ao listar arquivos do Google Drive: {e}")
        return []

if __name__ == '__main__':
    creds = autenticar()
    if creds:
        listar_arquivos_pasta(creds, TARGET_FOLDER_ID)
