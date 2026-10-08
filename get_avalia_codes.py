from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = [pg for pg in context.pages if "avalia" in pg.url][0]
    
    print("Conectado ao AVALIA:", page.url)
    
    # Buscar lista de questões lançadas via DOM ou API interna
    data = page.evaluate("""async () => {
        try {
            const resp = await fetch('https://avalia.grupoa.com.br/Elaborador/Questoes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' },
                body: 'idTipo=0'
            });
            const html = await resp.text();
            
            const div = document.createElement('div');
            div.innerHTML = html;
            const rows = Array.from(div.querySelectorAll('tr')).map(r => {
                const cols = Array.from(r.querySelectorAll('td, th')).map(c => c.innerText.trim());
                return cols;
            }).filter(r => r.length >= 2);
            
            return rows;
        } catch(e) {
            return e.toString();
        }
    }""")
    
    print("=== TABELA DE QUESTÕES E CÓDIGOS DO AVALIA ===")
    for row in data:
        print(row)
