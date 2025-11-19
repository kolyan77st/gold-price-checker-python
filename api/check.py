import requests
from bs4 import BeautifulSoup

def handler(request):
    try:
        url = "https://m-lombard.kz/"
        r = requests.get(url, timeout=10)
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

        text = f"585: {price_585}, 750: {price_750}, 999: {price_999}"
        return {"status": 200, "body": text}

    except Exception as e:
        return {"status": 500, "body": f"Ошибка: {str(e)}"}
