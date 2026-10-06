---
name: vitest-jest-unit-testing
description: Criação de suítes de testes unitários e de integração de alta cobertura usando Vitest e Jest com mocks limpos e asserções claras.
---

# Vitest & Jest Unit Testing Skill

Esta skill define os padrões para escrita de testes unitários e de integração rápidos e isolados.

## 1. Estrutura AAA (Arrange, Act, Assert)

Cada teste deve ser legível por humanos e focar em apenas uma responsabilidade:

```ts
import { describe, it, expect, vi } from 'vitest'
import { calculateDiscount } from './pricing'

describe('calculateDiscount', () => {
  it('deve aplicar 10% de desconto para compras acima de $100', () => {
    // Arrange (Preparar)
    const amount = 150

    // Act (Executar)
    const result = calculateDiscount(amount)

    // Assert (Verificar)
    expect(result).toBe(135)
  })
})
```

## 2. Isolamento & Mocks Limpos

- Use `vi.fn()` ou `jest.fn()` para simular serviços externos (APIs, bancos de dados).
- Limpe o estado de cada mock entre os testes com `beforeEach(() => vi.clearAllMocks())`.
- Evite testar detalhes internos de implementação; teste os contratos de entrada e saída.
