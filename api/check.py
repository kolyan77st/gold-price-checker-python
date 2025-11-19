from http.server import BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")
URL = "https://m-lombard.kz/"

def send_email(text):
    try:
        EMAIL_USER = os.environ.get("EMAIL_USER")
        EMAIL_PASS = os.environ.get("EMAIL_PASS")
        
        if not EMAIL_USER or not EMAIL_PASS:
            print("Email credentials not set")
            return False

        recipients = ["KZJ78@yandex.kz", "alex77st@mail.ru"]

        msg = MIMEText(text, "plain", "utf-8")
        msg["Subject"] = "Цены на золото (585, 750, 999)"
        msg["From"] = EMAIL_USER
        msg["To"] = ", ".join(recipients)

        # Используем порт 465 (SSL) вместо 587 (TLS)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, recipients, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {str(e)}")
        return False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if not SCRAPER_API_KEY:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write("SCRAPER_API_KEY не задан".encode('utf-8'))
                return

            scraper_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={URL}"

            r = requests.get(scraper_url, timeout=30)
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

            email_sent = send_email(text)
            
            response_text = text
            if not email_sent:
                response_text += "\n⚠️ Письмо не отправлено (проверьте логи)"

            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(response_text.encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            error_msg = f"Ошибка: {str(e)}"
            self.wfile.write(error_msg.encode('utf-8'))

    def do_POST(self):
        self.do_GET()
