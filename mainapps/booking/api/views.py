from rest_framework import viewsets, permissions,generics
from ..models import Booking, BookingGroup, EventSection, Venue, VenueSection, Event
from .serializers import (
    BookingGroupSerializer, 
    BookingSerializer, 
    EventSectionSerializer, 
    EventSerializer, 
    VenueSectionSerializer, 
    VenueSerializer)

class BaseOwnerViewSet(viewsets.ModelViewSet):
    """Base ViewSet that ensures created_by is set and filters queryset by user"""
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Set created_by to the authenticated user"""
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        """Filter objects so users only see their own"""
        if not self.request or not self.request.user or self.request.user.is_anonymous:
            return self.queryset.none() 
    
        return self.queryset.filter(created_by=self.request.user)
    
class VenueViewSet(BaseOwnerViewSet):
    """CRUD endpoint for Venue"""
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer


class VenueSectionViewSet(BaseOwnerViewSet):
    """
    API endpoint for managing venue sections.

    Endpoints:
    - List all sections: GET /venue-sections/
    - Retrieve a section: GET /venue-sections/{id}/
    - Create a new section: POST /venue-sections/
    - Update a section: PUT/PATCH /venue-sections/{id}/
    - Delete a section: DELETE /venue-sections/{id}/
    """
    queryset = VenueSection.objects.all()
    serializer_class = VenueSectionSerializer

class EventViewSet(BaseOwnerViewSet):
    
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventSectionViewSet(BaseOwnerViewSet):
    """
    CRUD API for Event Sections.
    """
    queryset = EventSection.objects.all()
    serializer_class = EventSectionSerializer


class BookingViewSet(BaseOwnerViewSet):
    """
    CRUD API for Bookings.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class BookingGroupListCreateView(generics.ListCreateAPIView):
    queryset = BookingGroup.objects.all()
    serializer_class = BookingGroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class BookingGroupDetailView(generics.RetrieveAPIView):
    queryset = BookingGroup.objects.all()
    serializer_class = BookingGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

