import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token_drive_rw.json'

SEGUNDA_ENTRADA_ID = '1LX5DsKxWGolJ_sYpDH8euFUSAANdqMJN'

def inspecionar():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)

    # List subfolders inside Segunda Entrada
    res = drive_service.files().list(
        q=f"'{SEGUNDA_ENTRADA_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        fields="files(id, name)",
        pageSize=100,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    subfolders = res.get('files', [])
    print(f"Encontradas {len(subfolders)} subpastas em Segunda Entrada.\n")

    for sf in subfolders:
        sf_id = sf['id']
        sf_name = sf['name']
        print(f"📁 Subpasta: '{sf_name}' ({sf_id})")

        # List files in this subfolder
        f_res = drive_service.files().list(
            q=f"'{sf_id}' in parents and trashed = false",
            fields="files(id, name, mimeType)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files = f_res.get('files', [])

        for f in files:
            print(f"   - Arquivo: '{f['name']}' | Tipo: {f['mimeType']} | ID: {f['id']}")
            if f['mimeType'] == 'application/vnd.google-apps.spreadsheet':
                try:
                    spreadsheet = sheets_service.spreadsheets().get(spreadsheetId=f['id']).execute()
                    sheets = spreadsheet.get('sheets', [])
                    print(f"     📊 Abas da planilha:")
                    for s in sheets:
                        props = s['properties']
                        hidden = props.get('hidden', False)
                        title = props.get('title')
                        sheet_id = props.get('sheetId')
                        print(f"        * Sheet Title: '{title}' (ID: {sheet_id}, Hidden: {hidden})")

                        # Get cell D2 value
                        val_res = sheets_service.spreadsheets().values().get(
                            spreadsheetId=f['id'],
                            range=f"'{title}'!D2"
                        ).execute()
                        vals = val_res.get('values', [])
                        d2_val = vals[0][0] if vals and vals[0] else "(vazio)"
                        print(f"          D2: {d2_val}")

                except Exception as e:
                    print(f"     ❌ Erro ao ler planilha Google Sheets: {e}")

            elif f['mimeType'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                print(f"     ⚠️ Arquivo Excel (.xlsx) local no Drive. Precisa converter ou processar.")

        print()

if __name__ == '__main__':
    inspecionar()
