---
name: infographic-creator
description: Framework e padrões para criação de infográficos visuais rica e interativamente estruturados usando HTML, SVG, CSS e bibliotecas de Data Viz (Chart.js, D3, Mermaid).
---

# Infographic Creator Skill

Esta skill orienta a criação de infográficos de alto valor visual, educativos e de fácil leitura, combinando SVG vetorial, componentes HTML5, animações CSS e representações de dados.

## 1. Estrutura Narrativa e Hierarquia Visual

Infográficos eficientes seguem a regra dos 3 níveis:
- **Nível 1 (Must See - Gancho)**: Título marcante, métrica principal gigantesca (Big Stat) ou ilustração central SVG.
- **Nível 2 (Should See - Blocos de Conteúdo)**: Linha do tempo, fluxo de processo, comparação em colunas ou gráficos interativos.
- **Nível 3 (Can See - Detalhes)**: Notas de rodapé, fontes, dados explicativos e legendas.

## 2. Tipos de Layouts de Infográfico

1. **Linha do Tempo (Timeline Flow)**: Marcos conectados por linhas SVG com pontos de brilho (glow points) e cartões alternados.
2. **Comparativo (Versus Grid)**: Duas colunas contrastantes destacando prós/contras ou dados A vs B.
3. **Dashboard de Estatísticas (Metrics Board)**: Cartões de KPI com ícones dinâmicos, barras de progresso animadas e mini-gráficos.
4. **Fluxograma / Processo (Step-by-Step)**: Sequência numerada com setas direcionais SVG e destaques visuais por etapa.

## 3. Uso Eficiente de SVG e Animações CSS

- Use SVG embutido (`<svg viewBox="0 0 800 600">`) para garantir responsividade perfeita.
- Animações CSS com `@keyframes` para entrada dos dados e efeito de preenchimento de barras (`stroke-dashoffset` ou `width` transition).
- Efeitos interativos ao passar o mouse (`:hover`) em regiões do infográfico para exibir tooltips com informações extras.

## 4. Padrões de Código para Infográficos HTML/SVG

```html
<div class="infographic-container">
  <header class="info-header">
    <span class="badge">INFOGRÁFICO INTERATIVO</span>
    <h1>Título Principal do Infográfico</h1>
    <p class="subtitle">Subtítulo explicativo com o contexto dos dados</p>
  </header>

  <section class="stats-grid">
    <div class="stat-card">
      <div class="stat-number" data-value="85">85%</div>
      <div class="stat-label">Crescimento de Eficiência</div>
      <div class="progress-bar"><div class="fill" style="width: 85%"></div></div>
    </div>
  </section>
</div>
```

```css
.stat-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 24px;
  transition: transform 0.3s ease, border-color 0.3s ease;
}
.stat-card:hover {
  transform: translateY(-5px);
  border-color: #6366f1;
  box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
}
```
