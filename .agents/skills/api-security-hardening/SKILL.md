---
name: api-security-hardening
description: Diretrizes de segurança para APIs REST/GraphQL (Autenticação JWT/OAuth2, Rate Limiting, CORS, Headers de segurança e sanitização).
---

# API Security Hardening Skill

Esta skill orienta a proteção de APIs RESTful e servidores backend contra ataques e uso indevido.

## 1. Proteção em Camadas

- **Rate Limiting**: Configure limites de requisição por IP ou Token (ex.: `express-rate-limit`, `upstash/ratelimit`) para prevenir ataques de força bruta e DoS.
- **CORS Estrito**: Defina origens permitidas explicitamente (`origin: ['https://meudominio.com']`) e proíba `origin: '*'`.
- **Headers de Segurança (Helmet)**:
  - `Content-Security-Policy (CSP)`
  - `Strict-Transport-Security (HSTS)`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`

## 2. Autenticação e Sessão Segura

- **Tokens JWT**: Assine tokens com chaves secretas fortes (mínimo 256 bits). Defina prazos curtos de expiração para `access_token` (ex.: 15m) e use `refresh_token` armazenado em cookie `HttpOnly`, `Secure` e `SameSite=Strict`.

```ts
res.cookie('refreshToken', token, {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'strict',
  maxAge: 7 * 24 * 60 * 60 * 1000,
})
```
