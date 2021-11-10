from rest_framework import serializers

from authors.serializers import AuthorSerializer

from .models import PaperWordPairs, Publications, Words


class PublicationSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Publications
        fields = [
            "id", "venue", "year", "volume", "doi",
            "title", "abstract", "n_citations", "semantic_scholar_id",
            "authors",
        ]
        read_only = [
            "id", "venue", "year", "volume", "doi",
            "title", "abstract", "n_citations", "semantic_scholar_id",
            "authors",
        ]


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Words
        fields = ["word", "frequency"]
        read_only = ["word", "frequency"]


class PaperWordSerializer(serializers.ModelSerializer):
    word = serializers.PrimaryKeyRelatedField(many=False, queryset=Words)
    paper = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=Publications,
    )

    class Meta:
        model = PaperWordPairs
        fields = ["word", "paper", "count"]
        read_only = ["word", "paper", "count"]
