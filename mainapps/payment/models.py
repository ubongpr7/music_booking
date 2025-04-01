from django.db import models

# Create your models here.

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    ]
    
    booking_group = models.ForeignKey('booking.BookingGroup', on_delete=models.CASCADE)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[('success', 'Success'), ('failed', 'Failed')])
    payment_reference = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for BookingGroup {self.booking_group.reference}: {self.payment_status}"

