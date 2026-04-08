import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_latest_spot():
    url = "https://www.autogespot.fr/spots"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    print(f"1. Tentative de connexion à {url}...")
    res = requests.get(url, headers=headers)
    print(f"2. Connexion réussie (200) !" if res.status_code == 200 else f"2. Erreur {res.status_code}")
    
    soup = BeautifulSoup(res.text, 'html.parser')
    images = soup.find_all('img')
    print(f"3. Nombre total d'images trouvées : {len(images)}")
    
    for img in images:
        # Les sites modernes cachent parfois le lien dans 'data-src' pour charger plus vite
        img_url = img.get('data-src') or img.get('src') or ''
        
        # On filtre : on veut un JPG, et on exclut les avatars ou les logos du site
        if '.jpg' in img_url.lower() and 'logo' not in img_url.lower() and 'avatar' not in img_url.lower():
            # On force la haute résolution pour ton fond d'écran
            img_url = img_url.replace('small', 'large').replace('medium', 'large')
            
            # On répare le lien s'il est incomplet
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = 'https://www.autogespot.fr' + img_url
                
            print(f"4. ✅ Super ! Image trouvée : {img_url}")
            return img_url
            
    print("❌ Erreur : Impossible de trouver une voiture parmi les images.")
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
