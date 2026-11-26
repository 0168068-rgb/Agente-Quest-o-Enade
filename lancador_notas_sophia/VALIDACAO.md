# Validação realizada em Linux

Data: 13/10/2026. Python 3.12; dependências diretas correspondentes às versões fixadas em `requirements.txt`.

## Testes automatizados

Comando: `python3 -m unittest discover -s tests -v`.

30 cenários cobrem leitura de CSV/Excel, arquivos inválidos, zeros à esquerda, notas zero/vazias/inválidas, precisão decimal, seleção de cursos, polos deslocados, geração das três abas, exclusão de disciplinas por polo, correspondências exatas e duplicatas, período indisponível, cancelamento antes/depois do preenchimento e da gravação, falha de inventário, campo de avaliação ausente e falha de preenchimento do lote.

Os testes com Chromium usam uma página HTML local e interceptam todas as requisições HTTP. Exercitam o botão Gravar, a releitura da nota, a restauração do período ao passar de Itaperuna para Nova Iguaçu e a preservação da coluna AI ao preencher AD. Também verificam que a simulação não aciona Gravar. Um teste adicional aguarda um postback WebForms atrasado.

A janela foi aberta no Linux e seu visual aprovado pelo usuário. Os testes da interface verificam seleção de colunas, simulação como padrão, comunicação com a tarefa em segundo plano e confirmação antes do modo real.

## Conferência da planilha fornecida

Leitura sem alterar o CSV original: 8.323 registros totais; Fisioterapia tem 289 registros, dos quais 280 têm nota válida. As unidades identificadas são Itaperuna e Nova Iguaçu. A planilha e seus dados pessoais **não estão incluídos neste pacote**.

## O que ainda exige Windows

O instalador não foi compilado ou executado neste ambiente Linux. Estão incluídos o script PowerShell, a configuração Inno Setup e as instruções para geração no computador Windows do usuário. Ainda é necessário validar instalação, execução do Chromium empacotado, teste em simulação no SophiA e preservação dos relatórios após desinstalar.

Nenhuma gravação real no SophiA foi realizada. Os scripts original e de diagnóstico foram preservados. O código do aplicativo é independente deles.

Correção adicional: a lista de cursos é preenchida mesmo enquanto os controles estão bloqueados durante a leitura. Teste de regressão incluído; a suíte completa passou com 30 testes.

## Orientação por etapas e janelas menores

A interface agora tem instruções em cada grupo e orientação no topo atualizada por foco/clique, ao carregar a planilha e ao iniciar/concluir o processamento. Os botões ficam fixos e o formulário rola. Foram executados os 7 testes da interface, incluindo as 3 novas verificações de orientação por etapa, bloqueio durante execução e acesso em janela de 860 × 650; todos passaram. A alteração não executou a automação no SophiA.

## Correção da exportação CSV e dos cantos arredondados

A exportação fornecida contém vírgulas sem aspas na disciplina QSMS e em notas decimais. A leitura foi corrigida por âncoras estruturais, recuperando nome, RA, disciplina, nota e polo, sem alterar o arquivo de origem. Foram conferidas as seis linhas afetadas da aba de pendências; o relatório antigo foi preservado e a geração de um novo relatório exige refazer a simulação. A leitura continua com 8.323 registros totais e 289 de Fisioterapia, dos quais 280 têm nota.

Os grupos, entradas, seletores, lista de cursos e área de mensagens passaram a usar superfícies arredondadas, mantendo os botões com sombra. Um teste adicional verifica que o desenho das bordas cobre a área inteira dos grupos e dos campos, sem encobrir os títulos. A janela corrigida foi inspecionada visualmente no Linux.

Após as correções, a suíte completa passou: 38 testes. Nenhum deles acessa o SophiA real.

## Marketing — 20/10/2026

O relatório analisado tinha 0 resultados e 77 pendências: 48 notas acima do limite fixo de 10, 13 polos com travessão não reconhecido, 12 notas tratadas como vazias e 4 duplicatas. A planilha contém valores de 0 a 100 e erros de fórmula #VALUE!. Conforme orientação do usuário, os valores devem ser mantidos exatamente, sem divisão.

Foi adicionada a faixa configurável 0–10/0–100, com sugestão na interface e confirmação da faixa no modo real. A releitura após gravação usa a mesma faixa; o Excel preserva notas de até 100 como números. Nomes de polo com travessão são reconhecidos e erros de fórmula XLSX permanecem explícitos. Duplicatas continuam pendentes, sem escolha automática de uma nota. A planilha e o relatório de origem foram preservados.

A suíte completa passou: 47 testes, incluindo 100 e 90 preservados em simulação e após gravação no portal fictício, sem conversão. Nenhuma nota foi gravada no SophiA real nesta verificação. A nova simulação no portal ainda requer login e início pelo usuário.

## Janelas HTML do SophiA e colunas — 20/10/2026

A análise de duas execuções reais do usuário identificou uma seleção incorreta de Nota (contendo nomes de polo) na primeira e oito tentativas de gravação não confirmadas na segunda, seguidas por bloqueio da interface por uma cortinaDialogo. Não se presume que zero resultados confirmados signifique zero gravações.

A seleção de colunas foi protegida, a roda do mouse deixa de alterar seletores e o mapeamento passa a constar no log. As janelas HTML são registradas e aguardadas para leitura/resposta manual, com imagem na pasta de relatórios quando possível. O timeout interrompe a execução sem repetir o lote incerto; o cancelamento mantém as pendências. Apenas a releitura confirma os valores.

Os testes cobrem diálogo HTML fechado pelo usuário, imagem de diagnóstico, timeout, cancelamento, preservação da incerteza e bloqueio de coluna de polo como Nota. Suíte completa: 54 testes aprovados. Nenhuma gravação adicional foi feita no SophiA real durante esta correção. As oito tentativas do usuário ainda precisam de conferência no portal.
