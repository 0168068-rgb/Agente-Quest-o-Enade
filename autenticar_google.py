import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Escopo para acesso completo à agenda do Google Agenda
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_PATH = '/home/hamilcar/Downloads/credentials.json'
TOKEN_PATH = '/home/hamilcar/Downloads/token.json'

def autenticar():
    creds = None
    # O arquivo token.json armazena as credenciais de acesso do usuário de forma persistente.
    # Ele é criado automaticamente quando o fluxo de autorização é concluído pela primeira vez.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        
    # Se não houver credenciais válidas disponíveis, faz o login do usuário
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Token expirado. Atualizando credenciais...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                print(f"Erro: O arquivo {CREDENTIALS_PATH} não foi encontrado na pasta de Downloads.")
                print("Por favor, verifique se baixou o arquivo JSON do Google Cloud Console e renomeou correto.")
                return None
                
            print("Iniciando fluxo de login no navegador...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            
            # Executa o servidor local para receber o token.
            # O Python tentará abrir o seu navegador padrão automaticamente.
            # Se não abrir, você verá o link de autenticação impresso abaixo para copiar e colar.
            creds = flow.run_local_server(port=0, open_browser=True)
            
        # Salva o token para a próxima execução
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
            print(f"Token de acesso gerado e salvo com sucesso em: {TOKEN_PATH}")
            
    return creds

def testar_conexao(creds):
    if not creds:
        return
        
    print("\nTestando conexão com a API do Google Agenda...")
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Recupera as informações da agenda principal
        print("Buscando sua agenda principal...")
        calendar = service.calendars().get(calendarId='primary').execute()
        print(f" -> Conexão bem-sucedida! Agenda ativa: {calendar.get('summary')} ({calendar.get('id')})")
        
        # Lista as próximas 5 reuniões
        print("\nListando seus próximos 5 compromissos da agenda:")
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indica fuso UTC
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=5, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print(' -> Nenhum compromisso futuro encontrado.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f" • {start} - {event.get('summary')}")
            
    except Exception as e:
        print(f" -> Falha ao obter dados da agenda: {e}")

if __name__ == '__main__':
    creds = autenticar()
    testar_conexao(creds)
