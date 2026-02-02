# ingest/boamp/client.py
import requests
from datetime import date, datetime
import time

DOMTOM_CODES = ["971", "972", "973", "974", "975", "976", "977", "978"]

def fetch_boamp_ao(max_results=800):
    """
    Récupère les AO DOM-TOM EN COURS (date limite réponse >= aujourd'hui)
    Utilise exactement la même requête que le site web
    """
    # Date d'aujourd'hui au format YYYY-MM-DD
    date_aujourdhui = date.today().strftime("%Y-%m-%d")
    
    print(f"[API] 📅 Recherche des AO en cours à la date: {date_aujourdhui}")
    
    # Construction EXACTE comme sur le site web :
    # (NOT #null(datelimitereponse) AND datelimitereponse>="DATE") 
    # OR (#null(datelimitereponse) AND datefindiffusion>="DATE")
    q_filter = f'(NOT #null(datelimitereponse) AND datelimitereponse>="{date_aujourdhui}") OR (#null(datelimitereponse) AND datefindiffusion>="{date_aujourdhui}")'
    
    # Paramètres EXACTEMENT comme dans le network du site
    params = {
        "dataset": "boamp",
        "q": q_filter,
        "disjunctive.type_marche": "true",
        "disjunctive.descripteur_code": "true",
        "disjunctive.dc": "true",
        "disjunctive.code_departement": "true",
        "disjunctive.type_avis": "true",
        "disjunctive.famille": "true",
        # Ajouter chaque département séparément (comme sur le site)
        "refine.code_departement": "971",
        "refine.code_departement": "972", 
        "refine.code_departement": "973",
        "refine.code_departement": "974",
        "refine.code_departement": "975",
        "refine.code_departement": "976",
        "refine.code_departement": "977",
        "refine.code_departement": "978",
        "rows": min(max_results, 800),
        "sort": "-dateparution",
        "timezone": "Europe/Paris",
        "lang": "fr"
    }
    
    # Mais requests ne supporte pas les clés dupliquées, donc on fait :
    params_list = [
        "dataset=boamp",
        f"q={requests.utils.quote(q_filter)}",
        "disjunctive.type_marche=true",
        "disjunctive.descripteur_code=true",
        "disjunctive.dc=true",
        "disjunctive.code_departement=true",
        "disjunctive.type_avis=true",
        "disjunctive.famille=true",
    ]
    
    # Ajouter chaque département
    for code in DOMTOM_CODES:
        params_list.append(f"refine.code_departement={code}")
    
    params_list.extend([
        f"rows={min(max_results, 800)}",
        "sort=-dateparution",
        "timezone=Europe/Paris",
        "lang=fr"
    ])
    
    query_string = "&".join(params_list)
    url = f"https://boamp-datadila.opendatasoft.com/api/records/1.0/search/?{query_string}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.boamp.fr/',
    }
    
    try:
        print(f"[API] Requête pour AO en cours...")
        print(f"[API] URL (simplifiée): ...q={q_filter[:80]}...")
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total_hits = data.get('nhits', 0)
            records = data.get('records', [])
            
            print(f"[API] ✅ {total_hits} AO DOM-TOM en cours trouvés")
            
            # Debug: afficher les dates des premiers résultats
            if records:
                print("[API] 📅 Dates des premiers résultats:")
                for i, record in enumerate(records[:3]):
                    fields = record.get('fields', {})
                    print(f"  {i+1}. dateparution: {fields.get('dateparution')}, "
                          f"datelimitereponse: {fields.get('datelimitereponse')}")
            
            return {
                "success": True,
                "total": total_hits,
                "data": data,
                "records": records,
                "source": "exact_api_match"
            }
        else:
            print(f"[API] ❌ HTTP {response.status_code}")
            print(f"[API] Réponse: {response.text[:200]}")
            return {"success": False, "error": f"HTTP {response.status_code}", "records": []}
            
    except Exception as e:
        print(f"[API] ❌ Erreur: {e}")
        return {"success": False, "error": str(e), "records": []}

# Dans fetch_all_results de client.py
def fetch_all_results(days=None, max_results=800):
    """
    Interface pour la commande Django
    - Ignore le paramètre 'days' car on veut toujours les AO "en cours"
    - 'max_results' contrôle combien on récupère de l'API
    """
    print(f"[API] Récupération des AO DOM-TOM EN COURS (max: {max_results})")

    return fetch_boamp_ao(max_results)
    return fetch_boamp_ao(max_results)