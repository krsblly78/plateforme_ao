# ingest/management/commands/scrape_boamp.py
import sys
import json
from datetime import datetime
from django.core.management.base import BaseCommand

from ingest.boamp.client import fetch_all_results
from ingest.boamp.parser import parse_api_response, sort_by_date

class Command(BaseCommand):
    help = "Récupère les appels d'offres DOM-TOM EN COURS depuis l'API BOAMP"

    def add_arguments(self, parser):
        # Garder les arguments existants mais simplifier
        parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="Nombre maximum d'AO à afficher (défaut: 20)"
        )
        parser.add_argument(
            "--save",
            type=str,
            help="Sauvegarder les résultats dans un fichier JSON"
        )
        parser.add_argument(
            "--raw",
            action="store_true",
            help="Afficher les données brutes de l'API"
        )
        # Garder --days pour compatibilité mais l'ignorer
        parser.add_argument(
            "--days",
            type=int,
            default=50,
            help="⚠️ Ignoré: les AO sont toujours 'en cours' (gardé pour compatibilité)"
        )
        parser.add_argument(
            "--no-filter",
            action="store_true",
            help="⚠️ Ignoré: pas de filtre appliqué (gardé pour compatibilité)"
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Afficher les détails de débogage"
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        save_file = options.get("save")
        show_raw = options["raw"]
        debug = options["debug"]
        
        self.stdout.write("=" * 60)
        self.stdout.write("📡 API BOAMP DOM-TOM - AVIS EN COURS")
        self.stdout.write("=" * 60)
        
        try:
            # PHASE 1: Récupération depuis l'API
            self.stdout.write(f"\n[1/2] 🔍 Recherche des AO DOM-TOM EN COURS...")
            self.stdout.write(f"     📅 Actifs à la date du jour")
            self.stdout.write(f"     📊 Limite d'affichage: {limit}")
            
            # Appeler l'API pour les AO en cours
            api_result = fetch_all_results(max_results=limit * 2)  # Récupérer un peu plus pour le tri
            
            if not api_result.get("success"):
                self.stderr.write(f"\n❌ ERREUR API: {api_result.get('error', 'Inconnue')}")
                sys.exit(1)
            
            total_found = api_result.get("total", 0)
            self.stdout.write(f"     ✅ {total_found} AO trouvés par l'API")
            
            # PHASE 2: Parsing
            self.stdout.write(f"\n[2/2] 📋 Traitement des données...")
            all_ao = parse_api_response(api_result)
            
            # Trier par date limite réponse (plus proche d'abord)
            all_ao = sort_by_date(all_ao)
            
            # Limiter pour l'affichage
            final_results = all_ao[:limit]
            
            # Afficher les résultats
            self.display_results(final_results, total_found)
            
            # Option: afficher les données brutes
            if show_raw and api_result.get("data"):
                self.show_raw_data(api_result["data"])
            
            # Option: debug
            if debug:
                self.show_debug_info(api_result, all_ao)
            
            # Sauvegarder si demandé
            if save_file:
                self.save_results(final_results, save_file, api_result)
            
        except Exception as e:
            self.stderr.write(f"\n❌ ERREUR: {e}")
            if debug:
                import traceback
                self.stderr.write(traceback.format_exc())
            sys.exit(1)
    
    def display_results(self, results, total_found):
        """Affiche les résultats formatés"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(f"🎯 RÉSULTATS: {len(results)} AO EN COURS affichés")
        if total_found > len(results):
            self.stdout.write(f"📊 (Total disponible: {total_found})")
        self.stdout.write("="*60)
        
        if not results:
            self.stdout.write("\n⚠️ Aucun appel d'offres en cours trouvé.")
            return
        
        for i, ao in enumerate(results, 1):
            titre = ao.get("titre", "Sans titre")
            if len(titre) > 80:
                titre = titre[:77] + "..."
            
            num = ao.get("numero_avis", "N/A")
            date_pub = ao.get("date_publication", "Date inconnue")
            date_limite = ao.get("date_limite_reponse", "Non spécifiée")
            depts = ", ".join(ao.get("departements", [])) or "DOM-TOM"
            type_marche = ao.get("type_marche", "")
            
            self.stdout.write(f"\n{i:2d}. {titre}")
            self.stdout.write(f"    🏷️  {num} | 📍 {depts}")
            
            if date_limite != "Non spécifiée":
                self.stdout.write(f"    📅 Publié: {date_pub} | ⏱️ Limite: {date_limite}")
            else:
                self.stdout.write(f"    📅 Publié: {date_pub}")
            
            if type_marche:
                self.stdout.write(f"    📋 Type: {type_marche}")
            
            if ao.get("lien"):
                self.stdout.write(f"    🔗 {ao['lien']}")
    
    def show_raw_data(self, data):
        """Affiche les données brutes de l'API"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("📄 DONNÉES BRUTES DE L'API (premier résultat)")
        self.stdout.write("="*60)
        
        if data.get('records'):
            first_record = data['records'][0]
            self.stdout.write(json.dumps(first_record, indent=2, ensure_ascii=False)[:1500] + "...")
    
    def show_debug_info(self, api_result, parsed_results):
        """Affiche des informations de débogage"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("🐛 INFOS DE DÉBOGAGE")
        self.stdout.write("="*60)
        
        self.stdout.write(f"API success: {api_result.get('success')}")
        self.stdout.write(f"API total: {api_result.get('total')}")
        self.stdout.write(f"API source: {api_result.get('source')}")
        self.stdout.write(f"Résultats parsés: {len(parsed_results)}")
        
        if parsed_results:
            self.stdout.write("\nPremier résultat parsé:")
            self.stdout.write(json.dumps(parsed_results[0], indent=2, ensure_ascii=False))
    
    def save_results(self, results, filename, api_metadata=None):
        """Sauvegarde les résultats en JSON"""
        try:
            data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "total_displayed": len(results),
                    "api_total": api_metadata.get("total", 0) if api_metadata else 0,
                    "source": "boamp_opendatasoft_api",
                    "filter": "avis_en_cours"
                },
                "results": results
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.stdout.write(f"\n💾 Résultats sauvegardés dans: {filename}")
            
        except Exception as e:
            self.stderr.write(f"\n❌ Erreur sauvegarde: {e}")


































