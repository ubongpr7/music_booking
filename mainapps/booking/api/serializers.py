from datetime import timezone
from rest_framework import serializers
from ..models import Booking, BookingGroup, EventSection, Venue, VenueSection,Event


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'
        read_only_fields = ('id',)
        
class VenueSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueSection
        fields = '__all__'
        read_only_fields = ('id',)

class EventSerializer(serializers.ModelSerializer):
    def validate_event_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Event date must be in the future.")
        return value

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ('id',)


class EventSectionSerializer(serializers.ModelSerializer):
    def validate_tickets_available(self, value):
        if value > self.instance.venue_section.capacity:
            raise serializers.ValidationError("Tickets available exceed venue section capacity.")
        return value

    class Meta:
        model = EventSection
        fields = '__all__'
        read_only_fields = ('id',)




class BookingSerializer(serializers.ModelSerializer):
    def validate_number_of_tickets(self, value):
        if value > self.instance.event_section.tickets_available:
            raise serializers.ValidationError("Not enough tickets available for this section.")
        return value

    def create(self, validated_data):
        event_section = validated_data['event_section']
        number_of_tickets = validated_data['number_of_tickets']

        if number_of_tickets > event_section.tickets_available:
            raise serializers.ValidationError("Not enough tickets available.")

        booking = Booking.objects.create(**validated_data)
        return booking

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('id',)

class BookingGroupSerializer(serializers.ModelSerializer):
    bookings = BookingSerializer(many=True, read_only=True)  
    
    class Meta:
        model = BookingGroup
        fields = ['id', 'user', 'total_price', 'status', 'bookings']
        # depth = 1 