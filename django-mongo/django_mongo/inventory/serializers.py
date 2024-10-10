from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(required=True)
    quantity = serializers.IntegerField(required=True)
    description = serializers.CharField(required=False)

    def create(self, validated_data):
        return Item(**validated_data).save()

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance
