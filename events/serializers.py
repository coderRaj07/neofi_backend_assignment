from rest_framework import serializers
from .models import Event, EventVersion, EventPermission

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['owner']

class ShareEventSerializer(serializers.Serializer):
    users = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )

class EventVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventVersion
        fields = '__all__'