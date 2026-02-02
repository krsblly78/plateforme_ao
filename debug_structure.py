# debug_boamp.py
import sys
import os

# Ajouter le projet au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Tester le scraper directement
from ingest.boamp.scraper import scrape_boamp_site

print("=" * 60)
print("🧪 TEST DIRECT DU SCRAPER BOAMP")
print("=" * 60)

# Test avec différentes approches
test_cases = [
    {"days": 7, "name": "7 derniers jours"},
    {"days": 30, "name": "30 derniers jours"},
    {"days": 90, "name": "90 derniers jours"},
]

for test in test_cases:
    print(f"\n🔍 Test: {test['name']}")
    results = scrape_boamp_site(days=test['days'])
    
    if results:
        print(f"✅ Trouvé {len(results)} résultats:")
        for i, result in enumerate(results[:5], 1):
            print(f"  {i}. {result['titre'][:80]}...")
            if result.get('lien'):
                print(f"     🔗 {result['lien'][:100]}")
    else:
        print("❌ Aucun résultat")
        
    print("-" * 60)

print("\n🎯 Pour debug avancé:")
print("1. Ouvrez le fichier 'debug_boamp_page.html' dans votre navigateur")
print("2. Inspectez la structure HTML avec F12")
print("3. Ajustez les sélecteurs dans scraper.py")