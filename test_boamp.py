# test_api.py
import requests
import json

def test_api():
    # Test 1: Sans filtre
    print("=== TEST 1: Sans filtre ===")
    url1 = "https://boamp-datadila.opendatasoft.com/api/records/1.0/search/?dataset=boamp&rows=3"
    r1 = requests.get(url1)
    print(f"Status: {r1.status_code}")
    print(f"Total: {r1.json().get('nhits', 0)}")
    
    # Afficher la structure
    if r1.json().get('records'):
        record = r1.json()['records'][0]['fields']
        print("\nStructure du premier record:")
        for key, value in record.items():
            print(f"  {key}: {value}")
    
    # Test 2: Avec facet pour voir les valeurs possibles
    print("\n=== TEST 2: Valeurs possibles pour code_departement ===")
    url2 = "https://boamp-datadila.opendatasoft.com/api/records/1.0/search/?dataset=boamp&rows=0&facet=code_departement"
    r2 = requests.get(url2)
    facets = r2.json().get('facet_groups', [])
    for facet in facets:
        if facet.get('name') == 'code_departement':
            print("Valeurs de département disponibles:")
            for item in facet.get('facets', [])[:20]:  # 20 premières
                print(f"  {item.get('name')}: {item.get('count')} résultats")
    
    # Test 3: Chercher les DOM par nom dans 'dc'
    print("\n=== TEST 3: Recherche par nom DOM ===")
    for dom in ["GUADELOUPE", "MARTINIQUE", "REUNION"]:
        url3 = f"https://boamp-datadila.opendatasoft.com/api/records/1.0/search/?dataset=boamp&q={dom}&rows=1"
        r3 = requests.get(url3)
        count = r3.json().get('nhits', 0)
        print(f"  {dom}: {count} résultats")

if __name__ == "__main__":
    test_api()