---
name: postgres-optimization-indexing
description: Guias e técnicas para otimização de consultas PostgreSQL, estratégias de indexação (B-tree, GIN, GiST), conexões e EXPLAIN ANALYZE.
---

# PostgreSQL Optimization & Indexing Skill

Esta skill define os métodos para otimização de performance e indexação em bancos de dados PostgreSQL.

## 1. Estratégias de Indexação

- **B-Tree (Padrão)**: Para comparações diretas e ordenação (`=`, `>`, `<`, `BETWEEN`, `ORDER BY`).
- **GIN (Generalized Inverted Index)**: Ideal para busca textual (`tsvector`), JSONB (`jsonb_ops` / `jsonb_path_ops`) e colunas de arrays.
- **Índices Compostos (Multi-Column)**: Coloque colunas usadas em cláusulas `=` primeiro, seguidas de colunas usadas em intervalo (`>`) ou `ORDER BY`.

```sql
-- Exemplo de índice GIN para buscas em JSONB
CREATE INDEX idx_users_metadata_gin ON users USING GIN (metadata);

-- Exemplo de índice composto otimizado
CREATE INDEX idx_orders_user_status ON orders (user_id, status, created_at DESC);
```

## 2. Análise de Execução de Queries

- Execute sempre `EXPLAIN (ANALYZE, BUFFERS)` para identificar **Seq Scan** desnecessários em tabelas grandes ou operações pesadas de ordenação na memória (`Sort Method: external merge Disk`).
- **N+1 Queries**: Identifique e elimine requisições repetitivas no ORM utilizando junções (`JOIN`, `include` ou `select_related`).
