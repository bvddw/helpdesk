from rest_framework import serializers
from .models import HelpRequest, DeclinedRequest


class RequestSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    requester = serializers.CharField(read_only=True)

    class Meta:
        model = HelpRequest
        fields = '__all__'

    def create(self, validated_data):
        validated_data['requester'] = self.context['request'].user
        return super().create(validated_data)


class DeclinedRequestSerializer(serializers.ModelSerializer):
    declined_request = serializers.CharField(read_only=True)

    class Meta:
        model = DeclinedRequest
        fields = '__all__'
