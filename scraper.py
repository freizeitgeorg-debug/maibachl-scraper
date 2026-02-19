import requests
import os
import time
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText




def check_secrets():
    required = ["EMAIL_USER", "EMAIL_PASS", "EMAIL_TO"]
    missing = []

    for key in required:
        value = os.getenv(key)
        if value is None or value.strip() == "":
            missing.append(key)

    if missing:
        print("❌ FEHLENDE SECRETS:", ", ".join(missing))
        raise SystemExit("Abbruch: Secrets fehlen oder sind leer.")
    else:
        print("✅ Alle Secrets vorhanden.")

# Direkt nach den Imports aufrufen:
check_secrets()





URL = "https://hydrographie.ktn.gv.at/grundwasser_quellen/quellen"
MAX_RETRIES = 5
RETRY_DELAY = 5  # Sekunden

def send_email(subject, body):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    recipient = os.getenv("EMAIL_TO")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print("E-Mail gesendet:", subject)


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
    # Test-E-Mail – wird bei jedem Lauf gesendet
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

