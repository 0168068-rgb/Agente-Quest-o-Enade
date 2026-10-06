---
name: presentation-master
description: Guia e padrões para criação de apresentações executivas e técnicas de alto impacto (Slide Decks em HTML/CSS, Marp, Reveal.js ou Tailwind Slides).
---

# Presentation Master Skill

Esta skill define as melhores práticas para planejar, estruturar e gerar apresentações visuais (slide decks) modernas, legíveis e memoráveis em formato web (HTML/CSS interativo ou Markdown/Marp).

## 1. Regra de Ouro do Design de Slides

- **Uma Ideia por Slide**: Nunca sobrecarregue um slide com múltiplos temas. Se houver mais de 3 pontos principais, divida em múltiplos slides.
- **Ratio Aspectual 16:9**: Toda apresentação deve ser formatada para telas modernas panorâmicas (1920x1080px ou aspect-ratio 16/9).
- **Legibilidade Extrema**: Tamanho mínimo de fonte: 24pt/px para corpo, 44pt/px para títulos. Pouco texto, mais hierarquia.
- **Modos Escuro e Claro**: Escolha temas escuros elegantes (Cyber/Modern Dark) para apresentações em telas LED/telas de computador e temas claros limpos para projeções.

## 2. Estrutura Narrativa da Apresentação

1. **Slide de Capa (Title Slide)**: Título marcante, subtítulo, autor/data e plano de fundo dinâmico.
2. **Slide de Problema (Hook/Problem)**: O desafio ou dor atual destacado em poucas palavras.
3. **Slide de Solução (The Proposal)**: A resposta estratégica com 3 pilares visuais.
4. **Slide de Métricas / Resultados**: Números gigantes e gráficos de destaque.
5. **Slide de Demonstração / Arquitetura**: Diagrama explicativo, código limpo ou captura visual.
6. **Slide de Encerramento (Call to Action / Q&A)**: Resumo, próximos passos e contatos.

## 3. Implementação em HTML/CSS (Slide Deck Web)

Formato leve e executável diretamente em qualquer navegador com navegação por teclado (Setas Esquerda/Direita):

```html
<div class="deck">
  <section class="slide active">
    <div class="slide-content">
      <span class="category-tag">APRESENTAÇÃO EXECUTIVA</span>
      <h1>Revolucionando Interfaces com IA</h1>
      <p class="subtitle">Como construir experiências de usuário no estado da arte</p>
    </div>
  </section>

  <section class="slide">
    <div class="slide-content">
      <h2>O Problema Atual</h2>
      <div class="grid-2">
        <div class="card warning">
          <h3>Interfaces Genéricas</h3>
          <p>Falta de identidade visual e experiência monótona.</p>
        </div>
        <div class="card highlight">
          <h3>Nossa Solução</h3>
          <p>Sistemas de design dinâmicos com micro-interações.</p>
        </div>
      </div>
    </div>
  </section>
</div>
```

```css
.deck {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  position: relative;
  background: #0d1117;
  color: #f0f6fc;
  font-family: 'Inter', sans-serif;
}
.slide {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.4s ease, transform 0.4s ease;
  transform: scale(0.96);
  padding: 4rem;
}
.slide.active {
  opacity: 1;
  pointer-events: auto;
  transform: scale(1);
}
```
