from flask import Flask, Response, request
import requests
import os
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

app = Flask(__name__)

# --- Настройки Email ---
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

# --- API URLs ---
GOLD_API_URL = "https://m-lombard.kz/ru/api/admin/purities/?format=json"
KURS_KZ_URL = "https://kurs.kz/informers/informer_frame_2.php"

# --- Адресаты ---
RECIPIENTS = ["KZJ78@yandex.kz", "alex77st@mail.ru"]


# ==================================================================
#  EMAIL отправка
# ==================================================================
def send_email(text):
    msg = MIMEText(text, "plain", "utf-8")
    msg["Subject"] = "Цены на золото + курс доллара"
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
#  Получение цен золота из M-Lombard
# ==================================================================
def get_gold_prices():
    try:
        r = requests.get(GOLD_API_URL, timeout=15)
        r.raise_for_status()
        data = r.json()

        # Формируем словарь: {"585": 37470, ...}
        prices = {item["code"]: item["price"] for item in data}

        return prices

    except Exception as e:
        print("Ошибка API M-Lombard:", e)
        raise


# ==================================================================
#  Получение USD из Kurs.kz
# ==================================================================
def get_usd_rate_kurs():
    try:
        r = requests.get(KURS_KZ_URL, timeout=10)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        # Ищем строку, где встречается текст "USD"
        rows = soup.find_all("tr")

        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 3:
                text = cells[0].get_text(strip=True)
                if "USD" in text.upper():
                    buy = cells[1].get_text(strip=True)
                    sell = cells[2].get_text(strip=True)
                    return buy, sell

        return None, None

    except Exception as e:
        print("Ошибка получения USD с Kurs.kz:", e)
        return None, None



# ==================================================================
#  Основной маршрут
# ==================================================================
@app.route("/api/check")
def check_gold():

    try:
        # --- Цены золота ---
        prices = get_gold_prices()

        # --- USD курс ---
        buy, sell = get_usd_rate_kurs()

        usd_text = (
            f"USD (Kurs.kz): покупка {buy} тг, продажа {sell} тг"
            if buy and sell else
            "USD (Kurs.kz): нет данных"
        )

        # --- Формируем письмо ---
        result = (
            "Текущие цены на золото (M-Lombard):\n"
            f"585 проба: {prices.get('585', 'нет данных')} тг\n"
            f"750 проба: {prices.get('750', 'нет данных')} тг\n"
            f"999 проба: {prices.get('999', 'нет данных')} тг\n\n"
            "Курс доллара:\n"
            f"{usd_text}\n"
        )

        # test режим — только показать данные
        if request.args.get("test") == "1":
            return Response(result, status=200, mimetype="text/plain")

        # отправка письма
        send_email(result)

        return Response(result, status=200, mimetype="text/plain")

    except Exception as e:
        return Response(f"Ошибка: {str(e)}", status=500, mimetype="text/plain")


# ==================================================================
#  Локальный запуск
# ==================================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
