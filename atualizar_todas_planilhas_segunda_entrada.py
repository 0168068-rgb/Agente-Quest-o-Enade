import os
import datetime
import openpyxl
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token_drive_rw.json'

SEGUNDA_ENTRADA_ID = '1LX5DsKxWGolJ_sYpDH8euFUSAANdqMJN'
NOVA_DATA = datetime.datetime(2026, 9, 24, 0, 0)
DATA_STR = "24/09/2026"

def atualizar_planilhas():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)

    print(f"Buscando subpastas dentro de 'Segunda Entrada' (ID: {SEGUNDA_ENTRADA_ID})...\n")

    # List all subfolders inside Segunda Entrada
    res = drive_service.files().list(
        q=f"'{SEGUNDA_ENTRADA_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        fields="files(id, name)",
        pageSize=100,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    subfolders = res.get('files', [])

    print(f"Total de subpastas encontradas: {len(subfolders)}\n")
    processadas = 0

    for idx, sf in enumerate(subfolders, 1):
        sf_id = sf['id']
        sf_name = sf['name']
        print(f"[{idx}/{len(subfolders)}] 📁 Processando subpasta: '{sf_name}'")

        # Find spreadsheets in this subfolder
        f_res = drive_service.files().list(
            q=f"'{sf_id}' in parents and (mimeType = 'application/vnd.google-apps.spreadsheet' or mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') and trashed = false",
            fields="files(id, name, mimeType)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files = f_res.get('files', [])

        if not files:
            print("   ⚠️ Nenhuma planilha encontrada nesta subpasta.")
            continue

        for f in files:
            file_id = f['id']
            file_name = f['name']
            file_mime = f['mimeType']

            print(f"   📊 Planilha encontrada: '{file_name}' ({file_mime})")

            local_path = f"/tmp/mod_{file_id}.xlsx"
            try:
                # Download / Export
                if file_mime == 'application/vnd.google-apps.spreadsheet':
                    request = drive_service.files().export_media(
                        fileId=file_id,
                        mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                else:
                    request = drive_service.files().get_media(fileId=file_id)

                with open(local_path, 'wb') as fh:
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()

                # Load and update with openpyxl
                wb = openpyxl.load_workbook(local_path)
                
                # Identify target sheet (Página2, Página 2, ou a 2ª aba)
                target_sheet = None
                for sname in wb.sheetnames:
                    if 'página' in sname.lower() or 'pagina' in sname.lower() or '2' in sname:
                        target_sheet = sname
                        break
                if not target_sheet and len(wb.sheetnames) > 1:
                    target_sheet = wb.sheetnames[1]
                elif not target_sheet:
                    target_sheet = wb.sheetnames[0]

                ws = wb[target_sheet]
                val_antigo = ws['D2'].value
                
                # Update D2 cell
                ws['D2'] = NOVA_DATA
                ws['D2'].number_format = 'DD/MM/YYYY'
                
                # Hide sheet
                ws.sheet_state = 'hidden'

                wb.save(local_path)

                # Re-upload / Update file on Drive
                media = MediaFileUpload(
                    local_path,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    resumable=True
                )

                drive_service.files().update(
                    fileId=file_id,
                    media_body=media,
                    supportsAllDrives=True
                ).execute()

                print(f"      ✅ Sucesso! Aba '{target_sheet}' -> Célula D2 alterada de '{val_antigo}' para '24/09/2026' e aba ocultada.")
                processadas += 1

            except Exception as e:
                print(f"      ❌ Erro ao processar planilha '{file_name}': {e}")
            finally:
                if os.path.exists(local_path):
                    os.remove(local_path)

        print()

    print(f"\n🎉 Concluído! Total de planilhas alteradas: {processadas}")

if __name__ == '__main__':
    atualizar_planilhas()
