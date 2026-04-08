import requests
from bs4 import BeautifulSoup
import os
from io import BytesIO
from PIL import Image, ImageFilter

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def get_latest_spot():
    url = "https://www.autogespot.fr/spots"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    print("1. Connexion à Autogespot...")
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    images = soup.find_all('img')
    
    for img in images:
        img_url = img.get('data-src') or img.get('src') or ''
        if '.jpg' in img_url.lower() and 'logo' not in img_url.lower() and 'avatar' not in img_url.lower():
            img_url = img_url.replace('small', 'large').replace('medium', 'large')
            if img_url.startswith('//'): img_url = 'https:' + img_url
            elif img_url.startswith('/'): img_url = 'https://www.autogespot.fr' + img_url
            print(f"2. Image trouvée : {img_url}")
            return img_url
    return None

def create_wallpaper_and_send(img_url):
    print("3. Téléchargement et transformation de l'image...")
    
    # On télécharge l'image
    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content))
    
    # Taille standard d'un écran de smartphone (1080x1920)
    target_w, target_h = 1080, 1920
    
    # --- Création du fond flou ---
    bg_ratio = max(target_w / img.width, target_h / img.height)
    bg_w, bg_h = int(img.width * bg_ratio), int(img.height * bg_ratio)
    bg_img = img.resize((bg_w, bg_h), Image.Resampling.LANCZOS)
    
    # On recadre au centre
    left = (bg_w - target_w) / 2
    top = (bg_h - target_h) / 2
    bg_img = bg_img.crop((left, top, left + target_w, top + target_h))
    
    # On applique un beau flou
    bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=30))
    
    # --- Ajout de la voiture nette au centre ---
    fg_ratio = target_w / img.width
    fg_w, fg_h = target_w, int(img.height * fg_ratio)
    fg_img = img.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
    
    paste_y = (target_h - fg_h) // 2
    bg_img.paste(fg_img, (0, paste_y))
    
    # On sauvegarde temporairement
    wallpaper_path = "wallpaper.jpg"
    bg_img.save(wallpaper_path, quality=95)
    
    print("4. Envoi de l'image format Mobile à Telegram...")
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    
    # Cette fois on envoie le Fichier, pas juste le lien
    with open(wallpaper_path, 'rb') as photo:
        payload = {'chat_id': CHAT_ID, 'caption': '📱 Nouveau spot (Format Mobile) !'}
        res = requests.post(api_url, data=payload, files={'photo': photo})
        
    if res.status_code == 200:
        print("5. ✅ Fond d'écran envoyé avec succès !")
    else:
        print(f"5. ❌ Erreur Telegram : {res.text}")

if __name__ == "__main__":
    url = get_latest_spot()
    if url:
        create_wallpaper_and_send(url)
