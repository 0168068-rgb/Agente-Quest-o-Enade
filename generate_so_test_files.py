# -*- coding: utf-8 -*-
"""
Script de geração de 5 questões ENADE para a disciplina Sistemas Operacionais de Redes Abertas (UAs 2, 5, 7, 13).
Gera dois entregáveis:
1. Arquivo Word (.docx): Questoes_ENADE_Sistemas_Operacionais.docx (Versão limpa do Estudante)
2. Arquivo Excel (.xlsx): AI Sistemas Operacionais de Redes Abertas.xlsx (10 Colunas padronizadas no modelo)
"""
import os, sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

sys.path.append('/home/hamilcar/Antigravity/agente_gerador_questoes_enade/src')
from docx_exporter import ENADEDocxExporter

# ---------------------------------------------------------
# 1. CONTEÚDO DO DOCUMENTO WORD (ESTUDANTE)
# ---------------------------------------------------------
md_estudante = r"""# BANCO DE QUESTÕES ENADE — SISTEMAS OPERACIONAIS DE REDES ABERTAS
## CADERNO DE QUESTÕES (VERSÃO DO ESTUDANTE)

---

## QUESTÃO 1 (UA 02 — Arquitetura de sistema e recursos do Linux)
**Tipo Estrutural:** Múltipla Escolha Simples

### Contexto Realista
No sistema operacional Linux, a arquitetura é dividida fundamentalmente em dois modos de execução: o Espaço do Usuário (*User Space*), onde rodam as aplicações e utilitários cotidianos, e o Espaço do Kernel (*Kernel Space*), reservado ao núcleo monolítico modular. Para que uma aplicação de usuário consiga acessar o hardware, como gravar dados em um disco rígido ou enviar um pacote de rede através de uma interface eth0, a aplicação deve acionar uma interface padronizada do sistema.

### Comando da Questão
Considerando a arquitetura do sistema operacional Linux, o mecanismo que permite a uma aplicação em *User Space* solicitar serviços protegidos ao *Kernel Space* é denominado

A) a chamada de sistema (*system call*), que alterna o modo de execução do processador de usuário para núcleo.  
B) a recompilação em tempo real do código-fonte da aplicação diretamente na memória BIOS.  
C) a execução em modo de emulação por interpretação de scripts em linguagem Java.  
D) o desativamento temporário das travas de segurança do gerenciador de memória do sistema.

---

## QUESTÃO 2 (UA 05 — Shell do Linux)
**Tipo Estrutural:** Múltipla Escolha Simples

### Contexto Realista
Durante a auditoria de um servidor de rede Linux, um administrador precisa analisar os logs de erros de autenticação contidos no arquivo `/var/log/auth.log`. Ele deseja filtrar apenas as linhas que contêm a palavra "Failed", ordenar o resultado em ordem alfabética e salvar a saída final em um novo arquivo denominado `erros_autenticacao.txt`, sem sobrescrever outros dados existentes se o arquivo já existir.

### Comando da Questão
Diante da necessidade apresentada e considerando os operadores de redirecionamento e *pipes* do Shell do Linux, o comando que atende de forma exata e eficiente a essa solicitação é

A) `grep 'Failed' /var/log/auth.log | sort >> erros_autenticacao.txt`  
B) `grep 'Failed' /var/log/auth.log > sort > erros_autenticacao.txt`  
C) `cat /var/log/auth.log < grep 'Failed' < erros_autenticacao.txt`  
D) `sort /var/log/auth.log 2> grep 'Failed' >> erros_autenticacao.txt`

---

## QUESTÃO 3 (UA 07 — Gerenciamento de arquivos e diretórios no Linux)
**Tipo Estrutural:** Sentenças Combinadas (Resposta Múltipla)

### Contexto Realista
Em um servidor web Linux rodando a distribuição Ubuntu Server, o administrador de sistemas precisa configurar um diretório compartilhado `/var/www/projeto` para a equipe de desenvolvimento. Para garantir a segurança dos arquivos da aplicação, o diretório deve permitir leitura, escrita e execução para o dono do diretório (usuário `webmaster`), leitura e execução para o grupo do projeto (`devs`), e nenhum acesso para outros usuários do sistema. Além disso, o administrador precisa atualizar a lista de repositórios e instalar o serviço de hospedagem web Apache2 através do gerenciador de pacotes da distribuição.

### Afirmativas para Análise
Com base nos conhecimentos sobre gerenciamento de arquivos, permissões POSIX e gerenciador de pacotes APT no Linux, analise as afirmativas:

I. O comando `chmod 750 /var/www/projeto` configura exatamente as permissões necessárias de leitura, escrita e execução para o dono (7), leitura e execução para o grupo (5) e nenhum acesso para outros (0).  
II. O comando `chown webmaster:devs /var/www/projeto` altera o proprietário do diretório para o usuário `webmaster` e o grupo associado para `devs`.  
III. A sequência de comandos `apt update` seguido de `apt install apache2` atualiza o índice local de pacotes dos repositórios e instala o servidor web Apache2 no sistema.

### Comando da Questão
É correto o que se afirma em:

A) I e II, apenas.  
B) I, II e III.  
C) II e III, apenas.  
D) I e III, apenas.

---

## QUESTÃO 4 (UA 13 — Configuração dos serviços NAT, DHCP e DNS em Linux)
**Tipo Estrutural:** Sentenças Combinadas (Resposta Múltipla)

### Contexto Realista
Uma pequena empresa contratou um analista de redes para configurar um roteador/gateway Linux que conectará a rede local corporativa (192.168.1.0/24) à internet através de uma interface de rede WAN (`eth0`). Na interface interna (`eth1`), o gateway deve distribuir IPs automaticamente para os computadores da rede local via serviço DHCP, fornecendo também o endereço do gateway padrão e os servidores DNS. Na interface externa (`eth0`), o gateway deve mascarar o tráfego da rede interna usando NAT.

### Afirmativas para Análise
Com base nos procedimentos de configuração dos serviços NAT e DHCP no Linux, analise as afirmativas:

I. Para ativar o mascaramento NAT na interface externa `eth0` via IPTables, o analista deve executar o comando `iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE` e habilitar o encaminhamento de pacotes no kernel em `/proc/sys/net/ipv4/ip_forward`.  
II. No arquivo de configuração do servidor DHCP (`/etc/dhcp/dhcpd.conf`), o parâmetro `option routers 192.168.1.1;` especifica o endereço IP do gateway padrão que será entregue aos clientes da rede local.  
III. O serviço DHCP exige que o cabo de rede esteja obrigatoriamente desconectado da placa de rede durante a atribuição estática do endereço MAC dos clientes.

### Comando da Questão
É correto o que se afirma em:

A) I e II, apenas.  
B) I e III, apenas.  
C) II e III, apenas.  
D) I, II e III.

---

## QUESTÃO 5 (UA 13 + UA 07 — Configuração do Serviço DNS BIND9)
**Tipo Estrutural:** Asserção-Razão

### Contexto Realista
Na infraestrutura de TI de uma instituição de ensino, o servidor DNS principal roda o serviço BIND9 (`named`) em Linux para resolver os nomes do domínio `empresa.com.br` e realizar a resolução reversa dos endereços IP da rede. Durante a manutenção do arquivo de zona direta `/etc/bind/db.empresa.com.br`, o administrador adicionou novos registros de recursos dos tipos A, CNAME e PTR, salvando o arquivo e reiniciando o daemon `named`.

### Texto Base e Estrutura Asserção-Razão
Com base nos conceitos de configuração de servidores DNS BIND9 no Linux, analise as afirmativas:

**I. O registro de recurso do tipo PTR (*Pointer Record*) deve ser configurado no arquivo de zona de resolução reversa para mapear um endereço IP em um nome de domínio FQDN, enquanto os registros do tipo A mapeiam nomes de domínio em endereços IPv4.**

**PORQUE**

**II. O servidor BIND9 utiliza o arquivo de zona de resolução reversa (ex: `db.192.168.1`) para responder a consultas de clientes que possuem um endereço IP e desejam descobrir o nome de domínio correspondente associado a esse IP.**

### Comando da Questão
A respeito dessas afirmativas, assinale a opção correta:

A) As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.  
B) As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.  
C) A afirmativa I é verdadeira, e a II é falsa.  
D) As afirmativas I e II são falsas.
"""

# Exportar Arquivo Word (.docx)
output_docx = "/home/hamilcar/Antigravity/AI Sistemas Operacionais de Redes Abertas.docx"
exporter = ENADEDocxExporter()
exporter.markdown_to_docx(md_estudante, output_docx, title="Caderno de Questões ENADE - Sistemas Operacionais de Redes Abertas")
print(f"[DOCX EXPORTER] Concluído: {output_docx}")

# ---------------------------------------------------------
# 2. CONTEÚDO DO DOCUMENTO EXCEL (.XLSX)
# ---------------------------------------------------------
excel_rows = [
    # Header
    ["Identificação da questão", "Palavra chave", "Tipo da questão", "Nível cognitivo", "Texto da Questão", "Alternativa A", "Alternativa B", "Alternativa C", "Alternativa D", "Feedback da questão"],
    
    # Row 1 (Questão 1)
    [
        "UA-02_QUESTÃO-1_OBJ-1_MÉDIA",
        "Arquitetura do Linux e Kernel Space",
        "Questão de Resposta múltiplas",
        "(Re)conhecimento",
        "Disciplina: Sistemas Operacionais de Redes Abertas\n\nNo sistema operacional Linux, a arquitetura é dividida fundamentalmente em dois modos de execução: o Espaço do Usuário (User Space), onde rodam as aplicações e utilitários cotidianos, e o Espaço do Kernel (Kernel Space), reservado ao núcleo monolítico modular. Para que uma aplicação de usuário consiga acessar o hardware, como gravar dados em um disco rígido ou enviar um pacote de rede através de uma interface eth0, a aplicação deve acionar uma interface padronizada do sistema.\n\nPergunta: Considerando a arquitetura do sistema operacional Linux, o mecanismo que permite a uma aplicação em User Space solicitar serviços protegidos ao Kernel Space é denominado [lacuna]",
        "a chamada de sistema (system call), que alterna o modo de execução do processador de usuário para núcleo.",
        "a recompilação em tempo real do código-fonte da aplicação diretamente na memória BIOS.",
        "a execução em modo de emulação por interpretação de scripts em linguagem Java.",
        "o desativamento temporário das travas de segurança do gerenciador de memória do sistema.",
        "A resposta certa é a chamada de sistema (system call), que alterna o modo de execução do processador de usuário para núcleo.\nComentário: O primeiro objetivo da UA 2 (Definir como é a arquitetura do sistema operacional Linux) explica a divisão entre User Space e Kernel Space. Para acessar recursos de hardware protegidos, os programas de usuário acionam chamadas de sistema (system calls), alternando o nível de privilégio da CPU.\nFonte: Arquitetura de sistema e recursos do Linux, UA 2."
    ],

    # Row 2 (Questão 2)
    [
        "UA-05_QUESTÃO-2_OBJ-3_MÉDIA",
        "Redirecionamento de Saída e Pipes no Shell",
        "Questão de Resposta múltiplas",
        "Compreensão",
        "Disciplina: Sistemas Operacionais de Redes Abertas\n\nDurante a auditoria de um servidor de rede Linux, um administrador precisa analisar os logs de erros de autenticação contidos no arquivo /var/log/auth.log. Ele deseja filtrar apenas as linhas que contêm a palavra 'Failed', ordenar o resultado em ordem alfabética e salvar a saída final em um novo arquivo denominado erros_autenticacao.txt, sem sobrescrever outros dados existentes se o arquivo já existir.\n\nPergunta: Diante da necessidade apresentada e considerando os operadores de redirecionamento e pipes do Shell do Linux, o comando que atende de forma exata e eficiente a essa solicitação é [lacuna]",
        "grep 'Failed' /var/log/auth.log | sort >> erros_autenticacao.txt",
        "grep 'Failed' /var/log/auth.log > sort > erros_autenticacao.txt",
        "cat /var/log/auth.log < grep 'Failed' < erros_autenticacao.txt",
        "sort /var/log/auth.log 2> grep 'Failed' >> erros_autenticacao.txt",
        "A resposta certa é grep 'Failed' /var/log/auth.log | sort >> erros_autenticacao.txt\nComentário: O terceiro objetivo da UA 5 (Explicar o redirecionamento de saídas no Linux) trata dos operadores de tubo (pipe |) e redirecionamento. O tubo (|) conecta a saída do grep como entrada do sort, e o operador '>>' anexa o resultado ao arquivo final sem sobrescrever dados pré-existentes.\nFonte: Shell do Linux, UA 5."
    ],

    # Row 3 (Questão 3)
    [
        "UA-07_QUESTÃO-3_OBJ-2_DIFÍCIL",
        "Permissões POSIX e Gerenciador de Pacotes",
        "Questão de Resposta múltiplas",
        "Aplicação",
        "Disciplina: Sistemas Operacionais de Redes Abertas\n\nTexto-base: Em um servidor web Linux rodando a distribuição Ubuntu Server, o administrador de sistemas precisa configurar um diretório compartilhado /var/www/projeto para a equipe de desenvolvimento. Para garantir a segurança dos arquivos da aplicação, o diretório deve permitir leitura, escrita e execução para o dono do diretório (usuário 'webmaster'), leitura e execução para o grupo do projeto ('devs'), e nenhum acesso para outros usuários do sistema. Além disso, o administrador precisa atualizar a lista de repositórios e instalar o serviço de hospedagem web Apache2 através do gerenciador de pacotes da distribuição.\n\nCom base nos conhecimentos sobre gerenciamento de arquivos, permissões POSIX e gerenciador de pacotes APT no Linux, analise as afirmativas:\nI. O comando 'chmod 750 /var/www/projeto' configura exatamente as permissões necessárias de leitura, escrita e execução para o dono (7), leitura e execução para o grupo (5) e nenhum acesso para outros (0).\nII. O comando 'chown webmaster:devs /var/www/projeto' altera o proprietário do diretório para o usuário 'webmaster' e o grupo associado para 'devs'.\nIII. A sequência de comandos 'apt update' seguido de 'apt install apache2' atualiza o índice local de pacotes dos repositórios e instala o servidor web Apache2 no sistema.\n\nPergunta: É correto o que se afirma em:",
        "I e II, apenas.",
        "I, II e III.",
        "II e III, apenas.",
        "I e III, apenas.",
        "A resposta certa é I, II e III.\nComentário: As três afirmativas são verdadeiras. A afirmativa I aplica a notação octal 750 (u=rwx, g=rx, o=---). A afirmativa II utiliza o comando chown para alterar usuário e grupo. A afirmativa III utiliza os comandos corretos do APT para atualizar os repositórios e instalar o serviço Apache2.\nFonte: Gerenciamento de arquivos e diretórios no sistema operacional Linux, UA 7."
    ],

    # Row 4 (Questão 4)
    [
        "UA-13_QUESTÃO-4_OBJ-1_DIFÍCIL",
        "Configuração dos Serviços NAT e DHCP",
        "Questão de Resposta múltiplas",
        "Análise",
        "Disciplina: Sistemas Operacionais de Redes Abertas\n\nTexto-base: Uma pequena empresa contratou um analista de redes para configurar um roteador/gateway Linux que conectará a rede local corporativa (192.168.1.0/24) à internet através de uma interface de rede WAN (eth0). Na interface interna (eth1), o gateway deve distribuir IPs automaticamente para os computadores da rede local via serviço DHCP, fornecendo também o endereço do gateway padrão e os servidores DNS. Na interface externa (eth0), o gateway deve mascarar o tráfego da rede interna usando NAT.\n\nCom base nos procedimentos de configuração dos serviços NAT e DHCP no Linux, analise as afirmativas:\nI. Para ativar o mascaramento NAT na interface externa eth0 via IPTables, o analista deve executar o comando 'iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE' e habilitar o encaminhamento de pacotes no kernel em '/proc/sys/net/ipv4/ip_forward'.\nII. No arquivo de configuração do servidor DHCP (/etc/dhcp/dhcpd.conf), o parâmetro 'option routers 192.168.1.1;' especifica o endereço IP do gateway padrão que será entregue aos clientes da rede local.\nIII. O serviço DHCP exige que o cabo de rede esteja obrigatoriamente desconectado da placa de rede durante a atribuição estática do endereço MAC dos clientes.\n\nPergunta: É correto o que se afirma em:",
        "I e II, apenas.",
        "I e III, apenas.",
        "II e III, apenas.",
        "I, II e III.",
        "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II são verdadeiras. A afirmativa I detalha a regra de mascaramento NAT via IPTables e a ativação do ip_forward no kernel. A afirmativa II especifica corretamente o parâmetro 'option routers' no dhcpd.conf. A afirmativa III é falsa pois a comunicação DHCP utiliza quadros de broadcast na camada de enlace (ETH) com o cabo fisicamente conectado.\nFonte: Configuração dos serviços NAT, DHCP e DNS em Linux, UA 13."
    ],

    # Row 5 (Questão 5)
    [
        "UA-13_QUESTÃO-5_OBJ-3_DIFÍCIL",
        "Serviço DNS BIND9 e Arquivos de Zona",
        "Questão de Asserção e Razão",
        "Julgamento",
        "Disciplina: Sistemas Operacionais de Redes Abertas\n\nTexto-base: Na infraestrutura de TI de uma instituição de ensino, o servidor DNS principal roda o serviço BIND9 (named) em Linux para resolver os nomes do domínio 'empresa.com.br' e realizar a resolução reversa dos endereços IP da rede. Durante a manutenção do arquivo de zona direta /etc/bind/db.empresa.com.br, o administrador adicionou novos registros de recursos dos tipos A, CNAME e PTR, salvando o arquivo e reiniciando o daemon named.\n\nCom base nos conceitos de configuração de servidores DNS BIND9 no Linux, analise as afirmativas:\nI. O registro de recurso do tipo PTR (Pointer Record) deve ser configurado no arquivo de zona de resolução reversa para mapear um endereço IP em um nome de domínio FQDN, enquanto os registros do tipo A mapeiam nomes de domínio em endereços IPv4.\nPORQUE\nII. O servidor BIND9 utiliza o arquivo de zona de resolução reversa (ex: db.192.168.1) para responder a consultas de clientes que possuem um endereço IP e desejam descobrir o nome de domínio correspondente associado a esse IP.\n\nPergunta: A respeito dessas afirmativas, assinale a opção correta:",
        "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
        "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
        "A afirmativa I é verdadeira, e a II é falsa.",
        "As afirmativas I e II são falsas.",
        "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A afirmativa I diferencia os registros PTR (IP -> Nome) dos registros A (Nome -> IP). A afirmativa II explica a função exata da zona reversa, justificando por que o registro PTR é indispensável nesse arquivo para resolver consultas IP -> FQDN.\nFonte: Configuração dos serviços NAT, DHCP e DNS em Linux, UA 13."
    ]
]

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Questões ENADE"

header_fill = PatternFill(start_color="003366", end_color="003366", fill_type="solid")
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
cell_font = Font(name="Calibri", size=10)
wrap_alignment = Alignment(wrap_text=True, vertical="top")
thin_border = Border(
    left=Side(style='thin', color='D3D3D3'),
    right=Side(style='thin', color='D3D3D3'),
    top=Side(style='thin', color='D3D3D3'),
    bottom=Side(style='thin', color='D3D3D3')
)

for row_idx, row_data in enumerate(excel_rows, 1):
    for col_idx, val in enumerate(row_data, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=val)
        cell.border = thin_border
        if row_idx == 1:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        else:
            cell.font = cell_font
            cell.alignment = wrap_alignment

# Ajustar larguras das colunas
col_widths = [28, 30, 28, 20, 65, 40, 40, 40, 40, 65]
for idx, width in enumerate(col_widths, 1):
    col_letter = openpyxl.utils.get_column_letter(idx)
    ws.column_dimensions[col_letter].width = width

output_xlsx = "/home/hamilcar/Antigravity/AI Sistemas Operacionais de Redes Abertas.xlsx"
wb.save(output_xlsx)
print(f"[EXCEL EXPORTER] Concluído: {output_xlsx}")
