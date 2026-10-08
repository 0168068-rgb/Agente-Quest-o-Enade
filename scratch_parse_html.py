from bs4 import BeautifulSoup
import json

with open("/home/hamilcar/Antigravity/professor_live.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

tables = soup.find_all("table")
print(f"Total de tabelas: {len(tables)}")

for idx, t in enumerate(tables):
    print(f"\n--- TABELA {idx + 1} ---")
    headers = [th.get_text(strip=True) for th in t.find_all("th")]
    print("Headers:", headers)
    
    rows = t.find_all("tr")
    print(f"Linhas (tr): {len(rows)}")
    for r_idx, r in enumerate(rows[:5]):
        cols = [td.get_text(strip=True) for td in r.find_all(["td", "th"])]
        print(f"  Row {r_idx}: {cols}")
        # também mostrar links em cada td
        tds = r.find_all("td")
        for c_i, td in enumerate(tds):
            links = td.find_all(["a", "button", "span"])
            if links:
                print(f"    Col {c_i} ({headers[c_i] if c_i < len(headers) else '?'}) -> {[l.get_text(strip=True) for l in links]} | attrs: {[l.attrs for l in links]}")
