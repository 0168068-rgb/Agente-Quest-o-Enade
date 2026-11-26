# Lançador de Notas SophiA — 1.0.0

Aplicativo em português para Windows 10/11 de 64 bits. A janela também pode ser executada em Linux. O portal configurado é `https://portal.sophia.com.br/SophiA_111/Acesso.aspx?escola=8262`.

## Gerar o instalador no seu Windows

1. Extraia todo o ZIP para uma pasta, por exemplo `C:\Sophia`.
2. Instale **Python 3.12 de 64 bits** com o Python Launcher (`py`), pela [página oficial](https://www.python.org/downloads/windows/).
3. Instale **Inno Setup 6** pela [página oficial](https://jrsoftware.org/isdl.php). Esses programas são necessários somente no computador que gera o instalador.
4. Abra o PowerShell na pasta extraída e execute:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\gerar_instalador.ps1
```

O script cria um ambiente Python separado, instala as dependências, baixa Chromium, executa os testes locais e gera o aplicativo e o instalador. Essa etapa exige internet. A política `Bypass` vale apenas para esse processo, sem alterar a configuração permanente do PowerShell.

Se Inno Setup estiver em outra pasta:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\gerar_instalador.ps1 -InnoCompiler "C:\MinhaPasta\ISCC.exe"
```

O instalador final será `dist\instalador\LancadorNotasSophia-Setup-1.0.0.exe`. Use esse arquivo para instalar em outros computadores. Ele instala por usuário, sem exigir administrador, inclui Python e Chromium e não exige Python instalado no computador de destino.

As dependências diretas têm versões fixadas; as versões completas resolvidas no Windows serão registradas em `dist\dependencias-windows.txt`.

## Usar a janela

A faixa no topo orienta a etapa atual. Clique em um campo ou entre nele com Tab para ver o que fazer; ao carregar a planilha, a orientação passa para a conferência das colunas. Cada grupo também contém uma instrução curta. O formulário tem rolagem, e Iniciar, Cancelar e Abrir relatório continuam visíveis em janelas menores.

1. Clique em **Escolher arquivo** e selecione CSV, XLSX ou XLS.
2. Confira as colunas de nome, curso, disciplina, nota, matrícula e polo. As colunas são detectadas, mas podem ser corrigidas nos seletores.
3. Selecione um ou mais cursos. Cada clique marca ou desmarca um curso.
4. Escolha AD, AI, PS ou AE, informe o período (por exemplo `2026.2`) e confira a **Faixa de notas: 0 a 10 ou 0 a 100**. O programa sugere a faixa pela coluna selecionada; você pode alterá-la. Os valores não são divididos nem convertidos: 100 continua 100 e 10 continua 10.
5. Mantenha **Simulação** para testar sem gravar. O modo real exige confirmação antes de iniciar.
6. Escolha a pasta dos relatórios e clique em **Iniciar**.
7. Faça login manualmente no navegador aberto. O aplicativo não lê nem armazena sua senha.
8. Acompanhe as mensagens. **Cancelar** interrompe antes do próximo passo seguro; uma gravação já iniciada será verificada antes da interrupção. As gravações anteriores não são desfeitas.
9. Clique em **Abrir relatório** ao terminar. Os arquivos recebem data e hora e não sobrescrevem os anteriores.

Os seletores não mudam com a roda do mouse: ela rola o formulário. A seleção de uma mesma coluna para campos diferentes, ou de uma coluna de polo como Nota, bloqueia o início e solicita correção na etapa 2. As colunas efetivamente usadas aparecem no acompanhamento.

### Janela do portal depois de Gravar

Se o SophiA apresentar uma janela HTML que bloqueia a tela, o aplicativo registra o texto e, quando possível, salva uma imagem `janela_sophia_*.png` na pasta dos relatórios. Ele aguarda até cinco minutos para você ler e responder/fechar a janela no próprio navegador, sem clicar automaticamente em confirmações desconhecidas. Em seguida, relê os valores para conferir a gravação. Fechar a janela não significa, por si só, que houve gravação.

Se a janela permanecer aberta ou você cancelar, o aplicativo gera relatório parcial e mantém os valores como gravação não confirmada. Uma operação não confirmada deve ser conferida no SophiA antes de repetir o lançamento real. O número de Resultados representa valores confirmados, não apenas tentativas de clicar em Gravar.

## Relatório Excel

O relatório contém exatamente três abas:

- **Resultados:** preenchimentos em simulação ou valores de gravações conferidos após recarregar os filtros e buscar novamente.
- **Planilha - Pendentes:** nota ausente/inválida, aluno não localizado, correspondência ambígua, campo bloqueado, gravação não confirmada e registros não processados por erro ou cancelamento.
- **Web - Sem Planilha:** alunos das turmas/disciplinas consultadas sem correspondência na fonte.

Registros de disciplinas não disponibilizadas pelo portal **no respectivo polo e curso** são omitidos quando o inventário termina com sucesso. Em inventário incompleto, não se presume que uma disciplina esteja ausente: os registros ficam pendentes no relatório parcial.

Matrículas são comparadas exatamente, preservando zeros à esquerda. Somente na ausência de matrícula usa-se o nome completo normalizado exato; nomes semelhantes, parciais ou ambíguos não autorizam preenchimento. Duplicatas da planilha ficam pendentes. Notas devem ser números dentro da faixa escolhida (0 a 10 ou 0 a 100), com ponto ou vírgula decimal; zero é nota válida e casas decimais são preservadas. A faixa define somente a validação: não existe conversão de escala. Células XLSX com erro, como `#VALUE!`, permanecem identificadas como erro no relatório e não são tratadas como notas vazias. Prefixos Polo/Campus/Unidade e hífens/travessões no nome do polo são normalizados.

Na exportação CSV observada do SophiA, vírgulas sem aspas dentro da disciplina, do nome e da nota decimal deslocam campos. Quando o arquivo tem o cabeçalho completo dessa exportação, a leitura realinha os campos usando posições identificadas de matrícula/CPF, período/modalidade e faltoso/chamada. O acompanhamento informa quantas linhas foram realinhadas. Uma linha ambígua interrompe a leitura em vez de presumir um nome ou uma nota; nesse caso, use XLSX ou CSV corretamente delimitado. O arquivo de origem não é alterado. Confira a coluna de nota escolhida: valores não numéricos ficam pendentes.

O aplicativo não substitui um período indisponível por outro. Ele não preenche uma avaliação diferente se a célula correta não puder ser identificada. Gravações sem releitura confirmada não são repetidas automaticamente. Uma nota já existente pode ser substituída pelo valor da planilha quando o modo real é confirmado.

## Testar sem acessar o SophiA

No ambiente Python com as dependências instaladas:

```powershell
python -m unittest discover -s tests -v
```

Os testes usam dados fictícios e uma página local interceptada pelo Playwright. Nenhuma requisição ao SophiA ou gravação real é realizada. Eles verificam também o caminho do botão Gravar em um portal simulado.

## Executar os fontes no Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
.venv/bin/python main.py
```

Tkinter é incluído no Python oficial para Windows. No Linux, pode ser necessário instalar o pacote `python3-tk` da distribuição. Abrir `main.py` apenas mostra a interface; a automação só começa ao clicar em Iniciar.

## Validação no Windows

O pacote foi desenvolvido e testado em Linux. A geração e a validação do `.exe`/instalador precisam ser feitas no Windows: PyInstaller não gera diretamente um executável Windows a partir de Linux. Depois de gerar:

- Instale em uma conta sem Python e verifique a abertura da janela e do navegador incluído.
- Execute primeiro em **simulação**, incluindo mais de um polo, e confira os resultados e pendências.
- Confira pastas com espaços/acentos, cancelamento durante o login e geração de relatório parcial.
- Desinstale e confirme que os relatórios continuam na pasta escolhida.

O modo real foi exercitado apenas no portal de teste. Nenhuma gravação real no SophiA foi executada durante o desenvolvimento.

## Organização e referências

`sophia/gui.py`: janela e fila de eventos; `data.py`: leitura e validação; `portal.py`: interação com o navegador; `engine.py`: execução e reconciliação; `report.py`: Excel. Os scripts original e de diagnóstico existentes não foram modificados.

Empacotamento baseado na [documentação do Playwright](https://playwright.dev/python/docs/library#pyinstaller), do [PyInstaller](https://pyinstaller.org/en/stable/usage.html) e na [instalação sem administrador do Inno Setup](https://jrsoftware.org/ishelp/topic_setup_privilegesrequired.htm).
