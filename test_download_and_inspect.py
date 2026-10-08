import os
import io
import openpyxl
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token_drive_rw.json'

SEGUNDA_ENTRADA_ID = '1LX5DsKxWGolJ_sYpDH8euFUSAANdqMJN'

def testar():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)

    # List files in Segunda Entrada subfolders
    res = drive_service.files().list(
        q=f"'{SEGUNDA_ENTRADA_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        fields="files(id, name)",
        pageSize=10,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    subfolders = res.get('files', [])

    for sf in subfolders:
        sf_id = sf['id']
        sf_name = sf['name']
        print(f"\n📁 Subpasta: '{sf_name}'")

        f_res = drive_service.files().list(
            q=f"'{sf_id}' in parents and trashed = false",
            fields="files(id, name, mimeType)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()

        for f in f_res.get('files', []):
            if f['mimeType'] in ['application/vnd.google-apps.spreadsheet', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                print(f"  📊 Baixando e inspecionando planilha: '{f['name']}' ({f['mimeType']})")

                local_path = f"/tmp/{f['id']}.xlsx"
                if f['mimeType'] == 'application/vnd.google-apps.spreadsheet':
                    request = drive_service.files().export_media(
                        fileId=f['id'],
                        mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                else:
                    request = drive_service.files().get_media(fileId=f['id'])

                with open(local_path, 'wb') as fh:
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()

                wb = openpyxl.load_workbook(local_path, data_only=False)
                print(f"     Nomes das abas: {wb.sheetnames}")
                for sname in wb.sheetnames:
                    ws = wb[sname]
                    d2_val = ws['D2'].value
                    print(f"     Aba '{sname}': Celula D2 = {d2_val!r}, Estado da aba = {ws.sheet_state}")

                os.remove(local_path)
                break

if __name__ == '__main__':
    testar()
