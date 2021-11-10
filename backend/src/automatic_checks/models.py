from django.db import models


class Properties(models.Model):
    last_modified = models.DateTimeField()
    db_schema_version = models.IntegerField()
    version = models.IntegerField()
    dblp_version = models.DateField(null=True)
    semantic_scholar_version = models.DateField(null=True)
    aminer_mag_version = models.DateField(null=True)

    class Meta:
        db_table = "properties"

    def __str__(self):
        return self.last_modified.__str__()
