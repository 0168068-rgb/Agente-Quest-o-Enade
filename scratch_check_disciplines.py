from bs4 import BeautifulSoup
import json

with open("/home/hamilcar/Antigravity/professor_live.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

table = soup.find_all("table")[1]
headers = [th.get_text(strip=True) for th in table.find_all("th")]

print("Headers:", headers)
pre_val_idx = None
for i, h in enumerate(headers):
    if "pré-validada" in h.lower() or "pre-validada" in h.lower():
        pre_val_idx = i
        break

print("Índice da coluna 'Questões pré-validadas':", pre_val_idx)

rows = table.find_all("tr")
for r_idx, tr in enumerate(rows):
    tds = tr.find_all("td")
    if not tds or len(tds) <= (pre_val_idx or 12):
        continue
    disc_name = tds[3].get_text(strip=True) if len(tds) > 3 else "N/A"
    pre_val_cell = tds[pre_val_idx] if pre_val_idx is not None else tds[12]
    pre_val_text = pre_val_cell.get_text(strip=True)
    link = pre_val_cell.find("a")
    link_url = link.get("data-load-url") if link else None
    print(f"Disciplina: '{disc_name}' | Pré-validadas: {pre_val_text} | Link: {link_url}")

# Checar paginação do DataTables
paginate = soup.find(class_=lambda c: c and "paginate" in c)
if paginate:
    print("\nPaginação encontrada:", [a.get_text(strip=True) for a in paginate.find_all("a")])
