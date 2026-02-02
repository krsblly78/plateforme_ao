# tenders/views.py
from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return HttpResponse("Page d'accueil des appels d'offres")

def liste_tenders(request):
    return HttpResponse("Liste des appels d'offres")

def detail_tender(request, id):
    return HttpResponse(f"Détail de l'appel d'offres n°{id}")