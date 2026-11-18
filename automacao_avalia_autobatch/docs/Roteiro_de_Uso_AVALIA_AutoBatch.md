# 📘 Roteiro Oficial de Uso — AVALIA AutoBatch Desktop v5.1
**Automação de Cadastro de Questões em Lote no AVALIA (Grupo A)**  
**Criado por:** *Hamilcar Silva*  

---

## 🎯 Objetivos do Aplicativo
O **AVALIA AutoBatch Desktop** foi projetado com base em metas de **Usabilidade e Interação Humano-Computador (IHC)** para automatizar a inserção repetitiva de questões acadêmicas no sistema AVALIA do Grupo A, garantindo:
- 🚀 **Agilidade**: Cadastro automático de 10 a 50+ questões por disciplina em poucos minutos.
- 🎯 **Precisão**: Preenchimento exato de enunciado, alternativas, gabarito e feedbacks pedagógicos.
- 📄 **Rastreabilidade**: Captura automática dos códigos de ID gerados pelo AVALIA e exportação instantânea de relatórios em **Microsoft Word (`.docx`)** e **Markdown (`.md`)**.

---

## 📋 Passo a Passo de Utilização

### 1️⃣ Passo 1 — Preparar a Planilha Excel (`.xlsx`)
1. Abra o aplicativo **AVALIA AutoBatch Desktop**.
2. No **Passo 2** da tela principal, clique no botão **`📥 Baixar Modelo de Planilha Exemplo (.xlsx)`**.
3. Escolha onde salvar o arquivo modelo no seu computador.
4. Abra o modelo baixado no Excel e preencha as colunas conforme a estrutura exigida:
   - `Identificação da questão`: Código/Nome único da questão (ex: `UA-01_QUESTÃO-1_OBJ-1_FÁCIL`).
   - `Palavra chave`: Termo ou tema da questão.
   - `Tipo da Questão`: `questão de complementação Simples`, `resposta Múltipla` ou `Asserção e Razão`.
   - `Nível cognitivo`: `Reconhecimento`, `Compreensão` ou `Aplicação`.
   - `Texto da Questão`: O enunciado pedagógico completo.
   - `Alternativa A`, `Alternativa B`, `Alternativa C`, `Alternativa D` (e `Alternativa E` se houver).
   - `Feedback da questão`: Explicação do gabarito indicando claramente a alternativa correta (ex: *"A resposta certa é a alternativa A. Justificativa..."*).

---

### 2️⃣ Passo 2 — Abrir o Navegador Chrome AVALIA
1. No **Passo 1** do aplicativo, clique no botão **`🌐 Abrir Chrome AVALIA (Porta 9222)`**.
2. Uma janela dedicada do Google Chrome será aberta automaticamente.
3. **Faça o login** com suas credenciais no AVALIA.

---

### 3️⃣ Passo 3 — Navegar no Chrome até a Etapa 4 da Disciplina
1. No Chrome que foi aberto, selecione a disciplina desejada.
2. Avance na tela do AVALIA até chegar na **Etapa 4 — Inserção de Questão** (onde aparece o formulário com os campos de Nome, Enunciado e Alternativas).
3. Volte ao aplicativo **AVALIA AutoBatch** e marque a caixa de seleção:
   - **`☑️ Confirmo que já naveguei até o Passo 4 (Inserção de Questão) no Chrome`**.
   - O indicador superior mudará para **`🟢 PRONTO NA ETAPA 4`**.

---

### 4️⃣ Passo 4 — Carregar a Planilha e Iniciar a Automação
1. No **Passo 2** do aplicativo, clique em **`📂 Escolher Excel...`** e selecione o arquivo `.xlsx` preenchido.
2. O aplicativo fará uma validação prévia exibindo o total de questões detectadas.
3. No **Passo 3**, clique no botão principal:
   - **`🚀 INICIAR INSERÇÃO EM LOTE`**.
4. Acompanhe em tempo real:
   - A **Barra de Progresso** avançando.
   - Os logs detalhados na caixa preta do console com o aviso de submissão e o **Código ID do AVALIA** de cada questão.

---

### 5️⃣ Passo 5 — Finalização e Troca Sequencial de Disciplina
1. Quando todas as questões forem lançadas, uma mensagem de sucesso surgirá na tela.
2. O aplicativo perguntará:
   - *"Deseja carregar a planilha Excel de outra disciplina agora?"*
3. **Se clicar em SIM**:
   - A janela para selecionar a nova planilha se abrirá automaticamente.
   - No Chrome, navegue até a **Etapa 4** da nova disciplina.
   - Marque novamente o checkbox de confirmação e clique em **`🚀 INICIAR INSERÇÃO EM LOTE`**.

---

### 6️⃣ Passo 6 — Relatórios Gerados
Ao término de cada disciplina, o programa salva automaticamente na pasta do aplicativo:
- 📄 **`Relatorio_Oficial_AVALIA_<Nome_da_Disciplina>.docx`** *(Relatório formatado no Microsoft Word)*
- 📄 **`Relatorio_Oficial_AVALIA_<Nome_da_Disciplina>.md`** *(Relatório em Markdown)*

**Conteúdo da Tabela de Relatório:**
- Número da Questão (`#`)
- Identificador Original
- **Código / ID Oficial atribuído pelo AVALIA**
- Resposta Correta (Gabarito)
- Tipo de Questão

---

## 💡 Recomendações e Boas Práticas
- **Não feche a janela do Chrome** enquanto o robô estiver preenchendo as questões.
- Se o servidor do AVALIA oscilar, o robô tentará re-enviar automaticamente.
- Para interromper a execução a qualquer momento, clique no botão **`⏹️ PAUSAR/PARAR`**.
