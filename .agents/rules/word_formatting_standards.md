# Regra de Exportação e Formatação de Documentos Word (.docx)

> [!IMPORTANT]
> **DIRETRIZES MANDATÓRIAS DE FORMATAÇÃO E CONVERSÃO DE TEXTO/DOCX**

Em toda exportação de questões, relatórios ou documentos para o Microsoft Word (`.docx`), o agente e o módulo `docx_exporter.py` devem obrigatoriamente seguir os seguintes padrões de formatação:

---

### 1. Interpretador Inline Markdown (Remoção de Caracteres Brutos)
- **Itálico (`*texto*`)**: Converter para a fonte estilo **Itálico nativo do Word**, garantindo a remoção total dos asteriscos `*` no documento impresso (ex: `(*duct plug*)` deve ser renderizado como `(`*duct plug*`)`).
- **Negrito (`**texto**`)**: Converter para a fonte estilo **Negrito nativo do Word** sem asteriscos `**`.
- **Negrito + Itálico (`***texto***`)**: Converter para **Negrito + Itálico nativos**.
- **Código Inline (`` `texto` ``)**: Converter para fonte **Consolas 9.5pt**.

---

### 2. Diagramas ASCII e Blocos de Código
- Blocos de diagrama/código (entre ```` ``` ````) devem ser formatados obrigatoriamente com:
  - Fonte: **Consolas 8.5pt**.
  - Espaçamento de linha: **Simples (`1.0`)**.
  - Espaçamento antes/depois: **0 pt**.
  - Preservação integral dos espaços originais e caracteres ASCII (`|`, `/`, `\`, `-`, `=`) para não desalinhar desenhos e esquemas físicos.

---

### 3. Fórmulas e Notações Matemáticas
- **Proibição de LaTeX Cru no Word**: Nunca deixar comandos LaTeX crus com barras de escapamento (ex: `$\theta_c$`, `$n_1$`, `$I^2R$`), pois causam desformatados de tabulação `\t` ou cifrões visíveis.
- **Conversão Mandatória para Símbolos Unicode**:
  - `$n_1$` $\rightarrow$ `n₁`
  - `$n_2$` $\rightarrow$ `n₂`
  - `$\theta_c$` $\rightarrow$ `θ_c`
  - `$I^2R$` $\rightarrow$ `I²R`
  - `$\lambda$` $\rightarrow$ `λ`
  - `$\mu\text{m}$` $\rightarrow$ `µm`
  - `$m^2$` $\rightarrow$ `m²`

---

### 4. Tabelas Nativas do Word
- Tabelas Markdown devem ser convertidas em tabelas nativas do Word (`add_table`) com:
  - Cabeçalho: Fundo azul escuro (`#003366`) e texto em branco em negrito.
  - Linhas alternadas: Sombreado suave (`#F2F4F7`).
