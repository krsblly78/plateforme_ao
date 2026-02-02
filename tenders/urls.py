# tenders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('tenders/', views.liste_tenders, name='liste_tenders'),
    path('tenders/<int:id>/', views.detail_tender, name='detail_tender'),
]