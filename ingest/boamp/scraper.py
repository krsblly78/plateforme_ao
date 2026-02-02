import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re
import json

DOMTOM = ["971", "972", "973", "974", "975", "976", "977", "978"]

def scrape_boamp_site(days=30):
    """
    Scraping de la NOUVELLE interface BOAMP (pages/recherche)
    Construit l'URL exacte basée sur les filtres de l'utilisateur.
    """
    base_url = "https://www.boamp.fr"
    results = []
    
    # 1. CALCUL DES DATES POUR LE FILTRE "avis en cours"
    # L'URL utilise une logique : date de réponse >= X OU (pas de date de réponse ET fin diffusion >= X)
    aujourdhui = datetime.now()
    date_reference = (aujourdhui - timedelta(days=days)).strftime("%Y-%m-%d")
    date_du_jour = aujourdhui.strftime("%Y-%m-%d")  # Pour une recherche "en cours" à date du jour
    
    print(f"[SCRAPE] Recherche des avis EN COURS (actifs à la date du jour: {date_du_jour})")
    
    # 2. CONSTRUCTION DE L'URL EXACTE (comme celle du navigateur)
    # Paramètres de base pour les DOM-TOM
    params_domtom = "&".join([f"refine.code_departement={dept}" for dept in DOMTOM])
    
    # Construction du filtre d'état complexe "avis en cours"
    # Filtre original : (NOT #null(datelimitereponse) AND datelimiteresponse>="DATE") OR (#null(datelimitereponse) AND datefindiffusion>="DATE")
    filtre_etat = f'q.filtre_etat=(NOT%20%23null(datelimitereponse)%20AND%20datelimitereponse%3E%3D%22{date_du_jour}%22)%20OR%20(%23null(datelimitereponse)%20AND%20datefindiffusion%3E%3D%22{date_du_jour}%22)'
    
    # URL finale identique à celle du navigateur
    search_url = f"{base_url}/pages/recherche/?disjunctive.type_marche&disjunctive.descripteur_code&disjunctive.dc&disjunctive.code_departement&disjunctive.type_avis&disjunctive.famille&sort=dateparution&{params_domtom}&{filtre_etat}#resultarea"
    
    print(f"[SCRAPE] URL construite : {search_url[:150]}...")
    
    # 3. HEADERS POUR IMITER UN NAVIGATEUR
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        # 4. REQUÊTE HTTP
        print("[SCRAPE] Envoi de la requête...")
        time.sleep(1)  # Courtoisie
        response = requests.get(search_url, headers=headers, timeout=30)
        
        print(f"[SCRAPE] Statut HTTP : {response.status_code}")
        
        if response.status_code != 200:
            print(f"[SCRAPE] ❌ La requête a échoué. Vérifiez l'URL.")
            # Sauvegarde pour debug
            with open("debug_page_failed.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            return []
        
        # 5. ANALYSE DE LA PAGE
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # DEBUG : Sauvegarde la page complète
        with open("debug_boamp_page.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print("[SCRAPE] Page HTML sauvegardée dans 'debug_boamp_page.html'")
        
        # 6. IDENTIFICATION DES RÉSULTATS
        # Regarde d'abord le message "Résultats par page"
        resultats_texte = soup.find(text=re.compile(r'Résultats par page'))
        if resultats_texte:
            print("[SCRAPE] Structure de résultats détectée.")
        
        # ESSAI 1 : Chercher les cartes de résultats
        # Les avis sont probablement dans des éléments structurés
        result_cards = soup.find_all(['article', 'div'], class_=lambda x: x and ('avis' in x.lower() or 'resultat' in x.lower() or 'card' in x.lower()))
        
        if not result_cards:
            # ESSAI 2 : Chercher dans les tables
            result_cards = soup.find_all('tr', class_=lambda x: x and ('ligne' in x.lower() or 'avis' in x.lower()))
        
        if not result_cards:
            # ESSAI 3 : Tout élément contenant un numéro d'avis
            result_cards = soup.find_all(text=re.compile(r'AVIS|Avis|avis'))
            result_cards = [elem.parent for elem in result_cards if elem.parent]
        
        print(f"[SCRAPE] {len(result_cards)} blocs d'annonce potentiels trouvés.")
        
        # 7. EXTRACTION DES DONNÉES
        for i, card in enumerate(result_cards[:50]):  # Limite pour le test
            try:
                ao_data = extract_avis_data(card, base_url)
                if ao_data:
                    results.append(ao_data)
                    print(f"  ✅ {i+1}. {ao_data['titre'][:60]}...")
            except Exception as e:
                print(f"  ⚠️ Erreur sur l'élément {i+1}: {e}")
                continue
        
        # 8. VÉRIFICATION DU NOMBRE TOTAL D'ANNONCES
        # Cherche le texte "Page de résultats n° 1 - nombre de résultats par page : X"
        page_info = soup.find(text=re.compile(r'Page de résultats n°'))
        if page_info:
            print(f"[SCRAPE] Info de pagination : {page_info.strip()}")
        
        # Cherche le nombre total de résultats
        total_match = re.search(r'(\d+)\s+résultat', soup.get_text())
        if total_match:
            total = int(total_match.group(1))
            print(f"[SCRAPE] NOMBRE TOTAL D'AVIS TROUVÉS D'APRÈS LA PAGE : {total}")
        
    except Exception as e:
        print(f"[SCRAPE] ❌ Exception globale : {e}")
        import traceback
        traceback.print_exc()
    
    print(f"[SCRAPE] Extraction terminée. {len(results)} annonces parsées.")
    return results

def extract_avis_data(element, base_url):
    """
    Extrait les données d'un élément HTML représentant un avis.
    À ADAPTER après inspection du fichier debug_boamp_page.html
    """
    # STRATÉGIE : Extraire tout le texte et en déduire les informations
    full_text = element.get_text(separator=' | ', strip=True)
    
    if len(full_text) < 50:  # Trop court, probablement pas un avis
        return None
    
    # Recherche du titre (suppose qu'il est en début de texte ou dans un élément h2/h3)
    titre_elem = element.find(['h2', 'h3', 'h4', 'strong', 'b'])
    titre = titre_elem.get_text(strip=True) if titre_elem else full_text.split('|')[0][:150]
    
    # Recherche du lien détail
    lien = ""
    link_elem = element.find('a', href=True)
    if link_elem:
        href = link_elem['href']
        if href.startswith('/'):
            lien = base_url + href
        elif href.startswith('http'):
            lien = href
        else:
            lien = base_url + '/' + href
    
    # Recherche de la date de parution (format JJ/MM/AAAA)
    date_match = re.search(r'\d{2}/\d{2}/\d{4}', full_text)
    date_pub = date_match.group(0) if date_match else ""
    
    # Recherche du numéro d'avis (ex: 26-1, 26-123)
    num_avis_match = re.search(r'\b\d{2}-\d+\b', full_text)
    num_avis = num_avis_match.group(0) if num_avis_match else ""
    
    # Identification des départements dans le texte
    departements = []
    for dept in DOMTOM:
        if dept in full_text:
            departements.append(dept)
    
    return {
        "titre": titre[:250],
        "lien": lien,
        "date_publication": date_pub,
        "numero_avis": num_avis,
        "departements": departements if departements else DOMTOM,
        "source": "website",
        "extrait": full_text[:300]  # Pour debug
    }