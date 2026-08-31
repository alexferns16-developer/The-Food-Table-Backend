from decimal import Decimal
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import GstRate, Bill, Participant, Dish, ServiceCharge, AdditionalCharge
from .serializers import (
    GstRateSerializer, BillSerializer, ParticipantSerializer,
    DishSerializer, ServiceChargeSerializer, AdditionalChargeSerializer
)


class GstRateViewSet(viewsets.ModelViewSet):
    queryset = GstRate.objects.all()
    serializer_class = GstRateSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    @action(detail=True, methods=['post'], url_path='set_default')
    def set_default(self, request, pk=None):
        rate = self.get_object()
        rate.is_default = True
        rate.save()
        return Response(GstRateSerializer(rate).data)


class BillListSerializer(serializers.ModelSerializer):
    participant_count = serializers.SerializerMethodField()
    dish_count = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = ['id', 'name', 'restaurant_name', 'created_at', 'food_gst_rate', 'participant_count', 'dish_count']

    def get_participant_count(self, obj):
        return obj.participants.count()

    def get_dish_count(self, obj):
        return obj.dishes.count()


class BillViewSet(viewsets.ViewSet):
    def list(self, request):
        bills = Bill.objects.all().order_by('-created_at')
        return Response(BillListSerializer(bills, many=True).data)

    def create(self, request):
        default_gst = GstRate.objects.filter(is_default=True).first()
        gst_rate_val = default_gst.rate if default_gst else Decimal('5.00')
        bill = Bill.objects.create(
            name=request.data.get('name', ''),
            restaurant_name=request.data.get('restaurant_name', ''),
            food_gst_rate=gst_rate_val,
        )
        ServiceCharge.objects.create(
            bill=bill,
            amount=0,
            gst_applicable=False,
            gst_rate=gst_rate_val,
        )
        return Response(BillSerializer(bill).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        bill = get_object_or_404(Bill, pk=pk)
        return Response(BillSerializer(bill).data)

    def partial_update(self, request, pk=None):
        bill = get_object_or_404(Bill, pk=pk)
        if 'food_gst_rate' in request.data:
            bill.food_gst_rate = Decimal(str(request.data['food_gst_rate']))
        if 'name' in request.data:
            bill.name = request.data['name']
        if 'restaurant_name' in request.data:
            bill.restaurant_name = request.data['restaurant_name']
        bill.save()
        return Response(BillSerializer(bill).data)

    def destroy(self, request, pk=None):
        bill = get_object_or_404(Bill, pk=pk)
        bill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ParticipantListCreateView(APIView):
    def get(self, request, bill_pk):
        bill = get_object_or_404(Bill, pk=bill_pk)
        participants = bill.participants.all()
        return Response(ParticipantSerializer(participants, many=True).data)

    def post(self, request, bill_pk):
        bill = get_object_or_404(Bill, pk=bill_pk)
        serializer = ParticipantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(bill=bill)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ParticipantDestroyView(APIView):
    def patch(self, request, bill_pk, pk):
        participant = get_object_or_404(Participant, pk=pk, bill_id=bill_pk)
        serializer = ParticipantSerializer(participant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, bill_pk, pk):
        participant = get_object_or_404(Participant, pk=pk, bill_id=bill_pk)
        participant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DishListCreateView(APIView):
    def get(self, request, bill_pk):
        bill = get_object_or_404(Bill, pk=bill_pk)
        dishes = bill.dishes.prefetch_related('consumers').all()
        return Response(DishSerializer(dishes, many=True).data)

    def post(self, request, bill_pk):
        bill = get_object_or_404(Bill, pk=bill_pk)
        serializer = DishSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(bill=bill)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DishDetailView(APIView):
    def patch(self, request, bill_pk, pk):
        dish = get_object_or_404(Dish, pk=pk, bill_id=bill_pk)
        serializer = DishSerializer(dish, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, bill_pk, pk):
        dish = get_object_or_404(Dish, pk=pk, bill_id=bill_pk)
        dish.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ServiceChargeView(APIView):
    def get(self, request, bill_pk):
        bill = get_object_or_404(Bill, pk=bill_pk)
        svc, _ = ServiceCharge.objects.get_or_create(bill=bill)
        return Response(ServiceChargeSerializer(svc).data)

    def patch(self, request, bill_pk):
        bill = get_object_or_404(Bill, pk=bill_pk)
        svc, _ = ServiceCharge.objects.get_or_create(bill=bill)
        serializer = ServiceChargeSerializer(svc, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AdditionalChargeListCreateView(APIView):
    def get(self, request, bill_pk):
        bill = get_object_or_404(Bill, pk=bill_pk)
        charges = bill.additional_charges.all()
        return Response(AdditionalChargeSerializer(charges, many=True).data)

    def post(self, request, bill_pk):
        bill = get_object_or_404(Bill, pk=bill_pk)
        serializer = AdditionalChargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(bill=bill)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AdditionalChargeDetailView(APIView):
    def patch(self, request, bill_pk, pk):
        charge = get_object_or_404(AdditionalCharge, pk=pk, bill_id=bill_pk)
        serializer = AdditionalChargeSerializer(charge, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, bill_pk, pk):
        charge = get_object_or_404(AdditionalCharge, pk=pk, bill_id=bill_pk)
        charge.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SummaryView(APIView):
    def get(self, request, bill_pk):
        bill = get_object_or_404(Bill, pk=bill_pk)
        participants = list(bill.participants.all())
        dishes = list(bill.dishes.prefetch_related('consumers').all())
        additional_charges = list(bill.additional_charges.all())

        try:
            service_charge = bill.service_charge
        except ServiceCharge.DoesNotExist:
            service_charge = ServiceCharge(bill=bill, amount=0, gst_applicable=False, gst_rate=5)

        # Food cost per person; track who ate something
        food_by_person = {p.id: Decimal('0') for p in participants}
        active_participant_ids = set()
        for dish in dishes:
            consumers = list(dish.consumers.all())
            if not consumers:
                continue
            per_share = Decimal(str(dish.amount)) / len(consumers)
            per_share_gst = per_share * (1 + Decimal(str(bill.food_gst_rate)) / 100)
            for c in consumers:
                if c.id in food_by_person:
                    food_by_person[c.id] += per_share_gst
                    active_participant_ids.add(c.id)

        # Service charge and additional charges split only among active participants
        active_n = len(active_participant_ids)

        svc_amt = Decimal(str(service_charge.amount))
        if service_charge.gst_applicable:
            svc_total = svc_amt * (1 + Decimal(str(service_charge.gst_rate)) / 100)
        else:
            svc_total = svc_amt
        svc_pp = svc_total / active_n if active_n else Decimal('0')

        addl_breakdown = []
        for charge in additional_charges:
            amt = Decimal(str(charge.amount))
            if charge.gst_applicable:
                tot = amt * (1 + Decimal(str(charge.gst_rate)) / 100)
            else:
                tot = amt
            pp = tot / active_n if active_n else Decimal('0')
            addl_breakdown.append({
                'id': charge.id,
                'name': charge.name,
                'per_person': float(round(pp, 2)),
                'total': float(round(tot, 2)),
                'gst_applicable': charge.gst_applicable,
                'gst_rate': float(charge.gst_rate),
            })

        addl_pp = sum(Decimal(str(a['per_person'])) for a in addl_breakdown)

        rows = []
        inactive = []
        for p in participants:
            is_active = p.id in active_participant_ids
            food = float(round(food_by_person[p.id], 2))
            if is_active:
                svc = float(round(svc_pp, 2))
                addl = float(round(addl_pp, 2))
                total = float(round(food_by_person[p.id] + svc_pp + addl_pp, 2))
            else:
                svc = 0.0
                addl = 0.0
                total = 0.0
                inactive.append({'id': p.id, 'name': p.name})
            rows.append({
                'participant_id': p.id,
                'name': p.name,
                'food': food,
                'service': svc,
                'additional_total': addl,
                'total': total,
                'is_active': is_active,
            })

        grand_total = float(round(sum(Decimal(str(r['total'])) for r in rows), 2))

        return Response({
            'participants': rows,
            'additional_breakdown': addl_breakdown,
            'grand_total': grand_total,
            'food_gst_rate': float(bill.food_gst_rate),
            'inactive_participants': inactive,
            'service_charge_gst_applicable': service_charge.gst_applicable,
            'service_charge_gst_rate': float(service_charge.gst_rate),
        })
