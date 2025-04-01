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


class Booking(Tracking):
    """
    Model representing a booking made by a user for a specific event section.

    Attributes:
        user: The user who made the booking.
        event_section: The specific event section where the booking is made.
        reference: Auto-generated booking reference for tracking.
        number_of_tickets: The number of tickets booked.
        booking_date: The date and time when the booking was created.
        total_price: Total price calculated based on the number of tickets and section ticket price.
        total_booked_tickets: Keeps track of the total number of booked tickets for the event section.
        status: Current status of the booking (Pending, Confirmed, Canceled, Completed).
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]

    reference = models.CharField(max_length=20, unique=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_section = models.ForeignKey(EventSection, on_delete=models.CASCADE, related_name='bookings')
    number_of_tickets = models.PositiveIntegerField()
    booking_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    total_booked_tickets = models.PositiveIntegerField(default=0)  # Tracks total booked tickets
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def generate_reference(self):
        """Generates a unique booking reference in the format BKG-YYYYMMDD-RANDOM."""
        date_str = now().strftime('%Y%m%d')  # Format: YYYYMMDD
        unique_code = uuid.uuid4().hex[:6].upper()  # Generate a 6-char random code
        return f"BKG-{date_str}-{unique_code}"

    def save(self, *args, **kwargs):
        """
        Handles auto-generation of the reference number, ticket validation,
        and total price calculation. Ensures total booked tickets are updated accordingly.
        """

        if not self.reference:  # Only generate a reference if it's not already set
            self.reference = self.generate_reference()

        # Calculate total price
        self.total_price = self.number_of_tickets * self.event_section.ticket_price

        if self.status == 'confirmed':
            if self.number_of_tickets > self.event_section.tickets_available:
                raise ValidationError("Not enough tickets available for this event section.")

            # Deduct available tickets
            self.event_section.tickets_available -= self.number_of_tickets
            self.event_section.save()

            # Update total booked tickets for this event section
            self.total_booked_tickets += self.number_of_tickets

        elif self.status == 'canceled':  # If canceled, restore ticket count
            self.event_section.tickets_available += self.number_of_tickets
            self.event_section.save()

            # Reduce booked ticket count
            self.total_booked_tickets -= self.number_of_tickets

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.reference} - {self.event_section.name} - {self.get_status_display()}"
