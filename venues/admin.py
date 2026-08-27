from django.contrib import admin
from .models import Location, Venue, Booking, Profile
from .models import Payment
from .models import VenueService
admin.site.register(VenueService)

admin.site.register(Payment)

# -------------------------
# Location Admin
# -------------------------
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


# -------------------------
# Venue Admin
# -------------------------
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "location",
        "capacity",
        "price",
    )

    list_filter = (
        "location",
    )

    search_fields = (
        "name",
        "location__name",
    )

    ordering = ("name",)

    list_per_page = 10


# -------------------------
# Booking Admin
# -------------------------
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "venue",
        "event_type",
        "event_date",
        "time_slot",
        "status",
    )

    list_filter = (
        "event_type",
        "time_slot",
        "status",
        "event_date",
    )

    search_fields = (
        "user__username",
        "venue__name",
    )

    ordering = (
        "-event_date",
    )

    list_per_page = 10

    date_hierarchy = "event_date"


# -------------------------
# Profile Admin
# -------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "role",
    )

    list_filter = (
        "role",
    )

    search_fields = (
        "user__username",
    )


# -------------------------
# Admin Panel Title
# -------------------------
admin.site.site_header = "Book My Venue Administration"
admin.site.site_title = "Book My Venue"
admin.site.index_title = "Welcome to Book My Venue Dashboard"