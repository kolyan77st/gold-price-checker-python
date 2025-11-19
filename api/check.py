from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

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

        url = "https://m-lombard.kz/"
        scraper_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
        r = requests.get(scraper_url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        imgs = soup.find_all("img", alt=lambda x: x and "Проба" in x)
        price_585 = price_750 = price_999 = "Нет данных"

        for img in imgs:
            alt = img.get('alt', '')
            if "585" in alt:
                price_585 = alt.split()[-1]
            elif "750" in alt:
                price_750 = alt.split()[-1]
            elif "999" in alt:
                price_999 = alt.split()[-1]

        text = (
            f"Текущие цены на золото:\n"
            f"585 проба: {price_585}\n"
            f"750 проба: {price_750}\n"
            f"999 проба: {price_999}\n"
        )

        send_email(text)
        return Response(text, status=200, mimetype="text/plain")

    except Exception as e:
        return Response(f"Ошибка: {str(e)}", status=500, mimetype="text/plain")
