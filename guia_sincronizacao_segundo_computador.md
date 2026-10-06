# Guia Mestre de Sincronização do Antigravity (Segundo Computador)

> [!IMPORTANT]
> **Instruções de Configuração e Sincronização Bidirecional**  
> Este guia contém o passo a passo completo para configurar o Antigravity no segundo computador com todas as habilidades, memórias, regras de formatação e automações ativadas no Computador A.

---

## 📌 Informações do Repositório
- **URL do GitHub**: `https://github.com/0168068-rgb/Agente-Quest-o-Enade.git`
- **Diretório Padrão no Computador**: `/home/hamilcar/Antigravity`
- **Pasta Sincronizada no OneDrive**: `$HOME/onedrive- Hamilcar/Antigravity_Global_Config/`

---

## 🚀 PASSO A PASSO PARA CONFIGURAÇÃO NO SEGUNDO COMPUTADOR

Execute os 4 passos abaixo no **terminal do segundo computador** (apenas uma vez) para ativar a sincronização total:

### PASSO 1: Baixar ou Atualizar o Repositório do Projeto
No terminal do segundo computador:

* **Se a pasta do projeto ainda NÃO existe**:
  ```bash
  cd ~ && git clone https://github.com/0168068-rgb/Agente-Quest-o-Enade.git Antigravity
  ```

* **Se a pasta do projeto JÁ existe**:
  ```bash
  cd ~/Antigravity && git pull origin main
  ```

---

### PASSO 2: Vincular Habilidades, Regras e Plugins Globais via OneDrive
Este comando conecta as pastas do Antigravity da outra máquina ao seu OneDrive sincronizado (garantindo que qualquer nova habilidade criada em qualquer um dos computadores fique disponível em tempo real):

```bash
rm -rf ~/.gemini/config/skills ~/.gemini/config/rules ~/.gemini/config/plugins && \
ln -s "$HOME/onedrive- Hamilcar/Antigravity_Global_Config/skills" ~/.gemini/config/skills && \
ln -s "$HOME/onedrive- Hamilcar/Antigravity_Global_Config/rules" ~/.gemini/config/rules && \
ln -s "$HOME/onedrive- Hamilcar/Antigravity_Global_Config/plugins" ~/.gemini/config/plugins
```

---

### PASSO 3: Ativar a Atualização Automática no Terminal (`~/.bashrc`)
Execute este comando para adicionar o auto-pull em segundo plano e o atalho `sync-antigravity`:

```bash
echo -e '\n# Antigravity Auto Sync\nantigravity_auto_pull() { if [ -d "$HOME/Antigravity/.git" ]; then (cd "$HOME/Antigravity" && git pull --quiet origin main 2>/dev/null &); fi; }\nantigravity_auto_pull\nalias sync-antigravity='\''cd "$HOME/Antigravity" && git add . && git commit -m "auto-sync: $(date)" && git push origin main && echo "Sincronizado com o GitHub com sucesso!"'\''' >> ~/.bashrc
```

Em seguida, recarregue o terminal:
```bash
source ~/.bashrc
```

---

### PASSO 4: Salvar as Credenciais do Git (Evitar Pedir Senha)
Para não precisar digitar o token do GitHub toda vez:

```bash
git config --global credential.helper store
```
*(Na primeira vez que você rodar um `git push` ou `sync-antigravity`, digite o usuário `0168068-rgb` e seu Token do GitHub `ghp_...`. O sistema salvará e não pedirá novamente).*

---

## 🛠️ REGRAS E FUNCIONALIDADES ATIVADAS

Uma vez executados os passos acima, o Antigravity do segundo computador terá ativas as seguintes regras e capacidades:

### 1. Skill de Sincronização Automática (`sincronizar-agente`)
A qualquer momento, em qualquer um dos computadores, você pode dizer ao Antigravity:
👉 **"sincronizar agente"**, **"salvar e enviar"** ou **"sync"**
O agente executará sozinho o `pull` e `push` de todas as novidades!

### 2. Regra Mandatória de Diálogo ENADE (`.agents/rules/enade_generation_workflow.md`)
O Antigravity **NUNCA** gerará questões ou documentos ENADE automaticamente. É obrigatório apresentar os Objetivos de Aprendizagem extraídos e consultar o usuário sobre:
1. Quais Objetivos de Aprendizagem priorizar.
2. Quantidade de questões desejada.
3. Tipos/modelos estruturais de preferência (Múltipla Escolha Direta, Escolha Combinada, Asserção-Razão ou Discursiva).

### 3. Padrão de Formatação para Microsoft Word (`.agents/rules/word_formatting_standards.md`)
Toda exportação Word (`.docx`) seguirá rigorosamente:
- **Itálico em parênteses**: termos como `(*duct plug*)` ou `(*manholes*)` são renderizados como `(`*duct plug*`)` sem asteriscos aparentes.
- **Fórmulas e Matemática em Unicode**: `n₁`, `n₂`, `θ₁`, `θ₂`, `θ_c`, `I²R`, `λ`, `µm`, `m²`, `·`, `sin`, `arcsin` sem códigos LaTeX crus ou barras.
- **Diagramas ASCII**: Fonte Consolas 8.5pt com espaçamento simples, mantendo alinhamento de desenhos.
- **Tabelas**: Tabela nativa do Word com cabeçalho azul escuro (`#003366`) e linhas zebradas.
