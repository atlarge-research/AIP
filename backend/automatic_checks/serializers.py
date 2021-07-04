from rest_framework import serializers
from .models import Properties


class PropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Properties
        fields = ['__all__']
        read_only = ['__all__']
