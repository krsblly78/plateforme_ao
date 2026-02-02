# ingest/boamp/parser.py
from datetime import datetime, timedelta
import re

def parse_api_response(api_result):
    """
    Parse la réponse de l'API OpenDataSoft
    """
    if not api_result or not api_result.get("success"):
        return []
    
    data = api_result.get("data") or {}
    records = data.get("records", [])
    
    if not records and "records" in api_result:
        records = api_result.get("records", [])
    
    parsed_results = []
    
    for record in records:
        fields = record.get("fields", {})
        
        # Informations de base
        titre = fields.get("objet", "Sans titre")
        numero_avis = fields.get("num_avis", "") or fields.get("idweb", "")
        
        # Date de publication
        date_parution = fields.get("dateparution", "")
        if date_parution and len(date_parution) > 10:
            date_parution = date_parution[:10]
        
        # Date limite de réponse (critère "en cours")
        date_limite_str = fields.get("datelimitereponse", "")
        if date_limite_str:
            # Nettoyer la date
            if 'T' in date_limite_str:
                date_limite_str = date_limite_str.split('T')[0]
        
        # Département
        code_dept = str(fields.get("code_departement", "")).strip()
        
        # Lien
        lien = f"https://www.boamp.fr/avis/detail/{numero_avis}" if numero_avis else ""
        
        # Type de marché
        type_marche = fields.get("type_marche", "")
        if type_marche:
            type_marche = type_marche.capitalize()
        
        ao = {
            "titre": titre[:300],
            "numero_avis": numero_avis,
            "date_publication": date_parution,
            "date_limite_reponse": date_limite_str,
            "departements": [code_dept] if code_dept else [],
            "lien": lien,
            "source": "api",
            "type_marche": type_marche,
            
            # Données supplémentaires
            "autorite_contractante": fields.get("nomacheteur", "")[:150],
            "nature_avis": fields.get("nature_libelle", ""),
        }
        
        parsed_results.append(ao)
    
    print(f"[PARSER] ✅ {len(parsed_results)} AO parsées")
    return parsed_results

def filter_by_days(results, days=30):
    """
    Filtre les résultats par date limite réponse (pas par date de publication)
    """
    if days <= 0:
        return results
    
    # On ne filtre plus par date de publication
    # mais on garde tous les AO "en cours" (déjà filtrés par l'API)
    print(f"[FILTER] 📅 Garde tous les {len(results)} AO 'en cours' (déjà filtrés par l'API)")
    return results

def sort_by_date(results):
    """
    Trie les résultats par date limite réponse (plus proche d'abord)
    """
    def get_date_key(item):
        # Priorité 1: date limite réponse
        date_str = item.get("date_limite_reponse", "")
        if date_str:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                pass
        
        # Priorité 2: date de publication
        date_str = item.get("date_publication", "")
        if date_str:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                pass
        
        # Sinon: date très lointaine
        return datetime.max
    
    return sorted(results, key=get_date_key)