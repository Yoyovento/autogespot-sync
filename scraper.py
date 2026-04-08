import requests
from bs4 import BeautifulSoup
import os

# Récupération des secrets depuis GitHub
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_latest_spot():
    url = "https://www.autogespot.fr/spots"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # On cherche la première image de spot
    img = soup.find('img', class_='spot-image')
    if img:
        return img['src'].replace('medium', 'large')
    return None

def send_to_telegram(photo_url):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    data = {'chat_id': CHAT_ID, 'photo': photo_url, 'caption': 'Nouveau spot trouvé !'}
    requests.post(api_url, data=data)

if __name__ == "__main__":
    url = get_latest_spot()
    if url:
        send_to_telegram(url)
