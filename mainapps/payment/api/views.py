import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse

from mainapps.booking.models import BookingGroup
from ..models import  Payment
from datetime import datetime



class CreateStripeCheckoutSession(APIView):
    """
    API view to create a Stripe checkout session for purchasing tickets
    based on an existing booking group's reference.
    """

    def get(self, request):
        # Retrieve query parameters from the URL (GET request)
        reference = request.GET.get('reference')
        success_path = request.GET.get('success_path')
        cancel_path = request.GET.get('cancel_path')

        if not reference:
            return Response({"error": "Reference is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Look up the BookingGroup by its reference
            booking_group = BookingGroup.objects.get(reference=reference)

            # Sum the number of tickets for all bookings in the group
            tickets_number = sum(booking.number_of_tickets for booking in booking_group.bookings.all())
            total_price = booking_group.total_price

            if tickets_number < 1 or total_price <= 0:
                return Response({"error": "Booking group must have at least 1 ticket and a positive total price."}, status=status.HTTP_400_BAD_REQUEST)

            # Set the Stripe secret key
            stripe.api_key = settings.STRIPE_SEC_KEY

            # Create a Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                customer=request.user.subscription.customer.stripe_customer_id,
                success_url=f'{success_path}?reference={reference}&tickets={tickets_number}&total_price={total_price}',
                cancel_url=cancel_path,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f'{tickets_number} Tickets for Event',
                            },
                            "unit_amount": int(total_price * 100),  # Stripe accepts amount in cents
                        },
                        "quantity": 1,  # Only 1 line item for the total amount
                    },
                ],
                mode="payment",
            )

            # Return the URL for the Stripe checkout session
            return Response({"redirect_url": checkout_session.url}, status=status.HTTP_200_OK)

        except BookingGroup.DoesNotExist:
            return Response({"error": "Booking group not found."}, status=status.HTTP_404_NOT_FOUND)
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SEC_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

    event = None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as _:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as _:
        return HttpResponse(status=400)

    event_type = event["type"]
    event_object = event["data"]["object"]

    if event_type == "checkout.session.completed":
        try:
            # Retrieve the BookingGroup reference from the session
            booking_group_ref = event_object.get("metadata", {}).get("booking_group_reference")

            if not booking_group_ref:
                return HttpResponse(status=400)  # Invalid event, missing booking group reference

            # Look up the BookingGroup
            booking_group = BookingGroup.objects.get(reference=booking_group_ref)

            # Update the status of the booking group and related bookings
            booking_group.payment_status = "paid"
            booking_group.payment_date = timezone.now()
            booking_group.save()

            # Calculate the total number of tickets and price
            tickets_number = sum(booking.number_of_tickets for booking in booking_group.bookings.all())
            total_price = sum(booking.number_of_tickets * booking.event_section.ticket_price for booking in booking_group.bookings.all())

            # Record the payment details
            payment = Payment(
                booking_group=booking_group,
                payment_amount=total_price,
                payment_status="success",
                payment_reference=event_object["id"],  # Stripe payment reference
                payment_method="stripe",
                payment_date=timezone.now()
            )
            payment.save()

            # Mark each individual booking as paid
            for booking in booking_group.bookings.all():
                booking.status = "paid"
                booking.save()

        except BookingGroup.DoesNotExist:
            return HttpResponse(status=404)  # BookingGroup not found

        except Exception as e:
            print(f"{datetime.now().strftime('%H:%M:%S')}: Error processing Stripe webhook: {e}")
            return HttpResponse(status=500)  # Internal Server Error

    elif event_type == "invoice.payment_failed":
        # Handle payment failure if necessary
        print(f"{datetime.now().strftime('%H:%M:%S')}: Payment Failed. Couldn't Complete Booking Payment.")
        return HttpResponse(status=400)

    return HttpResponse(status=200)
