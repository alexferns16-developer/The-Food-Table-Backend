from django.contrib import admin
from .models import GstRate, Bill, Participant, Dish, ServiceCharge, AdditionalCharge


@admin.register(GstRate)
class GstRateAdmin(admin.ModelAdmin):
    list_display = ('rate', 'is_default')
    list_editable = ('is_default',)


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 1


class DishInline(admin.TabularInline):
    model = Dish
    extra = 1


class ServiceChargeInline(admin.StackedInline):
    model = ServiceCharge
    can_delete = False


class AdditionalChargeInline(admin.TabularInline):
    model = AdditionalCharge
    extra = 1


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'food_gst_rate', 'created_at')
    inlines = [ParticipantInline, DishInline, ServiceChargeInline, AdditionalChargeInline]


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'bill')
    list_filter = ('bill',)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'bill')
    list_filter = ('bill',)
    filter_horizontal = ('consumers',)


@admin.register(ServiceCharge)
class ServiceChargeAdmin(admin.ModelAdmin):
    list_display = ('bill', 'amount', 'gst_applicable', 'gst_rate')


@admin.register(AdditionalCharge)
class AdditionalChargeAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'gst_applicable', 'gst_rate', 'bill')
    list_filter = ('bill',)
