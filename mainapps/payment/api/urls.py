from django.urls import path
from . import views
urlpatterns=[
    path('create_checkout_session/', views.CreateStripeCheckoutSession.as_view(), name='create_checkout_session'),
    path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
]