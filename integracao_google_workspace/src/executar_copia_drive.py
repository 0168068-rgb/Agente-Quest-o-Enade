import os
import json
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token_drive_rw.json'

PARENT_FOLDER_ID = '1QkWPHMFTkCLKbavnLrSMgjausB_AwwMq'
SOURCE_FOLDER_ID = '1mHsuQJjB8ZK9TbwdQ-m5VvqqqPGgF8C4' # ID de "Primeira Entrada"
NEW_FOLDER_NAME = 'Segunda Entrada'

def obter_servico():
    if not os.path.exists(TOKEN_PATH):
        raise FileNotFoundError(f"Arquivo de token {TOKEN_PATH} não encontrado.")
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build('drive', 'v3', credentials=creds)

def criar_pasta(service, nome_pasta, parent_id):
    metadata = {
        'name': nome_pasta,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    nova_pasta = service.files().create(
        body=metadata,
        fields='id, name',
        supportsAllDrives=True
    ).execute()
    print(f"📁 Pasta criada: '{nome_pasta}' (ID: {nova_pasta['id']})")
    return nova_pasta['id']

def copiar_item_arquivo(service, file_id, file_name, file_mime, dest_folder_id):
    body = {
        'name': file_name,
        'parents': [dest_folder_id]
    }
    try:
        copia = service.files().copy(
            fileId=file_id,
            body=body,
            fields='id, name, mimeType',
            supportsAllDrives=True
        ).execute()
        print(f"   📄 Arquivo copiado: '{file_name}' (ID: {copia['id']})")
        return copia['id']
    except Exception as e:
        if 'application/vnd.google-apps.site' in file_mime:
            print(f"   ⚠️ Google Site não suporta cópia direta via Drive API: '{file_name}' ({e})")
        else:
            print(f"   ❌ Erro ao copiar '{file_name}': {e}")
        return None

def copiar_pasta_recursiva(service, src_folder_id, dest_folder_id):
    query = f"'{src_folder_id}' in parents and trashed = false"
    page_token = None
    
    while True:
        results = service.files().list(
            q=query,
            pageSize=100,
            pageToken=page_token,
            fields="nextPageToken, files(id, name, mimeType)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        
        items = results.get('files', [])
        for item in items:
            name = item['name']
            mime = item['mimeType']
            item_id = item['id']
            
            if mime == 'application/vnd.google-apps.folder':
                sub_dest_id = criar_pasta(service, name, dest_folder_id)
                copiar_pasta_recursiva(service, item_id, sub_dest_id)
            else:
                copiar_item_arquivo(service, item_id, name, mime, dest_folder_id)
                
        page_token = results.get('nextPageToken')
        if not page_token:
            break

def executar():
    service = obter_servico()
    
    # Check if 'Segunda Entrada' already exists in parent
    q = f"'{PARENT_FOLDER_ID}' in parents and name = '{NEW_FOLDER_NAME}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    res = service.files().list(
        q=q,
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    
    existentes = res.get('files', [])
    if existentes:
        target_folder_id = existentes[0]['id']
        print(f"Usando pasta existente '{NEW_FOLDER_NAME}' (ID: {target_folder_id})")
    else:
        target_folder_id = criar_pasta(service, NEW_FOLDER_NAME, PARENT_FOLDER_ID)
        
    print(f"\nIniciando cópia de tudo da pasta 'Primeira Entrada' (ID: {SOURCE_FOLDER_ID}) para 'Segunda Entrada' (ID: {target_folder_id})...\n")
    copiar_pasta_recursiva(service, SOURCE_FOLDER_ID, target_folder_id)
    print("\n✅ Cópia concluída com sucesso!")

if __name__ == '__main__':
    executar()
