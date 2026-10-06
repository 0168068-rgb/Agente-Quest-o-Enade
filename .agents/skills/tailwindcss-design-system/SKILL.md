---
name: tailwindcss-design-system
description: Padrões de arquitetura para Design Systems baseados em Tailwind CSS (Design Tokens, temas escuro/claro, plugins e componentes responsivos).
---

# Tailwind CSS Design System Skill

Esta skill orienta a construção de interfaces escaláveis usando Tailwind CSS v3 e v4 com boas práticas de componentes.

## 1. Organização de Tokens de Design

- Configure cores semânticas no `tailwind.config.js` ou `@theme` (Tailwind v4) em vez de utilitários arbitrários:
  - `bg-primary`, `bg-surface`, `text-main`, `text-muted`, `border-subtle`, `accent-brand`.
- Suporte a Dark Mode com a classe `dark:` ou variáveis CSS mapeadas.

## 2. Padrões de Reutilização de Componentes

- Evite repetição massiva de classes brutas em múltiplos elementos; utilize abstrações com `clsx` / `tailwind-merge` (`cn` helper):

```ts
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

## 3. Componentes Consistentes com CVA (Class Variance Authority)

```tsx
import { cva } from 'class-variance-authority'

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-lg font-medium transition-colors focus-visible:outline-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-md',
        outline: 'border border-slate-700 bg-transparent hover:bg-slate-800 text-slate-200',
        ghost: 'hover:bg-slate-800 text-slate-300',
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  }
)
```
