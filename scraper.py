import requests
from bs4 import BeautifulSoup
import json
import time

URL = "https://hydrographie.ktn.gv.at/grundwasser_quellen/quellen"
FCM_URL = "https://fcm.googleapis.com/fcm/send"

SERVER_KEY = "HIER_DEIN_FIREBASE_SERVER_KEY"
DEVICE_TOKEN = "HIER_DEIN_DEVICE_TOKEN"

def get_maibachl_status():
    response = requests.get(URL, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.find_all("tr")

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) >= 3 and cols[0].lower() == "maibachl":
            value = float(cols[1].replace(",", "."))
            timestamp = cols[2]
            return value > 0, value, timestamp

    return None, None, None


def send_push(title, body):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"key={SERVER_KEY}"
    }

    payload = {
        "to": DEVICE_TOKEN,
        "notification": {
            "title": title,
            "body": body
        }
    }

    r = requests.post(FCM_URL, headers=headers, data=json.dumps(payload))
    print("FCM Response:", r.text)


def loop():
    last_status = None

    while True:
        status, value, timestamp = get_maibachl_status()

        if status is not None and status != last_status:
            if status:
                send_push("Maibachl rinnt!", f"{value} l/s – Stand {timestamp}")
            else:
                send_push("Maibachl rinnt NICHT", f"{value} l/s – Stand {timestamp}")

            last_status = status

        time.sleep(3600)  # alle 60 Minuten prüfen


if __name__ == "__main__":
    loop()
