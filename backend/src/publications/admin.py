from django.contrib import admin

from .models import (
    AuthorPaperPairs, Cites, PaperWordPairs, PublicationKeywordRelation,
    Publications, Words,
)


admin.site.register(Words)
admin.site.register(Publications)
admin.site.register(PaperWordPairs)
admin.site.register(AuthorPaperPairs)
admin.site.register(Cites)
admin.site.register(PublicationKeywordRelation)
