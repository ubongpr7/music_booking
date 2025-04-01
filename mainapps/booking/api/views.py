from rest_framework import viewsets, permissions,generics
from ..models import Booking, BookingGroup, EventSection, Venue, VenueSection, Event
from .serializers import (
    BookingGroupSerializer, 
    BookingSerializer, 
    EventSectionSerializer, 
    EventSerializer, 
    VenueSectionSerializer, 
    VenueSerializer)

class VenueViewSet(viewsets.ModelViewSet):
    """CRUD endpoint for Venue"""
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = [permissions.IsAuthenticated]


class VenueSectionViewSet(viewsets.ModelViewSet):
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
    permission_classes = [permissions.IsAuthenticated]

class EventViewSet(viewsets.ModelViewSet):
    
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventSectionViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Event Sections.
    """
    queryset = EventSection.objects.all()
    serializer_class = EventSectionSerializer
    permission_classes = [permissions.IsAuthenticated]


class BookingViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Bookings.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

class BookingGroupListCreateView(generics.ListCreateAPIView):
    queryset = BookingGroup.objects.all()
    serializer_class = BookingGroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class BookingGroupDetailView(generics.RetrieveAPIView):
    queryset = BookingGroup.objects.all()
    serializer_class = BookingGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

