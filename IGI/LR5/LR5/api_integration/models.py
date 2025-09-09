from django.db import models
from django.utils import timezone

class Joke(models.Model):
    setup = models.CharField(max_length=500)
    punchline = models.CharField(max_length=500)
    type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.setup} - {self.punchline}"

class CatFact(models.Model):
    fact = models.TextField()
    length = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fact[:50] + "..."
