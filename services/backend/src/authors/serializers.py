from rest_framework import serializers

from .models import Authors


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authors
        fields = ["name", "orcid", "first_publication_year"]
        read_only = ["name", "orcid", "first_publication_year"]
