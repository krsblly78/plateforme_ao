# tenders/views.py - SOLUTION COMPLÈTE SANS MODIFIER VOS FICHIERS
from django.shortcuts import render
from ingest.boamp.client import fetch_all_results
from ingest.boamp.parser import parse_api_response, sort_by_date

def get_ao_from_boamp(limit=1000):
    """Récupère les AO depuis BOAMP"""
    # Récupérer les données
    api_result = fetch_all_results(max_results=limit * 2)
    
    if not api_result.get("success"):
        return []
    
    # Parser les données
    all_ao = parse_api_response(api_result)
    all_ao = sort_by_date(all_ao)
    
    # Limiter
    return all_ao[:limit]

def liste_ao(request):
    """Affiche la liste des AO récupérés depuis BOAMP"""
    ao_list = get_ao_from_boamp(limit=1000)
    
    # Compter les AO par département
    stats = {}
    for ao in ao_list:
        dept = ao.get('departements', [''])[0] if ao.get('departements') else 'Inconnu'
        stats[dept] = stats.get(dept, 0) + 1
    
    context = {
        'ao_list': ao_list,
        'total': len(ao_list),
        'stats': stats,
    }
    
    return render(request, 'tenders/liste.html', context)

def detail_ao(request, ao_index):
    """Affiche le détail d'un AO"""
    ao_list = get_ao_from_boamp(limit=1000)
    
    try:
        index = int(ao_index)
        if 0 <= index < len(ao_list):
            ao = ao_list[index]
        else:
            ao = None
    except:
        ao = None
    
    context = {
        'ao': ao,
        'index': ao_index,
    }
    
    return render(request, 'tenders/detail.html', context)

def index(request):
    """Page d'accueil"""
    ao_list = get_ao_from_boamp(limit=1000)
    
    context = {
        'ao_list': ao_list,
        'total_ao': len(ao_list),
    }
    
    return render(request, 'tenders/index.html', context)