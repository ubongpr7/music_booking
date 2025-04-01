from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()
router.register(r'venues', views.VenueViewSet)
router.register(r'venue-sections', views.VenueSectionViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'event-sections', views.EventSectionViewSet)
router.register(r'bookings', views.BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('booking-groups/', views.BookingGroupListCreateView.as_view(), name='booking-group-list-create'),
    path('booking-group/<int:id>/', views.BookingGroupDetailView.as_view(), name='booking-group-detail'),
]

