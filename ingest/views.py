from django.http import JsonResponse
from ingest.boamp.client import fetch_boamp_domtom
from ingest.boamp.parser import parse_boamp_record

def boamp_domtom_view(request):
    data = fetch_boamp_domtom(limit=50, start=0)
    parsed = [parse_boamp_record(r) for r in data.get("records", [])]
    return JsonResponse(parsed, safe=False)
