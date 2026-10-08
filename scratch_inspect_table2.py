from bs4 import BeautifulSoup
import json

with open("/home/hamilcar/Antigravity/professor_live.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

table = soup.find_all("table")[1] # Tabela 2
headers = [th.get_text(strip=True) for th in table.find_all("th")]

print("=== CABEÇALHOS DA TABELA 2 ===")
for i, h in enumerate(headers):
    print(f"Col {i}: {h}")

print("\n=== LINHAS DA TABELA 2 ===")
for r_idx, tr in enumerate(table.find_all("tr")):
    tds = tr.find_all("td")
    if not tds:
        continue
    print(f"\n--- LINHA {r_idx} ---")
    for i, td in enumerate(tds):
        header_name = headers[i] if i < len(headers) else "N/A"
        txt = td.get_text(strip=True)
        links = td.find_all("a")
        link_info = []
        for a in links:
            link_info.append({
                "text": a.get_text(strip=True),
                "title": a.get("title"),
                "data-original-title": a.get("data-original-title"),
                "data-load-url": a.get("data-load-url"),
                "class": a.get("class")
            })
        print(f"Col {i} [{header_name}]: text='{txt}' | links={link_info}")
