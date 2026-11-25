import os
import sys
import requests

TOKEN = os.environ.get("WEBEX_TOKEN")
if not TOKEN:
    sys.exit("Geen token gevonden. Zet eerst de omgevingsvariabele WEBEX_TOKEN.")

URL = "https://webexapis.com/v1/rooms"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}
gegevens = {"title": "CCNA Automation Test Space"}

antwoord = requests.post(URL, headers=headers, json=gegevens, timeout=30)

print("Statuscode:", antwoord.status_code)

if antwoord.status_code == 200:
    space = antwoord.json()
    print("Space aangemaakt!")
    print("Titel:", space["title"])
    print("ID:   ", space["id"])
else:
    print("Fout:", antwoord.text)