import urllib.request
import json

BASE_URL = "http://localhost:8085"
GLOBAL_API_KEY = "multi_karambola_token_2026"
INSTANCE_NAME = "karambola"

headers = {"apikey": GLOBAL_API_KEY, "Content-Type": "application/json"}

# 1. Buscar grupos
url_groups = f"{BASE_URL}/group/fetchAllGroups/{INSTANCE_NAME}?getParticipants=false"
req = urllib.request.Request(url_groups, headers=headers, method="GET")

target_group = None
all_groups = []

try:
    with urllib.request.urlopen(req) as resp:
        groups = json.loads(resp.read().decode("utf-8"))
        for g in groups:
            sub = g.get("subject") or g.get("name") or ""
            gid = g.get("id")
            all_groups.append({"id": gid, "subject": sub})
            if "alunos de redes" in sub.lower() or "redes" in sub.lower():
                target_group = {"id": gid, "subject": sub}
except Exception as e:
    print("Erro ao buscar grupos:", e)

output = {
    "target_group": target_group,
    "all_groups_count": len(all_groups),
    "all_groups": all_groups[:20] # Primeiros 20
}

with open("resultado_busca_grupo.json", "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("Busca finalizada. Resultado salvo em resultado_busca_grupo.json")
