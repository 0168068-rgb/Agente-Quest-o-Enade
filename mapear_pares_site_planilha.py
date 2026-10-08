import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token_drive_rw.json'
SEGUNDA_ENTRADA_ID = '1LX5DsKxWGolJ_sYpDH8euFUSAANdqMJN'

def gerar_mapeamento():
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

    pares = []

    for sf in subfolders:
        sf_id = sf['id']
        sf_name = sf['name']

        f_res = drive_service.files().list(
            q=f"'{sf_id}' in parents and trashed = false",
            fields="files(id, name, mimeType)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files = f_res.get('files', [])

        site_info = None
        sheet_info = None

        for f in files:
            if f['mimeType'] == 'application/vnd.google-apps.site':
                site_info = {
                    'name': f['name'],
                    'id': f['id'],
                    'edit_url': f"https://sites.google.com/d/{f['id']}/edit"
                }
            elif f['mimeType'] in ['application/vnd.google-apps.spreadsheet', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                sheet_info = {
                    'name': f['name'],
                    'id': f['id'],
                    'url': f"https://docs.google.com/spreadsheets/d/{f['id']}/edit"
                }

        if site_info and sheet_info:
            pares.append({
                'disciplina': sf_name,
                'site': site_info,
                'planilha': sheet_info
            })

    with open('pares_site_planilha_segunda_entrada.json', 'w', encoding='utf-8') as f:
        json.dump(pares, f, indent=2, ensure_ascii=False)

    print(f"Mapeamento gerado com sucesso! Total de pares encontrados: {len(pares)}")

if __name__ == '__main__':
    gerar_mapeamento()
