# tenders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Page d'accueil
    path('', views.index, name='index'),
    
    # Liste des AO
    path('ao/', views.liste_ao, name='liste_ao'),
    path('tenders/', views.liste_ao, name='liste_ao'),  # Même nom pour les deux
    
    # Détail d'un AO
    path('ao/<int:ao_index>/', views.detail_ao, name='detail_ao'),
    path('tenders/<int:ao_index>/', views.detail_ao, name='detail_ao'),  # Même nom
]