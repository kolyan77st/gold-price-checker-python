from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.mime.text import MIMEText
import time

app = Flask(__name__)

# --- Настройки из Environment Variables ---
SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")
EMAIL_USER = os.environ.get("EMAIL_USER")  # Gmail, например kolyan77st@gmail.com
EMAIL_PASS = os.environ.get("EMAIL_PASS")  # App Password Gmail
URL = "https://m-lombard.kz/"

# --- Список адресатов ---
RECIPIENTS = ["KZJ78@yandex.kz", "alex77st@mail.ru"]

# --- Функция отправки письма ---
def send_email(text):
    msg = MIMEText(text, "plain", "utf-8")
    msg["Subject"] = "Цены на золото (585, 750, 999)"
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(RECIPIENTS)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, RECIPIENTS, msg.as_string())
        print("Email успешно отправлен на:", RECIPIENTS)
    except Exception as e:
        print("Ошибка при отправке email:", e)
        raise
    finally:
        server.quit()

# --- Основная функция ---
@app.route("/api/check")
def check_gold():
    try:
        if not SCRAPER_API_KEY:
            return Response("SCRAPER_API_KEY не задан", status=500)

        scraper_url = f"https://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={URL}&render=true"

        # --- Попытки получения страницы через Scraper API ---
        for attempt in range(3):
            try:
                r = requests.get(scraper_url, timeout=60)
                r.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                print(f"Попытка {attempt+1} не удалась: {e}")
                if attempt < 2:
                    time.sleep(5)
                else:
                    return Response("Scraper API не отвечает после 3 попыток", status=500)

        soup = BeautifulSoup(r.text, "html.parser")
        blocks = soup.select('div.big.fst-normal')

        price_585 = blocks[0].get_text(strip=True) if len(blocks) > 0 else "Нет данных"
        price_750 = blocks[1].get_text(strip=True) if len(blocks) > 1 else "Нет данных"
        price_999 = blocks[2].get_text(strip=True) if len(blocks) > 2 else "Нет данных"

        result = (
            f"Текущие цены на золото:\n"
            f"585 проба: {price_585}\n"
            f"750 проба: {price_750}\n"
            f"999 проба: {price_999}\n"
        )

        # --- Отправка письма ---
        try:
            send_email(result)
        except Exception as e:
            return Response(f"Ошибка отправки email: {e}", status=500, mimetype="text/plain")

        return Response(result, status=200, mimetype="text/plain")

    except Exception as e:
        return Response(f"Ошибка: {str(e)}", status=500, mimetype="text/plain")
