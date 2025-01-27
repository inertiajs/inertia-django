from django.db import models


class User(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    birthdate = models.DateField()
    registered_at = models.DateTimeField()
    created_at = models.DateField(auto_now_add=True)


class Sport(models.Model):
    name = models.CharField(max_length=255)
    season = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)

    class InertiaMeta:
        fields = ("id", "name", "created_at")
