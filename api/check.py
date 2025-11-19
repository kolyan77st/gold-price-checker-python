import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

def send_email(text):
    EMAIL_USER = os.environ["EMAIL_USER"]
    EMAIL_PASS = os.environ["EMAIL_PASS"]

    recipients = [
        "KZJ78@yandex.kz",
        "alex77st@mail.ru"
    ]

    msg = MIMEText(text, "plain", "utf-8")
    msg["Subject"] = "Цены на золото (585, 750, 999)"
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(recipients)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.sendmail(EMAIL_USER, recipients, msg.as_string())
    server.quit()

def handler(request):
    try:
        url = "https://m-lombard.kz/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=10)
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

        # Отправка email
        send_email(text)

        return {"status": 200, "body": text}

    except Exception as e:
        return {"status": 500, "body": f"Ошибка: {str(e)}"}
