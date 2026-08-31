from django.db import models


class GstRate(models.Model):
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['rate']

    def save(self, *args, **kwargs):
        if self.is_default:
            GstRate.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.rate}%'


class Bill(models.Model):
    name = models.CharField(max_length=100, blank=True, default='')
    restaurant_name = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    food_gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5)

    def __str__(self):
        return f'Bill #{self.pk}'


class Participant(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='participants')
    name = models.CharField(max_length=60)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Dish(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='dishes')
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    consumers = models.ManyToManyField(Participant, related_name='dishes', blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class ServiceCharge(models.Model):
    bill = models.OneToOneField(Bill, on_delete=models.CASCADE, related_name='service_charge')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_applicable = models.BooleanField(default=False)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5)

    def __str__(self):
        return f'ServiceCharge for Bill #{self.bill_id}'


class AdditionalCharge(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='additional_charges')
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gst_applicable = models.BooleanField(default=False)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name
