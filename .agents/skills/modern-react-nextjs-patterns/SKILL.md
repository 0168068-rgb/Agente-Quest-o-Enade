---
name: modern-react-nextjs-patterns
description: Padrões e boas práticas para React 19, Next.js (App Router), Server Components, Client Components, Server Actions e gerenciamento de estado.
---

# Modern React & Next.js Patterns Skill

Esta skill estabelece os padrões para desenvolvimento em React 19 e Next.js com App Router.

## 1. Servidor vs Cliente (RSC & Client Components)

- **Default Server-First**: Trate todos os componentes como React Server Components (RSC) por padrão.
- **`'use client'` Restrito**: Adicione a diretiva `'use client'` apenas em componentes de folha (leaf components) que precisam de interatividade (`useState`, `useEffect`, `onClick`).
- **Passagem de Dados**: Passe dados do servidor para o cliente através de props serializáveis. Evite instanciar estados complexos no cliente se a busca puder ser feita no servidor.

## 2. Server Actions & Mutations

- Utilize **Server Actions** (`'use server'`) para mutações de dados com tratamento de formulários (`useActionState`, `useOptimistic`).
- Validação estrita de entrada de dados no lado do servidor com bibliotecas como **Zod**.

```tsx
// app/actions/user.ts
'use server'
import { z } from 'zod'

const schema = z.object({ email: z.string().email() })

export async function updateUser(formData: FormData) {
  const parsed = schema.safeParse({ email: formData.get('email') })
  if (!parsed.success) return { error: 'Email inválido' }
  // Mutação no banco de dados...
}
```

## 3. Otimização de Performance

- **Streaming & Suspense**: Use `<Suspense fallback={<Skeleton />}>` para carregar seções assíncronas da página em paralelo.
- **Cache & Revalidation**: Utilize `revalidatePath()` e `revalidateTag()` estrategicamente para atualizar o cache do Next.js sem recarregar a página inteira.
