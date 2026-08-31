from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    GstRateViewSet, BillViewSet,
    ParticipantListCreateView, ParticipantDestroyView,
    DishListCreateView, DishDetailView,
    ServiceChargeView,
    AdditionalChargeListCreateView, AdditionalChargeDetailView,
    SummaryView,
)

router = DefaultRouter()
router.register('gst-rates', GstRateViewSet, basename='gstrate')
router.register('bills', BillViewSet, basename='bill')

urlpatterns = router.urls + [
    path('bills/<int:bill_pk>/participants/', ParticipantListCreateView.as_view()),
    path('bills/<int:bill_pk>/participants/<int:pk>/', ParticipantDestroyView.as_view()),
    path('bills/<int:bill_pk>/dishes/', DishListCreateView.as_view()),
    path('bills/<int:bill_pk>/dishes/<int:pk>/', DishDetailView.as_view()),
    path('bills/<int:bill_pk>/service-charge/', ServiceChargeView.as_view()),
    path('bills/<int:bill_pk>/additional-charges/', AdditionalChargeListCreateView.as_view()),
    path('bills/<int:bill_pk>/additional-charges/<int:pk>/', AdditionalChargeDetailView.as_view()),
    path('bills/<int:bill_pk>/summary/', SummaryView.as_view()),
]
