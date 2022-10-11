from django.db import models


class Properties(models.Model):
    last_modified = models.DateTimeField()
    db_schema_version = models.IntegerField()
    version = models.IntegerField()
    dblp_version = models.DateField()
    semantic_scholar_version = models.DateField()
    aminer_mag_version = models.DateField()

    class Meta:
        db_table = 'properties'

    def __str__(self):
        return self.last_modified.__str__()
