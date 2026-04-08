import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_latest_spot():
    url = "https://www.autogespot.fr/spots"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print(f"Connexion à {url}...")
    res = requests.get(url, headers=headers)
    print(f"Statut page : {res.status_code}")
    
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # On cherche toutes les images pour voir ce que le site renvoie
    images = soup.find_all('img')
    print(f"Nombre d'images trouvées sur la page : {len(images)}")

    # On essaie de trouver spécifiquement le premier spot
    # Autogespot utilise souvent la classe 'spot-image' ou 'spot-grid-image'
    img_tag = soup.find('img', class_='spot-image-image') or soup.find('img', class_='spot-image')
    
    if img_tag:
        img_url = img_tag['src'].replace('medium', 'large')
        if not img_url.startswith('http'):
            img_url = "https:" + img_url
        print(f"Image trouvée : {img_url}")
        return img_url
    
    print("❌ Erreur : Impossible de trouver la balise image du spot.")
    return None

def send_to_telegram(photo_url):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    payload = {'chat_id': CHAT_ID, 'photo': photo_url, 'caption': '🏎️ Nouveau spot !'}
    
    print(f"Envoi à Telegram (ID: {CHAT_ID})...")
    response = requests.post(api_url, data=payload)
    
    if response.status_code == 200:
        print("✅ Message envoyé avec succès !")
    else:
        print(f"❌ Erreur Telegram : {response.status_code} - {response.text}")

if __name__ == "__main__":
    url = get_latest_spot()
    if url:
        send_to_telegram(url)
