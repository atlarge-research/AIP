from rest_framework import serializers

from authors.models import Authors
from publications.models import Publications
from .models import Properties


class PropertiesSerializer(serializers.ModelSerializer):
    publications_count = serializers.SerializerMethodField()
    authors_count = serializers.SerializerMethodField()

    def get_publications_count(self, obj):
        return Publications.objects.count()

    def get_authors_count(self, obj):
        return Authors.objects.count()

    class Meta:
        model = Properties
        exclude = ['id']
        read_only = ['__all__']
