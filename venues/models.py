from django.db import models
from django.contrib.auth.models import User


# -------------------------
# Location Model
# -------------------------
class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# -------------------------
# Venue Model
# -------------------------
class Venue(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE
    )

    capacity = models.IntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to='venues/'
    )

    description = models.TextField()

    def __str__(self):
        return self.name

class VenueService(models.Model):
    SERVICE_CHOICES = [
        ('decoration', 'Decoration'),
        ('food_veg', 'Food - Veg'),
        ('food_nonveg', 'Food - Non-Veg'),
        ('photography', 'Photography'),
    ]

    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='services'
    )

    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_CHOICES
    )

    name = models.CharField(max_length=100)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to='services/'
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.venue.name}"

# -------------------------
# Booking Model
# -------------------------
class Booking(models.Model):

    EVENT_CHOICES = (
        ('Wedding', 'Wedding'),
        ('Reception', 'Reception'),
        ('Birthday', 'Birthday'),
        ('Baby Shower', 'Baby Shower'),
        ('Corporate Event', 'Corporate Event'),
        ('Product Launch', 'Product Launch'),
        ('Anniversary', 'Anniversary'),
        ('Get Together', 'Get Together'),
    )

    TIME_SLOT_CHOICES = (
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Evening', 'Evening'),
        ('Full Day', 'Full Day'),
    )

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Booked', 'Booked'),
        ('Cancellation Requested', 'Cancellation Requested'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE
    )

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_CHOICES
    )

    event_date = models.DateField()

    time_slot = models.CharField(
        max_length=20,
        choices=TIME_SLOT_CHOICES,
        default='Morning'
    )

    # Selected additional services
    services = models.ManyToManyField(
        'VenueService',
        blank=True,
        related_name='bookings'
    )

    # Final booking amount
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    booking_date = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return (
            f"{self.user.username} | "
            f"{self.venue.name} | "
            f"{self.event_date} | "
            f"{self.time_slot}"
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'venue',
                    'event_date',
                    'time_slot'
                ],
                name='unique_venue_date_timeslot'
            )
        ]

# -------------------------
# Profile Model
# -------------------------
class Profile(models.Model):

    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('owner', 'Venue Owner'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    def __str__(self):
        return self.user.username
    

class Payment(models.Model):

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    razorpay_order_id = models.CharField(
        max_length=200
    )

    razorpay_payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    razorpay_signature = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        default="Pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.booking.user.username

class Review(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.venue.name}"

class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
