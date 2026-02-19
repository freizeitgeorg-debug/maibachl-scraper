import os
import json
import time
import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from google.auth.transport.requests import Request

URL = "https://hydrographie.ktn.gv.at/grundwasser_quellen/quellen"
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
FIREBASE_PROJECT_ID = "maibachlapp"  # Dein Firebase-Projektname
SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT")

MAX_RETRIES = 5
RETRY_DELAY = 5


def get_access_token():
    info = json.loads(SERVICE_ACCOUNT_JSON)
    credentials = service_account.Credentials.from_service_account_info(
        info, scopes=SCOPES
    )
    credentials.refresh(Request())
    return credentials.token


def send_push_notification(title, body):
    token = get_access_token()

    url = f"https://fcm.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/messages:send"

    message = {
        "message": {
            "topic": "maibachl",
            "notification": {
                "title": title,
                "body": body
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; UTF-8",
    }

    response = requests.post(url, headers=headers, json=message)
    print("Push-Response:", response.text)


def fetch_page_with_retry():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Versuch {attempt}/{MAX_RETRIES}…")
            response = requests.get(URL, timeout=20)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Fehler beim Abrufen: {e}")
            if attempt < MAX_RETRIES:
                print(f"Warte {RETRY_DELAY} Sekunden…")
                time.sleep(RETRY_DELAY)
            else:
                print("Seite nicht erreichbar – fahre fort.")
                return None


def fetch_maibachl_status(html):
    if html is None:
        return "Unbekannt (Seite nicht erreichbar)"

    soup = BeautifulSoup(html, "html.parser")
    row = soup.find("tr", string=lambda t: t and "Maibachl" in t)

    if not row:
        return "Unbekannt (Maibachl nicht gefunden)"

    cells = row.find_all("td")
    if len(cells) < 2:
        return "Unbekannt (Tabellenformat fehlerhaft)"

    return cells[1].get_text(strip=True)


def main():
    # Testnachricht – garantiert, dass Push funktioniert
    send_push_notification("Testnachricht", "HTTP v1 funktioniert!")

    html = fetch_page_with_retry()
    status = fetch_maibachl_status(html)
    print("Status:", status)

    if "führt" in status.lower() or "wasser" in status.lower():
        send_push_notification("Maibachl führt Wasser!", f"Aktueller Status: {status}")
    else:
        print("Maibachl führt kein Wasser.")


if __name__ == "__main__":
    main()
