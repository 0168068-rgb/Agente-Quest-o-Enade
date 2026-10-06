---
name: supabase-prisma-migrations
description: Padrões para migrações de banco de dados seguras e idempotentes com Supabase e Prisma ORM sem downtime ou perda de dados.
---

# Supabase & Prisma Migrations Skill

Esta skill fornece diretrizes para gerenciamento de schemas e migrações em Supabase e Prisma.

## 1. Fluxo de Migração Seguro (Zero Downtime)

- **Mudança de Schema Não Destrutiva**: Em produção, altere schemas em duas etapas:
  1. Adicione a nova coluna/tabela (marcada como opcional/nullable).
  2. Migre os dados da aplicação e depois torne a coluna obrigatória (`NOT NULL`) se necessário.
- Evite comandos destrutivos como `DROP COLUMN` ou `DROP TABLE` em uma única migração direta.

## 2. Padrões com Prisma & Supabase CLI

```bash
# Para gerar migrações locais no Prisma
npx prisma migrate dev --name add_user_role

# Para aplicar migrações em produção no Supabase sem redefinir o banco
npx prisma migrate deploy

# Para sincronizar alterações RLS (Row Level Security) no Supabase
supabase db diff -f add_rls_policies
```

## 3. Segurança no Nível de Linha (RLS - Row Level Security)

Sempre garanta que novas tabelas no Supabase possuam RLS ativo por padrão:

```sql
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuários podem ler apenas seus próprios dados"
ON public.user_profiles FOR SELECT
USING (auth.uid() = user_id);
```
