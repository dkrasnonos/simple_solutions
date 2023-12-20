from rest_framework import serializers
from primary_api.models import Item


class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price']