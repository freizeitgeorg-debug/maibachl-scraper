import requests
import os
from bs4 import BeautifulSoup
import json

URL = "https://hydrographie.ktn.gv.at/grundwasser_quellen/quellen"
FIREBASE_KEY = os.getenv("FIREBASE_SERVER_KEY")

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


def fetch_maibachl_status():
    response = requests.get(URL, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Finde die Tabellenzeile, die "Maibachl" enthält
    row = soup.find("tr", string=lambda t: t and "Maibachl" in t)

    if not row:
        raise ValueError("Maibachl nicht in der Tabelle gefunden.")

    # Alle Zellen der Zeile
    cells = row.find_all("td")
    if len(cells) < 2:
        raise ValueError("Unerwartetes Tabellenformat.")

    # Status steht üblicherweise in der zweiten Spalte
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
        raise


if __name__ == "__main__":
    main()
