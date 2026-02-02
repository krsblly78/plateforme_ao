# scrape_boamp_web.py
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def scrape_boamp_website(days=30):
    """
    Scraping direct du site BOAMP (plus fiable)
    """
    base_url = "https://www.boamp.fr"
    
    # Calculer la date de début
    start_date = datetime.now() - timedelta(days=days)
    date_str = start_date.strftime("%d/%m/%Y")
    
    # Construire l'URL de recherche
    # Format: https://www.boamp.fr/avis/resultats?what=&where=971,972,973,974,975,976,977,978&when=01/11/2025
    search_url = f"{base_url}/avis/resultats"
    
    params = {
        "what": "",  # Type d'avis (vide = tous)
        "where": ",".join(DOMTOM),  # Codes départements
        "when": date_str,  # Date minimum
        "page": 1
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    try:
        print(f"🌐 Scraping BOAMP: {search_url}")
        print(f"📋 Paramètres: {params}")
        
        response = requests.get(search_url, params=params, headers=headers, timeout=30)
        print(f"📊 Statut: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Chercher les résultats (structure à inspecter)
            results = []
            
            # 1. Chercher les div d'annonces
            announcements = soup.find_all('div', class_='annonce')
            
            # 2. Si pas trouvé, chercher par d'autres sélecteurs
            if not announcements:
                announcements = soup.find_all('article', class_='avis')
            
            # 3. Si toujours pas, chercher dans les tables
            if not announcements:
                announcements = soup.find_all('tr', class_='ligne-avis')
            
            print(f"🔍 {len(announcements)} annonces trouvées")
            
            for ann in announcements:
                try:
                    # Extraire le titre
                    title_elem = ann.find(['h3', 'h4', 'a', 'span'], class_=['titre', 'title'])
                    if not title_elem:
                        title_elem = ann.find('strong')
                    
                    titre = title_elem.text.strip() if title_elem else "Titre non disponible"
                    
                    # Extraire le lien
                    link_elem = ann.find('a', href=True)
                    lien = base_url + link_elem['href'] if link_elem else ""
                    
                    # Extraire la date
                    date_elem = ann.find(['time', 'span', 'div'], class_=['date', 'publication'])
                    date_pub = date_elem.text.strip() if date_elem else ""
                    
                    results.append({
                        "titre": titre,
                        "lien": lien,
                        "date_publication": date_pub,
                        "departements": DOMTOM  # On sait que c'est DOM-TOM
                    })
                    
                except Exception as e:
                    print(f"⚠️ Erreur parsing annonce: {e}")
                    continue
            
            return results
            
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Exception scraping: {e}")
        return []