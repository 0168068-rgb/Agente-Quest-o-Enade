import os
import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Escopos para o Google Agenda
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials_gmail.json')
TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token_calendar.json')

def autenticar_agenda():
    """Autentica o usuário para o Google Agenda via OAuth2."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {CREDENTIALS_PATH}")
                
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
            
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
            
    return creds

def listar_proximos_eventos(max_results=10):
    """Lista os próximos compromissos da agenda principal do usuário."""
    creds = autenticar_agenda()
    service = build('calendar', 'v3', credentials=creds)
    
    agora = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indica UTC
    events_result = service.events().list(
        calendarId='primary',
        timeMin=agora,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    return events, events_result.get('summary', 'Agenda Principal')

if __name__ == '__main__':
    try:
        eventos, nome_agenda = listar_proximos_eventos()
        print(f"Agenda: {nome_agenda}")
        print(f"Total de compromissos futuros encontrados: {len(eventos)}")
        for i, ev in enumerate(eventos, 1):
            inicio = ev['start'].get('dateTime', ev['start'].get('date'))
            print(f"{i}. {inicio} - {ev.get('summary', '(Sem título)')}")
    except Exception as e:
        print(f"Erro ao acessar agenda: {e}")
