import os
import datetime
import openpyxl
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token_drive_rw.json'

SEGUNDA_ENTRADA_ID = '1LX5DsKxWGolJ_sYpDH8euFUSAANdqMJN'

def test_uma_planilha():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)

    # Pick first subfolder
    res = drive_service.files().list(
        q=f"'{SEGUNDA_ENTRADA_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        fields="files(id, name)",
        pageSize=1,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    sf = res.get('files', [])[0]

    # Pick first spreadsheet in subfolder
    f_res = drive_service.files().list(
        q=f"'{sf['id']}' in parents and (mimeType = 'application/vnd.google-apps.spreadsheet' or mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') and trashed = false",
        fields="files(id, name, mimeType)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    f = f_res.get('files', [])[0]

    print(f"Testando atualização no arquivo: '{f['name']}' ({f['mimeType']}) ID: {f['id']}")

    local_path = f"/tmp/test_{f['id']}.xlsx"
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

    wb = openpyxl.load_workbook(local_path)
    sheet_name = 'Página2' if 'Página2' in wb.sheetnames else ('Página 2' if 'Página 2' in wb.sheetnames else wb.sheetnames[1])
    ws = wb[sheet_name]

    print(f"Valor antigo em {sheet_name}!D2: {ws['D2'].value}")
    # Set new value
    ws['D2'] = "24/09/2026"
    ws.sheet_state = 'hidden'
    print(f"Novo valor em {sheet_name}!D2: {ws['D2'].value}, Estado: {ws.sheet_state}")

    wb.save(local_path)

    media = MediaFileUpload(local_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', resumable=True)
    
    updated = drive_service.files().update(
        fileId=f['id'],
        media_body=media,
        supportsAllDrives=True
    ).execute()

    print(f"Atualizado com sucesso! File ID: {updated['id']}")

    os.remove(local_path)

if __name__ == '__main__':
    test_uma_planilha()
