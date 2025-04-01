from django.contrib import admin
from django.urls import path,include
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


schema_view = get_schema_view(
    openapi.Info(
        title="Music Booking API",
        default_version="v1",
        description=(
            "The Music Booking API allows users to manage artist profiles, "
            "browse events, book tickets, and handle secure payments via Stripe. "
            "This API supports JWT authentication and includes endpoints for user "
            "registration, booking management, and payment processing."
        ),
        # terms_of_service="https://www.musicbooking.com/terms/",
        contact=openapi.Contact(email="ubongpr7@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # djoser urls
    path('auth-api/', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
    #  api endpoints docs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # core apps
    path('payment_api/', include("mainapps.payment.api.urls")),
    path('artist_api/v1/', include("mainapps.artist.api.urls")),
    path('booking_api/v1/', include("mainapps.booking.api.urls")),
]
