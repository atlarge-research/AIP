from django.contrib.postgres.indexes import HashIndex
from django.core.validators import RegexValidator
from django.db import models


class Authors(models.Model):
    name = models.CharField(max_length=1024)
    # Who knew the longest name in the world is 24 (first name) + 1000 letter
    # (last name)...
    orcid = models.CharField(
        max_length=32, blank=True, null=True, validators=[
        RegexValidator(
            "^\\d{4}-\\d{4}-\\d{4}-(\\d{3}X|\\d{4})$",
            message="ORCID must be a 16-digit identifier, formatted like xxxx-xxxx-xxxx-xxxx.",
        ),
        ],
    )
    first_publication_year = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "authors"
        indexes = [
            HashIndex(fields=["name"], name="ind_author_name"),
            HashIndex(fields=["orcid"], name="ind_author_orcid"),
            models.Index(fields=["first_publication_year"], name="ind_first_publication"),
        ]


    def __str__(self):
        return self.name
