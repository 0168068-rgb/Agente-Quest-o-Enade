import urllib.request
import json

BASE_URL = "http://localhost:8085"
GLOBAL_API_KEY = "multi_karambola_token_2026"
INSTANCE_NAME = "karambola"
GROUP_JID = "120363234383349752@g.us"

participants = [
    "5521981497448",
    "5521991659791",
    "5521967779019",
    "5521984125493",
    "5521995937048"
]

url = f"{BASE_URL}/group/updateParticipant/{INSTANCE_NAME}?groupJid={GROUP_JID}"
headers = {
    "apikey": GLOBAL_API_KEY,
    "Content-Type": "application/json"
}
data = {
    "action": "add",
    "participants": participants
}

req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print("RESPOSTA EVOLUTION API:", json.dumps(res, indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    err_content = e.read().decode("utf-8")
    print("HTTP ERROR:", e.code, err_content)
except Exception as e:
    print("ERRO:", e)
