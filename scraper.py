import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_latest_spot():
    url = "https://www.autogespot.fr/spots"
    # On met un déguisement de vrai navigateur très complet
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    print(f"1. Tentative de connexion à {url}...")
    res = requests.get(url, headers=headers)
    print(f"2. Réponse du site Autogespot : Erreur {res.status_code}" if res.status_code != 200 else "2. Connexion au site réussie (200) !")
    
    soup = BeautifulSoup(res.text, 'html.parser')
    images = soup.find_all('img')
    print(f"3. Nombre total d'images trouvées sur la page : {len(images)}")
    
    # On cherche l'image
    for img in images:
        if img.has_attr('class') and any('spot' in c for c in img['class']):
            img_url = img['src'].replace('medium', 'large')
            if not img_url.startswith('http'):
                img_url = "https:" + img_url
            print(f"4. ✅ Super ! Image trouvée : {img_url}")
            return img_url
            
    print("❌ Erreur : Impossible de trouver une voiture. Autogespot a peut-être changé son code ou bloqué l'accès.")
    return None

def send_to_telegram(photo_url):
    print("5. Préparation de l'envoi vers Telegram...")
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    payload = {'chat_id': CHAT_ID, 'photo': photo_url, 'caption': '🏎️ Nouveau spot !'}
    
    response = requests.post(api_url, data=payload)
    if response.status_code == 200:
        print("6. ✅ Message envoyé avec succès sur ton téléphone !")
    else:
        print(f"6. ❌ Erreur Telegram : {response.text}")

if __name__ == "__main__":
    url = get_latest_spot()
    if url:
        send_to_telegram(url)
