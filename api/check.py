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

    try:
        # Используем SMTP_SSL и порт 465 (часто надежнее для Gmail)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, recipients, msg.as_string())
        server.quit()
        return True, "Письмо отправлено"
    except Exception as e:
        print(f"Ошибка SMTP: {e}") # Смотрите логи сервера
        return False, str(e)

@app.route("/api/check")
def check_gold():
    try:
        if not SCRAPER_API_KEY or not EMAIL_USER or not EMAIL_PASS:
            return Response("Не заданы API ключи или почта", status=500)

        scraper_url = f"https://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={URL}&render=true"

        # --- Логика парсинга ---
        r = None
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
                    return Response(f"Scraper API ошибка: {str(e)}", status=500)

        soup = BeautifulSoup(r.text, "html.parser")
        blocks = soup.select('div.big.fst-normal')

        # Проверка, что верстка спарсилась
        if not blocks:
             return Response("Не найдены элементы цен на странице (изменилась верстка?)", status=500)

        price_585 = blocks[0].get_text(strip=True) if len(blocks) > 0 else "Нет данных"
        price_750 = blocks[1].get_text(strip=True) if len(blocks) > 1 else "Нет данных"
        price_999 = blocks[2].get_text(strip=True) if len(blocks) > 2 else "Нет данных"

        result = (
            f"Текущие цены на золото:\n"
            f"585 проба: {price_585}\n"
            f"750 проба: {price_750}\n"
            f"999 проба: {price_999}\n"
        )
        
        # --- Попытка отправки ---
        success, msg = send_email(result)
        
        if success:
            return Response(f"Успех! {result}", status=200, mimetype="text/plain")
        else:
            return Response(f"Данные получены, но ошибка отправки почты: {msg}\n\n{result}", status=500, mimetype="text/plain")

    except Exception as e:
        return Response(f"Общая ошибка скрипта: {str(e)}", status=500, mimetype="text/plain")