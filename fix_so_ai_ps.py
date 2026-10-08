# -*- coding: utf-8 -*-
from generate_full_batch import create_exam

# AI para Sistemas Operacionais de Redes Abertas (UAs 2, 5)
create_exam(
    "Sistemas Operacionais de Redes Abertas", "Sistemas Operacionais de Redes Abertas", "AI Sistemas Operacionais de Redes Abertas", "2; 5",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Hierarquia de Diretórios Padrão Linux (FHS) e Montagem de Dispositivos",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Em um servidor Linux corporativo, a equipe de administração de infraestrutura adiciona um novo disco rígido SSD para armazenar logs de auditoria de rede.\n\nO analista precisa formatar a partição com o sistema de arquivos ext4 e associar o dispositivo de bloco a um ponto de montagem dentro da árvore unificada de diretórios (`/mnt` ou `/var/log`).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa que indica o utilitário do Linux utilizado para associar um sistema de arquivos de um dispositivo a um diretório da árvore FHS:",
            "opt_a": "mount", "opt_b": "chmod", "opt_c": "grep", "opt_d": "chown",
            "feedback": "A resposta certa é mount.\nComentário: O comando `mount` anexa o sistema de arquivos localizado em um dispositivo de bloco a um ponto de montagem no diretório FHS do Linux.\nFonte: Sistemas Operacionais de Redes Abertas, UA 2."
        },
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Permissões de Arquivos e Máscara Padrão umask",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Ao criar novos arquivos de texto em um diretório de trabalho no Linux, um usuário observa que as permissões padrão aplicadas automaticamente são `rw-r--r--` (644).\n\nEssa atribuição de permissões iniciais ocorre devido ao valor da máscara de criação de arquivos do usuário (**umask**), que subtrai privilégios das permissões padrão do sistema.",
            "afirmativas": "",
            "comando_text": "Assinale o valor octal da umask que resulta nas permissões padrão 644 para arquivos:",
            "opt_a": "022", "opt_b": "777", "opt_c": "000", "opt_d": "666",
            "feedback": "A resposta certa é 022.\nComentário: A umask 022 subtrai as permissões de gravação para o grupo e outros (666 - 022 = 644 para arquivos).\nFonte: Sistemas Operacionais de Redes Abertas, UA 2."
        },
        {
            "ua": "05", "obj": 1, "grau": "DIFÍCIL", "kw": "Sinais de Controle de Processos Linux (SIGTERM vs SIGKILL)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um serviço de banco de dados em Linux para de responder a novas consultas de rede. O administrador precisa encerrar o processo com segurança para evitar corrupção de tabelas antes de tentar uma terminação forçada.\n\nEle analisa a diferença entre o sinal de encerramento gracioso (**SIGTERM - 15**) e o sinal de terminação imediata e incondicional (**SIGKILL - 9**).",
            "afirmativas": "Com base nos sinais de interrupção de processos no Linux, analise as afirmativas:\nI. O sinal `SIGTERM` (15) solicita que o processo encerre suas atividades graciosamente, permitindo fechar arquivos e liberar memória.\nII. O sinal `SIGKILL` (9) é capturado pelo kernel e encerra o processo de forma imediata sem permitir que ele trate o sinal.\nIII. O sinal `SIGKILL` (9) pode ser bloqueado ou ignorado por qualquer aplicação em modo usuário.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II diferenciam corretamente o encerramento gracioso do SIGTERM e a interrupção direta pelo kernel do SIGKILL. A afirmativa III é falsa pois o SIGKILL não pode ser capturado nem ignorado.\nFonte: Sistemas Operacionais de Redes Abertas, UA 5."
        },
        {
            "ua": "05", "obj": 2, "grau": "DIFÍCIL", "kw": "Configuração de Rotas e Gateway Padrão em Linux via iproute2",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Em um roteador baseado em Linux Ubuntu Server, o administrador precisa adicionar uma rota estática para encaminhar o tráfego da subnet `192.168.10.0/24` através do gateway `10.0.0.1` usando a interface `eth1`.\n\nEle utiliza o utilitário moderno `ip route` da suíte **iproute2**.",
            "afirmativas": "Com base na manipulação de tabelas de roteamento em Linux, analise as afirmativas:\nI. O comando `ip route show` exibe a tabela de roteamento ativa no kernel do Linux.\nII. A adição de uma rota estática padrão é feita com a sintaxe `ip route add default via <gateway>`.\nIII. O utilitário `route` é o padrão moderno exclusivo recomendado para o kernel Linux 6.x em substituição ao `ip route`.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II apresentam com exatidão os comandos da suíte iproute2. A afirmativa III é falsa pois o utilitário `route` do pacote net-tools é obsoleto e foi substituído pelo `ip route`.\nFonte: Sistemas Operacionais de Redes Abertas, UA 5."
        },
        {
            "ua": "05", "obj": 3, "grau": "DIFÍCIL", "kw": "Serviços de Resolução de Nomes DNS (Bind9) em Servidores Linux",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Em uma infraestrutura de rede corporativa, o servidor Linux executa o serviço de nome de domínio **BIND9** (`named`) configurado como servidor DNS autoritativo para a zona interna `empresa.local`.\n\nO administrador configura os registros de tipo **A** (mapeamento nome-para-IP) e registros de tipo **PTR** (zona de busca reversa).",
            "afirmativas": "Com base em serviços DNS (BIND9) em Linux, analise as afirmativas:\n\nI. Os registros de tipo PTR na zona de busca reversa do BIND9 traduzem endereços IP para nomes de domínio totalmente qualificados (FQDN).\n\nPORQUE\n\nII. O arquivo `/etc/resolv.conf` especifica os endereços IP dos servidores DNS que o sistema operacional local consulta para resolver nomes de host.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A afirmativa I trata da resolução reversa PTR no BIND9 e a afirmativa II trata do arquivo cliente resolv.conf; são conceitos distintos do ecossistema DNS em Linux.\nFonte: Sistemas Operacionais de Redes Abertas, UA 5."
        }
    ],
    subfolder='AI'
)

# PS para Sistemas Operacionais de Redes Abertas (UAs 2, 5)
create_exam(
    "Sistemas Operacionais de Redes Abertas", "Sistemas Operacionais de Redes Abertas", "PS Sistemas Operacionais de Redes Abertas", "2; 5",
    [
        {
            "ua": "02", "obj": 1, "grau": "MÉDIA", "kw": "Gerenciamento de Links Simbólicos (ln -s) vs Hard Links",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "(Re)conhecimento",
            "context_text": "Para facilitar o acesso rápido a um script armazenado em `/var/scripts/backup.sh`, o administrador cria um atalho no diretório do usuário utilizando o comando `ln -s /var/scripts/backup.sh ~/atalho_backup.sh`.\n\nEle necessita compreender a diferença de comportamento entre um link simbólico (symlink) e um link rígido (hard link).",
            "afirmativas": "",
            "comando_text": "Assinale a alternativa correta sobre o comportamento do link simbólico (`ln -s`):",
            "opt_a": "O link simbólico é um arquivo apontador para o caminho do arquivo de origem; se o arquivo original for excluído, o symlink fica quebrado.", "opt_b": "O link simbólico duplica os dados físicos ocupando o dobro do espaço em disco.", "opt_c": "Links simbólicos funcionam apenas entre pastas do mesmo inode sem permissões.", "opt_d": "O link simbólico altera a senha de root do sistema.",
            "feedback": "A resposta certa é O link simbólico é um arquivo apontador para o caminho do arquivo de origem; se o arquivo original for excluído, o symlink fica quebrado.\nComentário: Um symlink contém apenas o caminho do arquivo alvo. Se o alvo for removido, o symlink torna-se órfão (dangling link).\nFonte: Sistemas Operacionais de Redes Abertas, UA 2."
        },
        {
            "ua": "02", "obj": 2, "grau": "MÉDIA", "kw": "Alteração de Propriedade de Arquivos e Diretórios (chown e chgrp)",
            "tipo_label": "Múltipla Escolha Simples", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Compreensão",
            "context_text": "Um desenvolvedor envia uma pasta com código fonte para o servidor Linux via FTP e os arquivos são salvos com o proprietário `root:root`.\n\nO administrador de sistemas precisa alterar a propriedade da pasta e de todo o seu conteúdo recursivamente para o usuário `webuser` e grupo `www-data`.",
            "afirmativas": "",
            "comando_text": "Assinale a opção que indica o comando correto para realizar essa alteração de propriedade de forma recursiva:",
            "opt_a": "chown -R webuser:www-data /pasta", "opt_b": "chmod -R 777 /pasta", "opt_c": "umask 022 /pasta", "opt_d": "ls -l /pasta",
            "feedback": "A resposta certa é chown -R webuser:www-data /pasta.\nComentário: O comando `chown` com a opção `-R` (recursivo) altera o usuário e o grupo proprietário de arquivos e subdiretórios.\nFonte: Sistemas Operacionais de Redes Abertas, UA 2."
        },
        {
            "ua": "05", "obj": 1, "grau": "DIFÍCIL", "kw": "Agendamento de Tarefas Periódicas no Linux com Cron (/etc/crontab)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Aplicação",
            "context_text": "Um administrador de sistemas configura o daemon **cron** para executar automaticamente um script de backup (`/usr/local/bin/backup.sh`) todas as noites às 02:00 da manhã de segunda a sexta-feira.\n\nEle edita o arquivo de tabela do cron (**crontab**) utilizando os 5 campos temporais padrão (Minuto, Hora, Dia do Mês, Mês, Dia da Semana).",
            "afirmativas": "Com base no agendamento de tarefas com Cron, analise as afirmativas:\nI. A sintaxe `0 2 * * 1-5 /usr/local/bin/backup.sh` agenda a execução para as 02:00 de segunda a sexta-feira.\nII. O arquivo `/var/log/syslog` ou `/var/log/cron` registra os logs de execução das tarefas disparadas pelo daemon cron.\nIII. O cron exige que a sessão do usuário permaneça logada com o terminal aberto para executar as tarefas agendadas.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II especificam corretamente a sintaxe cron (min hora dia mês diasemana) e o registro de logs. A afirmativa III é falsa pois o daemon `cron` roda em segundo plano (background) independentemente de sessões interativas.\nFonte: Sistemas Operacionais de Redes Abertas, UA 5."
        },
        {
            "ua": "05", "obj": 2, "grau": "DIFÍCIL", "kw": "Análise de Tráfego e Diagnóstico de Conexões em Linux (netstat, ss e tcpdump)",
            "tipo_label": "Sentenças Combinadas (Resposta Múltipla)", "tipo_excel": "Questão de Resposta múltiplas", "nivel_excel": "Análise",
            "context_text": "Para identificar quais portas de rede TCP/UDP estão escutando (listening) e quais processos associados estão rodando no servidor Linux, o analista de segurança executa ferramentas de estatística de soquetes.\n\nEle compara os utilitários `ss` (socket statistics), `netstat` e a ferramenta de captura de pacotes `tcpdump`.",
            "afirmativas": "Com base em diagnóstico de conexões de rede em Linux, analise as afirmativas:\nI. O comando `ss -tulpn` exibe as portas TCP/UDP em escuta e os respectivos nomes e PIDs dos processos associados.\nII. O utilitário `ss` é mais rápido e eficiente que o antigo `netstat` para inspecionar tabelas de soquetes volumosas no kernel.\nIII. O comando `tcpdump` é utilizado exclusivamente para formatar partições de disco ext4.",
            "comando_text": "É correto o que se afirma em:",
            "opt_a": "I e II, apenas.", "opt_b": "I e III, apenas.", "opt_c": "II e III, apenas.", "opt_d": "I, II e III.",
            "feedback": "A resposta certa é I e II, apenas.\nComentário: As afirmativas I e II descrevem com exatidão as opções e a superioridade do utilitário `ss`. A afirmativa III é absurda pois o `tcpdump` é um sniffer/analisador de pacotes de rede.\nFonte: Sistemas Operacionais de Redes Abertas, UA 5."
        },
        {
            "ua": "05", "obj": 3, "grau": "DIFÍCIL", "kw": "Acesso Remoto Seguro SSH (OpenSSH) com Criptografia de Chaves Pública/Privada",
            "tipo_label": "Asserção-Razão", "tipo_excel": "Questão de Asserção e Razão", "nivel_excel": "Julgamento",
            "context_text": "Para elevar o nível de segurança do acesso remoto administrativo a servidores Linux, a política corporativa desabilita a autenticação por senha no `/etc/ssh/sshd_config` (`PasswordAuthentication no`).\n\nTodos os administradores devem autenticar-se utilizando pares de chaves criptográficas assimétricas (chaves pública e privada) geradas via `ssh-keygen`.",
            "afirmativas": "Com base na autenticação por chaves no OpenSSH em Linux, analise as afirmativas:\n\nI. A chave pública do administrador é copiada para o arquivo `~/.ssh/authorized_keys` no servidor remoto, enquanto a chave privada permanece protegida no computador local do administrador.\n\nPORQUE\n\nII. O protocolo SSH utiliza criptografia assimétrica no aperto de mão (handshake) para autenticar a identidade do usuário sem transmitir senhas ou chaves privadas pela rede.",
            "comando_text": "A respeito dessas afirmativas, assinale a opção correta:",
            "opt_a": "As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.",
            "opt_b": "As afirmativas I e II são verdadeiras, mas a II não é uma justificativa correta da I.",
            "opt_c": "A afirmativa I é verdadeira, e a II é falsa.",
            "opt_d": "As afirmativas I e II são falsas.",
            "feedback": "A resposta certa é As afirmativas I e II são verdadeiras, e a II é uma justificativa correta da I.\nComentário: Ambas as afirmativas são verdadeiras. A chave pública armazenada em `authorized_keys` permite a validação da assinatura enviada pela chave privada local durante o handshake assimétrico do SSH.\nFonte: Sistemas Operacionais de Redes Abertas, UA 5."
        }
    ],
    subfolder='PS'
)

print("Provas AI e PS de Sistemas Operacionais de Redes Abertas criadas com sucesso!")
