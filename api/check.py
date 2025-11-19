from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.mime.text import MIMEText
import time

app = Flask(__name__)

SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
URL = "https://m-lombard.kz/"

def send_email(text):
    recipients = ["KZJ78@yandex.kz", "alex77st@mail.ru"]
    msg = MIMEText(text, "plain", "utf-8")
    msg["Subject"] = "Цены на золото (585, 750, 999)"
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(recipients)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.sendmail(EMAIL_USER, recipients, msg.as_string())
    server.quit()

@app.route("/api/check")
def check_gold():
    try:
        if not SCRAPER_API_KEY:
            return Response("SCRAPER_API_KEY не задан", status=500)

        scraper_url = f"https://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={URL}&render=true"

        # retry 3 раза
        for attempt in range(3):
            try:
                r = requests.get(scraper_url, timeout=60)
                r.raise_for_status()
                break
            except requests.exceptions.RequestException:
                if attempt < 2:
                    time.sleep(5)
                else:
                    return Response("Scraper API не отвечает после 3 попыток", status=500)

        soup = BeautifulSoup(r.text, "html.parser")

        price_585 = price_750 = price_999 = "Нет данных"

        # простой поиск по тексту (можно уточнить селекторы)
        for div in soup.find_all("div"):
            text = div.get_text(strip=True)
            if "585" in text:
                price_585 = text.split()[-1]
            elif "750" in text:
                price_750 = text.split()[-1]
            elif "999" in text:
                price_999 = text.split()[-1]

        result = (
            f"Текущие цены на золото:\n"
            f"585 проба: {price_585}\n"
            f"750 проба: {price_750}\n"
            f"999 проба: {price_999}\n"
        )

        send_email(result)
        return Response(result, status=200, mimetype="text/plain")

    except Exception as e:
        return Response(f"Ошибка: {str(e)}", status=500, mimetype="text/plain")
