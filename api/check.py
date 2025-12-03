from flask import Flask, Response, request
import requests
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# --- Настройки ---
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "12345")

# --- API M-Lombard ---
API_URL = "https://m-lombard.kz/ru/api/admin/purities/?format=json"

# --- Кому отправлять ---
RECIPIENTS = ["KZJ78@yandex.kz", "alex77st@mail.ru"]


# ==================================================================
#  EMAIL
# ==================================================================
def send_email(text):
    msg = MIMEText(text, "plain", "utf-8")
    msg["Subject"] = "Цены на золото (585 / 750 / 999)"
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(RECIPIENTS)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, RECIPIENTS, msg.as_string())
        print("Email отправлен")
    except Exception as e:
        print("Ошибка отправки email:", e)
        raise


# ==================================================================
#  Получение JSON из API M-Lombard
# ==================================================================
def get_prices():
    try:
        r = requests.get(API_URL, timeout=15)
        r.raise_for_status()
        data = r.json()

        # Ждём формат:
        # [{"id":1,"purity":"585","price":"19900"}, ...]
        prices = {item["purity"]: item["price"] for item in data}

        return prices

    except Exception as e:
        print("Ошибка API M-Lombard:", e)
        raise


# ==================================================================
#  Эндпоинт
# ==================================================================
@app.route("/api/check")
def check_gold():
    try:
        prices = get_prices()

        result = (
            "Текущие цены на золото:\n"
            f"585 проба: {prices.get('585', 'нет данных')}\n"
            f"750 проба: {prices.get('750', 'нет данных')}\n"
            f"999 проба: {prices.get('999', 'нет данных')}\n"
        )

        # Если указан ?test=1 — письмо не отправляем
        if request.args.get("test") == "1":
            return Response(result, status=200, mimetype="text/plain")

        send_email(result)
        return Response(result, status=200, mimetype="text/plain")

    except Exception as e:
        return Response(f"Ошибка: {str(e)}", status=500, mimetype="text/plain")
