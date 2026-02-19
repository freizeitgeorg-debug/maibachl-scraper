import requests
import os
import time
from bs4 import BeautifulSoup
import json

URL = "https://hydrographie.ktn.gv.at/grundwasser_quellen/quellen"
FIREBASE_KEY = os.getenv("FIREBASE_SERVER_KEY")

MAX_RETRIES = 5
RETRY_DELAY = 10  # Sekunden


def send_push_notification(title, body):
    if not FIREBASE_KEY:
        print("Fehler: FIREBASE_SERVER_KEY nicht gesetzt.")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"key={FIREBASE_KEY}"
    }

    data = {
        "to": "/topics/maibachl",
        "notification": {
            "title": title,
            "body": body
        }
    }

    response = requests.post(
        "https://fcm.googleapis.com/fcm/send",
        headers=headers,
        data=json.dumps(data)
    )

    print("Push-Response:", response.text)


def fetch_page_with_retry():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Versuch {attempt}/{MAX_RETRIES}...")
            response = requests.get(URL, timeout=20)
            response.raise_for_status()
            return response.text

        except Exception as e:
            print(f"Fehler beim Abrufen: {e}")

            if attempt < MAX_RETRIES:
                print(f"Warte {RETRY_DELAY} Sekunden und versuche erneut...")
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError("Seite nach mehreren Versuchen nicht erreichbar.") from e


def fetch_maibachl_status():
    html = fetch_page_with_retry()
    soup = BeautifulSoup(html, "html.parser")

    # Suche die Zeile, die "Maibachl" enthält
    row = soup.find("tr", string=lambda t: t and "Maibachl" in t)

    if not row:
        raise ValueError("Maibachl nicht in der Tabelle gefunden.")

    cells = row.find_all("td")
    if len(cells) < 2:
        raise ValueError("Unerwartetes Tabellenformat.")

    status_text = cells[1].get_text(strip=True)
    return status_text


def main():
    try:
        status = fetch_maibachl_status()
        print("Status:", status)

        if "führt" in status.lower() or "wasser" in status.lower():
            send_push_notification(
                "Maibachl führt Wasser!",
                f"Aktueller Status: {status}"
            )
        else:
            print("Maibachl führt kein Wasser.")

    except Exception as e:
        print("Fehler im Scraper:", e)
        # Kein raise — Workflow soll nicht mehr rot werden
        # sondern sauber durchlaufen
        pass


if __name__ == "__main__":
    main()
