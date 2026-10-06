---
name: playwright-e2e-testing
description: Automação robusta de testes End-to-End (E2E), web scraping avançado, seletores resilientes e relatórios com Playwright.
---

# Playwright E2E Testing & Automation Skill

Esta skill orienta a criação de suítes de testes End-to-End resilientes e automação web com Playwright.

## 1. Seletores Resilientes (User-Facing Locators)

- Evite CSS selectors frágeis (`div > ul > li:nth-child(3)`).
- Priorize seletores orientados ao usuário (`getByRole`, `getByText`, `getByLabel`, `getByTestId`):

```ts
// Bom exemplo
await page.getByRole('button', { name: 'Salvar' }).click()
await expect(page.getByText('Alterações salvas')).toBeVisible()

// Evite
await page.click('.btn-primary-2')
```

## 2. Padrão Page Object Model (POM)

Mantenha a lógica de seleção e ação encapsulada em classes de modelo de página para facilitar manutenção:

```ts
export class LoginPage {
  constructor(private page: Page) {}

  async login(email: string, pass: string) {
    await this.page.getByLabel('E-mail').fill(email)
    await this.page.getByLabel('Senha').fill(pass)
    await this.page.getByRole('button', { name: 'Entrar' }).click()
  }
}
```

## 3. Esperas Automáticas & Assertions

- Use retentativas implícitas (`webFirst assertions` como `expect(locator).toBeVisible()`) em vez de esperas fixas (`page.waitForTimeout(5000)`).
