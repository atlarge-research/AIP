from django.core.validators import RegexValidator
from django.db import models


class Authors(models.Model):
    name = models.CharField(max_length=1024)
    orcid = models.CharField(max_length=32, blank=True, null=True, validators=[
        RegexValidator("^\\d{4}-\\d{4}-\\d{4}-(\\d{3}X|\\d{4})$",
                       message="""
        ORCID must be a 16-digit identifier,
         formatted like xxxx-xxxx-xxxx-xxxx.
        """)])
    first_publication_year = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'authors'

    def __str__(self):
        return self.name
