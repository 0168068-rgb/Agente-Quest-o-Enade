---
name: security-code-review
description: Checklist e auditoria automatizada para identificar vulnerabilidades OWASP Top 10, sanitização de dados, SQLi, XSS e validação de chaves.
---

# Security Code Review Skill

Esta skill fornece um guia de auditoria de código focado na prevenção e detecção de vulnerabilidades críticas de segurança.

## 1. Prevenção OWASP Top 10

1. **Injection (SQLi, Command Injection)**:
   - NUNCA concatene dados de usuário diretamente em queries SQL ou chamadas de sistema.
   - Use Prepared Statements / ORMs (Prisma, Drizzle, SQLAlchemy) ou consultas parametrizadas.
2. **Cross-Site Scripting (XSS)**:
   - Escape todo conteúdo inserido dinamicamente no DOM.
   - Evite `dangerouslySetInnerHTML` ou `innerHTML` sem sanitização com **DOMPurify**.
3. **Gestão de Segredos & API Keys**:
   - NUNCA grave API Keys, tokens JWT ou senhas diretamente no código (hardcoded).
   - Utilize variáveis de ambiente (`process.env`) e adicione `.env*` ao `.gitignore`.

## 2. Checklist de Revisão Rápida de Código

```markdown
- [ ] Todas as entradas de usuário são validadas com schemas (ex.: Zod, Yup, Joi)?
- [ ] Os endpoints possuem verificação de permissão/autorização (RBAC)?
- [ ] Chaves privadas ou tokens estão ausentes do histórico de commits?
- [ ] Os pacotes e dependências foram verificados com `npm audit` ou `bun audit`?
```
