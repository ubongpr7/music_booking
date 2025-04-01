from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from mainapps.artist.models import Artist
import uuid
from django.utils.timezone import now


User = get_user_model()

class Tracking(models.Model):
    """
    Abstract base model to track common fields across models.

    Attributes:
        created_by: User who created the record (optional; can be system-generated).
        created_at: Date and time when the record was created (automatically set).
        updated_at: Date and time when the record was last updated (automatically updated).
    """
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Venue(Tracking):
    """
    Model representing a venue.

    Attributes:
        name: The name of the venue.
        street_address: The street address of the venue.
        city: City where the venue is located.
        state: State or region where the venue is located.
        postal_code: Postal code of the venue's location.
        capacity: Overall capacity of the venue (total number of people it can hold).
        contact_email: Contact email for the venue.
        contact_phone: Contact phone number for the venue (optional).
    """
    name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.name


class VenueSection(Tracking):
    """
    Model representing a specific section within a venue.

    Attributes:
        venue: The venue to which this section belongs.
        name: The name of the section (e.g., "High Table", "Regular Table").
        capacity: Total number of seats available in this section.
    """
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(help_text="Total number of seats in this section.")

    def __str__(self):
        return f"{self.name} at {self.venue.name}"

class Event(Tracking):
    """
    Model representing an event where an artist performs at a venue.

    Attributes:
        venue: The venue where the event takes place.
        artist: The artist performing at the event.
        event_date: Date and time when the event is scheduled.
        ticket_price: Default ticket price for the event.
        tickets_available: Total number of tickets available across all sections.
        status: Current status of the event (Upcoming, Completed, Canceled).
        description: Optional detailed description of the event.
        booking_policy: Defines policies related to refunds, cancellations, and booking conditions.
        is_refundable: Specifies if tickets for the event can be refunded.
        refund_deadline: The last date/time users can request a refund.
    """

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    event_date = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Default ticket price")
    tickets_available = models.PositiveIntegerField(help_text="Total tickets available across all sections")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    description = models.TextField(blank=True)

    # Booking policy fields
    booking_policy = models.TextField(blank=True, help_text="Describe refund/cancellation policies")
    is_refundable = models.BooleanField(default=False, help_text="Are tickets refundable?")
    refund_deadline = models.DateTimeField(blank=True, null=True, help_text="Deadline for requesting a refund")

    def is_refund_available(self):
        """
        Check if a refund is possible based on the refund policy.
        Returns True if the event allows refunds and the deadline hasn't passed.
        """
        from django.utils.timezone import now
        if self.is_refundable and self.refund_deadline:
            return now() < self.refund_deadline
        return False


    def clean(self):
        """
        Validate that the event_date is set to a future date.
        """
        if self.event_date < timezone.now():
            raise ValidationError("Event date must be in the future.")

    def __str__(self):
        return f"{self.artist.name} at {self.venue.name} on {self.event_date.strftime('%Y-%m-%d %H:%M')}"


class EventSection(Tracking):
    """
    Model representing the availability and pricing of tickets for a specific section during an event.

    Attributes:
        event: The event for which this section configuration applies.
        venue_section: The venue section (e.g., "High Table") being configured.
        tickets_available: Number of tickets available in this section for the event.
        ticket_price: Ticket price for this section, which can differ from the event's default price.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_sections')
    venue_section = models.ForeignKey(VenueSection, on_delete=models.CASCADE, related_name='event_sections')
    tickets_available = models.PositiveIntegerField(help_text="Tickets available for this section")
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Ticket price for this section")

    def clean(self):
        """
        Validate that the number of tickets available for this event section
        does not exceed the overall capacity of the venue section.
        """
        if self.tickets_available > self.venue_section.capacity:
            raise ValidationError("Tickets available exceed the capacity of the venue section.")

    def __str__(self):
        return f"{self.venue_section.name} for {self.event}"

class BookingGroup(Tracking):
    """
    A parent model that groups multiple bookings together under a single transaction.

    Attributes:
        user: The user making the booking.
        reference: Unique booking reference for tracking.
        total_price: Sum of all bookings within this group.
        status: Overall booking status (Pending, Confirmed,Paid, Canceled, Completed).
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="booking_groups")
    reference = models.CharField(max_length=20, unique=True, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def generate_reference(self):
        """Generates a unique reference for the entire booking group."""
        date_str = now().strftime('%Y%m%d')
        unique_code = uuid.uuid4().hex[:6].upper()
        return f"GRP-{date_str}-{unique_code}"

    def save(self, *args, **kwargs):
        """Auto-generate reference and calculate total price."""
        if not self.reference:
            self.reference = self.generate_reference()
        
        # Recalculate total price
        self.total_price = sum(booking.total_price for booking in self.bookings.all())

        super().save(*args, **kwargs)

    def __str__(self):
        return f"BookingGroup {self.reference} - {self.user.username} ({self.get_status_display()})"


class Booking(Tracking):
    """
    A booking model representing a user's purchase of tickets for a specific event section.

    Attributes:
        booking_group: The parent group if booking multiple sections.
        user: The user making the booking.
        event_section: The section being booked.
        number_of_tickets: Number of tickets purchased.
        total_price: Price for this particular booking.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]

    booking_group = models.ForeignKey(BookingGroup, on_delete=models.CASCADE, related_name="bookings", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_section = models.ForeignKey(EventSection, on_delete=models.CASCADE, related_name='bookings')
    reference = models.CharField(max_length=20, unique=True, blank=True, null=True)
    number_of_tickets = models.PositiveIntegerField()
    booking_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def generate_reference(self):
        """Generates a unique reference for individual bookings."""
        date_str = now().strftime('%Y%m%d')
        unique_code = uuid.uuid4().hex[:6].upper()
        return f"BKG-{date_str}-{unique_code}"

    def save(self, *args, **kwargs):
        """Calculate total price and update booking group price."""
        if not self.reference:
            self.reference = self.generate_reference()
            

        self.total_price = self.number_of_tickets * self.event_section.ticket_price

        super().save(*args, **kwargs)

        # Update the booking group's total price
        if self.booking_group:
            self.booking_group.save()
        else:
            self.booking_group = BookingGroup.objects.create(
                user=self.user, 
                status='pending'
                )

        

    def __str__(self):
        return f"{self.user.username} - {self.reference} - {self.event_section.name} - {self.get_status_display()}"
