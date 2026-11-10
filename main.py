import time
import json
import requests
from bs4 import BeautifulSoup

# === НАЛАШТУВАННЯ ===
TELEGRAM_BOT_TOKEN = "9263784612:AAH6e00sFSTp_ZNc091e2hf6hiZk43jRFho"
CHAT_ID = "7987062433"

# Твоє посилання OLX (iPhone 13 Pro, б/в, до 14500 грн, найновіші)
SEARCH_URL = "https://www.olx.ua/uk/elektronika/telefony-i-aksesuary/mobilnye-telefony-smartfony/q-iphone-13-pro/?currency=UAH&search%5Border%5D=created_at:desc&search%5Bfilter_float_price:to%5D=14500&search%5Bfilter_enum_state%5D%5B0%5D=used"

SEEN_FILE = "seen_ads.json"

def load_seen():
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False)

def send_telegram_message(title, price, link):
    text = f"🔥 **Знайдено нове оголошення!**\n\n📌 **{title}**\n💰 **Ціна:** {price}\n🔗 {link}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload)

def parse_olx():
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    }
    response = requests.get(SEARCH_URL, headers=headers)
    if response.status_code != 200:
        print("Помилка завантаження сторінки OLX")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    seen_ads = load_seen()
    
    cards = soup.find_all("div", data_testid="l-card")
    
    new_found = 0
    for card in cards:
        link_elem = card.find("a", href=True)
        if not link_elem:
            continue
            
        link = link_elem["href"]
        if not link.startswith("http"):
            link = "https://www.olx.ua" + link
            
        ad_id = link.split("/")[-1].split(".html")[0]
        
        if ad_id in seen_ads:
            continue
            
        title_elem = card.find("h6")
        price_elem = card.find("p", data_testid="ad-price")
        
        title = title_elem.text.strip() if title_elem else "Без назви"
        price = price_elem.text.strip() if price_elem else "Ціна не вказана"
        
        send_telegram_message(title, price, link)
        seen_ads.add(ad_id)
        new_found += 1
        time.sleep(1)

    save_seen(seen_ads)
    print(f"Готово. Нових оголошень: {new_found}")

if __name__ == "__main__":
    parse_olx()
