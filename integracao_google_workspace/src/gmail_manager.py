import os
import os.path
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Escopos do Gmail:
# - 'https://mail.google.com/': Acesso completo para ler, modificar e enviar e-mails
SCOPES = ['https://mail.google.com/']

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), 'credentials_gmail.json')
TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token_gmail.json')

def autenticar_gmail():
    """Autentica o usuário localmente via OAuth2 e gera/reutiliza token_gmail.json."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Atualizando token expirado...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(f"Arquivo de credenciais não encontrado em: {CREDENTIALS_PATH}")
                
            print("\n=======================================================")
            print("Iniciando fluxo de autorização do Gmail no navegador...")
            print("Por favor, selecione sua conta do Google e permita as permissões.")
            print("=======================================================\n")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
            
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
            print(f"Token salvo com sucesso em: {TOKEN_PATH}")
            
    return creds

def obter_servico_gmail():
    """Retorna o objeto do serviço da API do Gmail."""
    creds = autenticar_gmail()
    return build('gmail', 'v1', credentials=creds)

def listar_ultimos_emails(max_results=5, query=None):
    """Lista as mensagens mais recentes da caixa de entrada."""
    service = obter_servico_gmail()
    kwargs = {'userId': 'me', 'maxResults': max_results}
    if query:
        kwargs['q'] = query
        
    results = service.users().messages().list(**kwargs).execute()
    messages = results.get('messages', [])
    
    lista_emails = []
    if not messages:
        print("Nenhum e-mail encontrado.")
        return lista_emails

    print(f"\n--- {len(messages)} Últimos E-mails Encontrados ---")
    for msg in messages:
        detalhes = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = detalhes.get('payload', {}).get('headers', [])
        
        assunto = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(Sem assunto)')
        remetente = next((h['value'] for h in headers if h['name'].lower() == 'from'), '(Desconhecido)')
        data = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
        snippet = detalhes.get('snippet', '')
        
        info = {
            'id': msg['id'],
            'remetente': remetente,
            'assunto': assunto,
            'data': data,
            'resumo': snippet
        }
        lista_emails.append(info)
        print(f"ID: {msg['id']}")
        print(f"De: {remetente}")
        print(f"Assunto: {assunto}")
        print(f"Resumo: {snippet[:80]}...\n" + "-"*40)
        
    return lista_emails

def enviar_email(destinatario, assunto, corpo_texto):
    """Envia um e-mail simples de texto."""
    service = obter_servico_gmail()
    
    mensagem = MIMEMultipart()
    mensagem['to'] = destinatario
    mensagem['subject'] = assunto
    mensagem.attach(MIMEText(corpo_texto, 'plain'))
    
    raw_msg = base64.urlsafe_b64encode(mensagem.as_bytes()).decode('utf-8')
    corpo_envio = {'raw': raw_msg}
    
    msg_enviada = service.users().messages().send(userId='me', body=corpo_envio).execute()
    print(f"E-mail enviado com sucesso! ID da Mensagem: {msg_enviada['id']}")
    return msg_enviada

if __name__ == '__main__':
    print("Testando autenticação e listagem inicial do Gmail...")
    try:
        listar_ultimos_emails(max_results=5)
    except Exception as e:
        print(f"Erro ao acessar Gmail: {e}")
