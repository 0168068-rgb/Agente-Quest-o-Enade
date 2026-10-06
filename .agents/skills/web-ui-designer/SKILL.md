---
name: web-ui-designer
description: Diretrizes e padrões avançados para criação de interfaces de sites modernas, atraentes e responsivas (UI/UX, Design Tokens, Glassmorphism, Micro-animações, Tailwind/CSS).
---

# Web UI/UX Designer Skill

Esta skill fornece diretrizes e padrões para criar interfaces de usuário (UI) impressionantes, modernas, responsivas e de alto impacto visual.

## 1. Princípios de Design Visual (Visual WOW)

- **Cores & Paletas Harmoniosas**: Evite cores genéricas (vermelho/azul/verde puros). Use paletas selecionadas em HSL/RGB com tons primários, secundários, neutros profundos e acentos vibrantes.
- **Tipografia Moderna**: Importe fontes do Google Fonts (ex.: Inter, Plus Jakarta Sans, Outfit, Sora, Fira Code). Defina hierarquia clara (Display, Heading 1-4, Body, Small).
- **Efeitos Visuais**:
  - **Glassmorphism**: `background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.1);`
  - **Gradientes Suaves**: Textos e bordas com gradientes e `background-clip: text;`
  - **Sombras de Camada (Layered Shadows)**: Sombras multinível para profundidade real.
- **Micro-Interações**: Efeitos `:hover`, `:focus-visible` e transições suaves (`transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1)`).

## 2. Arquitetura de Design System (CSS Variables)

Sempre estabeleça os **Design Tokens** no início da folha de estilos:

```css
:root {
  /* Colors */
  --bg-primary: #0b0f19;
  --bg-secondary: #111827;
  --bg-card: rgba(31, 41, 55, 0.6);
  --accent-primary: #6366f1;
  --accent-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  --text-main: #f9fafb;
  --text-muted: #9ca3af;
  --border-color: rgba(255, 255, 255, 0.08);

  /* Spacing & Radii */
  --radius-sm: 8px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --shadow-glow: 0 0 25px rgba(99, 102, 241, 0.25);
}
```

## 3. Componentes Indispensáveis

1. **Hero Section Impactante**: Título chamativo com palavra-chave em gradiente, subtítulo legível, botões CTA primário/secundário e elemento visual de fundo (glow/mesh grid).
2. **Cards com Hover Elevation**: Transformação Y leve (`transform: translateY(-4px)`) com brilho na borda.
3. **Navegação Fixa com Blur**: Header com `position: sticky; backdrop-filter: blur(12px)`.
4. **Rodapé e CTAs Organizados**: Seções responsivas em Grid/Flexbox.

## 4. Responsividade e Acessibilidade (A11y)

- Grid flexível (`grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))`).
- Contraste de cor adequado (WCAG AA).
- Rótulos `aria-label` e estados `:focus-visible` bem destacados.
