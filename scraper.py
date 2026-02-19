import requests
from bs4 import BeautifulSoup
import time

# -----------------------------------------
# KONFIGURATION
# -----------------------------------------

SENDGRID_API_KEY = SENDGRID_KEY
EMAIL_FROM = "em1556.georgsu55@sendgrid.at"
EMAIL_TO = "freizeitgeorg@gmail.com"

URL = "https://hydrographie.ktn.gv.at/grundwasser_quellen/quellen"
MAX_RETRIES = 5
RETRY_DELAY = 15  # Sekunden

# -----------------------------------------
# SENDGRID E-MAIL FUNKTION
# -----------------------------------------

def send_email(subject, body):
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "personalizations": [{
            "to": [{"email": EMAIL_TO}]
        }],
        "from": {"email": EMAIL_FROM},
        "subject": subject,
        "content": [{
            "type": "text/plain",
            "value": body
        }]
    }

    response = requests.post(url, headers=headers, json=data)
    print("SendGrid Response:", response.status_code, response.text)


# -----------------------------------------
# MAIBACHL SCRAPER
# -----------------------------------------

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
    # Test-E-Mail bei jedem Lauf
    send_email("Testnachricht", "Der Maibachl-Scraper läuft!")

    html = fetch_page_with_retry()
    status = fetch_maibachl_status(html)
    print("Status:", status)

    if "führt" in status.lower() or "wasser" in status.lower():
        send_email("Maibachl führt Wasser!", f"Aktueller Status: {status}")
    else:
        print("Maibachl führt kein Wasser.")


if __name__ == "__main__":
    main()



