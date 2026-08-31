from rest_framework import serializers
from .models import GstRate, Bill, Participant, Dish, ServiceCharge, AdditionalCharge


class GstRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GstRate
        fields = ['id', 'rate', 'is_default']


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'name']


class DishSerializer(serializers.ModelSerializer):
    consumer_ids = serializers.PrimaryKeyRelatedField(
        source='consumers',
        many=True,
        queryset=Participant.objects.all()
    )

    class Meta:
        model = Dish
        fields = ['id', 'name', 'amount', 'consumer_ids']


class ServiceChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCharge
        fields = ['id', 'amount', 'gst_applicable', 'gst_rate']


class AdditionalChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalCharge
        fields = ['id', 'name', 'amount', 'gst_applicable', 'gst_rate']


class BillSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    dishes = DishSerializer(many=True, read_only=True)
    service_charge = ServiceChargeSerializer(read_only=True)
    additional_charges = AdditionalChargeSerializer(many=True, read_only=True)

    class Meta:
        model = Bill
        fields = [
            'id', 'name', 'restaurant_name', 'created_at', 'food_gst_rate',
            'participants', 'dishes', 'service_charge', 'additional_charges'
        ]
