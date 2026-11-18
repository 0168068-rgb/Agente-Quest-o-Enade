import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token_drive_rw.json'

SEGUNDA_ENTRADA_ID = '1LX5DsKxWGolJ_sYpDH8euFUSAANdqMJN'

def inspecionar():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)

    res = drive_service.files().list(
        q=f"'{SEGUNDA_ENTRADA_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        fields="files(id, name)",
        pageSize=100,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    subfolders = res.get('files', [])

    print(f"Total de subpastas em Segunda Entrada: {len(subfolders)}\n")

    mapeamento = []

    for sf in subfolders:
        sf_id = sf['id']
        sf_name = sf['name']

        f_res = drive_service.files().list(
            q=f"'{sf_id}' in parents and trashed = false",
            fields="files(id, name, mimeType, webViewLink)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()

        files = f_res.get('files', [])
        print(f"📁 Subpasta: '{sf_name}' ({len(files)} arquivos)")

        pagina_file = None
        planilha_file = None

        for f in files:
            print(f"   - {f['name']} | Tipo: {f['mimeType']} | ID: {f['id']}")
            if f['mimeType'] in ['application/vnd.google-apps.spreadsheet', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                planilha_file = f
            elif f['mimeType'] in ['application/vnd.google-apps.site', 'application/vnd.google-apps.document', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/html']:
                pagina_file = f

        mapeamento.append({
            'subpasta': sf_name,
            'subpasta_id': sf_id,
            'pagina': pagina_file,
            'planilha': planilha_file
        })
        print()

    with open('mapeamento_segunda_entrada.json', 'w') as mf:
        json.dump(mapeamento, mf, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    inspecionar()
