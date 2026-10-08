import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

CREDENTIALS_PATH = 'credentials_gmail.json'
TOKEN_PATH = 'token_drive_rw.json'

PARENT_FOLDER_ID = '1QkWPHMFTkCLKbavnLrSMgjausB_AwwMq'
SOURCE_FOLDER_ID = '1mHsuQJjB8ZK9TbwdQ-m5VvqqqPGgF8C4' # Primeira Entrada subfolder

def autenticar():
    creds = None
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception as e:
            print(f"Erro ao carregar token: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Atualizando token...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Erro ao atualizar: {e}")
                creds = None

        if not creds:
            print("Iniciando login no navegador para permissão de escrita no Google Drive...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)

        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
            print(f"Token salvo em: {TOKEN_PATH}")

    return creds

if __name__ == '__main__':
    creds = autenticar()
    if creds:
        service = build('drive', 'v3', credentials=creds)
        print("Autenticado com sucesso para Leitura e Escrita no Drive!")
