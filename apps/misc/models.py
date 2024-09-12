from django.db import models


class AppStoreLink(models.Model):
    platform = models.CharField(max_length=10, unique=True)
    link = models.URLField()

    def __str__(self):
        return f"{self.platform}: {self.link}"
