import os
import sys
import requests

TOKEN = os.environ.get("WEBEX_TOKEN")
if not TOKEN:
    sys.exit("Geen token gevonden. Zet eerst de omgevingsvariabele WEBEX_TOKEN.")

TITEL = "CCNA Automation Test Space"
URL = "https://webexapis.com/v1/rooms"
headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. Alle spaces ophalen
antwoord = requests.get(URL, headers=headers, timeout=30)
print("Spaces ophalen, statuscode:", antwoord.status_code)

if antwoord.status_code != 200:
    sys.exit(f"Fout: {antwoord.text}")

# 2. Spaces met de juiste titel zoeken
spaces = [r for r in antwoord.json()["items"] if r["title"] == TITEL]

if not spaces:
    sys.exit(f"Geen space gevonden met de titel '{TITEL}'.")

for space in spaces:
    antwoord = requests.delete(f"{URL}/{space['id']}", headers=headers, timeout=30)
    if antwoord.status_code == 204:
        print(f"Space '{space['title']}' verwijderd (statuscode 204).")
    else:
        print(f"Fout bij verwijderen: {antwoord.status_code} {antwoord.text}")