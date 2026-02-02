from django.urls import path
from tenders.views import boamp_domtom_view

urlpatterns = [
    path("boamp/domtom/", boamp_domtom_view, name="boamp_domtom"),
]
