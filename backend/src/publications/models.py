from django.contrib.postgres.indexes import HashIndex
from django.db import models

from authors.models import Authors


class Words(models.Model):
    word = models.CharField(primary_key=True, max_length=32)
    frequency = models.IntegerField()

    class Meta:
        db_table = "words"
        indexes = [
            models.Index(fields=["word"]),
            models.Index(fields=["frequency"]),
        ]


class Publications(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    title = models.CharField(max_length=512, blank=True, null=False)
    abstract = models.TextField(blank=True, null=True)
    venue = models.CharField(max_length=64, blank=True, null=False)
    year = models.IntegerField(blank=True, null=True)
    volume = models.CharField(max_length=32, blank=True, null=True)
    doi = models.CharField(max_length=128, blank=True, null=True)
    n_citations = models.IntegerField(null=False, default=0)
    semantic_scholar_id = models.CharField(
        unique=True,
        max_length=64,
        blank=True,
        null=True,
    )
    authors = models.ManyToManyField(Authors, through="AuthorPaperPairs")
    words = models.ManyToManyField(Words, through="PaperWordPairs")
    citations = models.ManyToManyField(
        to="self",
        symmetrical=False,
        through="Cites",
    )

    class Meta:
        db_table = "publications"
        indexes = [
            models.Index(fields=["n_citations"]),
            HashIndex(fields=["doi"]),
            HashIndex(fields=["semantic_scholar_id"]),
            HashIndex(fields=["title"]),
            HashIndex(fields=["venue"]),
            HashIndex(fields=["volume"]),
            models.Index(fields=["year"]),
        ]

    def __str__(self):
        return self.title.__str__() + " (" + id.__str__() + ")"


class PaperWordPairs(models.Model):
    paper = models.ForeignKey("Publications", on_delete=models.CASCADE)
    word = models.ForeignKey("Words", on_delete=models.CASCADE)
    cnt = models.IntegerField()

    class Meta:
        db_table = "paper_word_pairs"
        unique_together = ("paper", "word")
        indexes = [
            models.Index(fields=["paper"]),
            models.Index(fields=["word"]),
            models.Index(fields=["cnt"]),
        ]


class AuthorPaperPairs(models.Model):
    author = models.ForeignKey("authors.Authors", on_delete=models.CASCADE)
    paper = models.ForeignKey("Publications", on_delete=models.CASCADE)
    author_position = models.IntegerField(null=True, default=-1)

    class Meta:
        db_table = "author_paper_pairs"
        unique_together = ("author", "paper")


class Cites(models.Model):
    paper = models.ForeignKey(
        "Publications",
        on_delete=models.CASCADE,
        related_name="cites",
    )
    cited_paper = models.ForeignKey(
        "Publications",
        on_delete=models.CASCADE,
        related_name="cited_by",
    )

    class Meta:
        db_table = "cites"
        unique_together = ("paper", "cited_paper")


class PublicationKeywordRelation(models.Model):
    paper = models.ForeignKey("Publications", on_delete=models.CASCADE)
    word = models.ForeignKey("Words", on_delete=models.CASCADE)
    # TODO: check references to word_id
    #word_id = models.CharField(max_length=64)

    class Meta:
        db_table = "publication_keyword_relation"
        unique_together = ("paper", "word")
        indexes = [
            models.Index(fields=["paper"]),
            models.Index(fields=["word"]),
        ]
