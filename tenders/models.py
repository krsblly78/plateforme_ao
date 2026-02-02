from django.db import models
from django.utils import timezone

class Tender(models.Model):
    STATUS_CHOICES = [
        ("todo", "À traiter"),
        ("doing", "En cours"),
        ("submitted", "Soumis"),
        ("won", "Gagné"),
        ("lost", "Perdu"),
    ]

    source = models.CharField(max_length=50)
    external_id = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    buyer = models.CharField(max_length=300, null=True, blank=True)
    url = models.URLField()
    published_at = models.DateTimeField(null=True, blank=True)
    deadline_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    cpv_codes = models.JSONField(null=True, blank=True)
    procedure_type = models.CharField(max_length=100, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("source", "external_id")

    def __str__(self):
        return f"{self.title} ({self.source})"


class TenderDocument(models.Model):
    tender = models.ForeignKey(Tender, related_name="documents", on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    url = models.URLField()
    kind = models.CharField(max_length=50)
    sha256 = models.CharField(max_length=64, null=True, blank=True)
    storage_path = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.kind})"
