from django.urls import path
from . import views

urlpatterns = [

    # Home
    path('', views.home, name='home'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    # Customer
    path('venues/', views.venue_list, name='venue_list'),
    path('venue/<int:venue_id>/', views.venue_detail, name='venue_detail'),
    path('book-venue/<int:venue_id>/', views.book_venue, name='book_venue'),

    # Owner
    path('owner/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/add-venue/', views.add_venue, name='add_venue'),
    path('owner/my-venues/', views.owner_venues, name='owner_venues'),

    path(
        'owner/bookings/',
        views.owner_bookings,
        name='owner_bookings'
    ),

path(
    "refund-policy/",
    views.refund_policy,
    name="refund_policy"
),

    path('owner/profile/', views.profile, name='profile'),

    # OTP
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),

    # Payment
    path(
        'payment/<int:booking_id>/',
        views.payment,
        name='payment'
    ),

    path(
        'payment-success/',
        views.payment_success,
        name='payment_success'
    ),

    # Customer Bookings
    path(
        'my-bookings/',
        views.my_bookings,
        name='my_bookings'
    ),

    path(
        'invoice/<int:booking_id>/',
        views.invoice,
        name='invoice'
    ),

    # Booking Requests
    path(
        'booking_requests/',
        views.booking_requests,
        name='booking_requests'
    ),

    path(
        'approve_booking/<int:booking_id>/',
        views.approve_booking,
        name='approve_booking'
    ),

    path(
        'reject_booking/<int:booking_id>/',
        views.reject_booking,
        name='reject_booking'
    ),

path(
    "cancel-booking/<int:booking_id>/",
    views.cancel_booking,
    name="cancel_booking"
),

path(
    "cancellation-requests/",
    views.cancellation_requests,
    name="cancellation_requests"
),

path(
    "approve-cancellation/<int:booking_id>/",
    views.approve_cancellation,
    name="approve_cancellation"
),

path(
    "reject-cancellation/<int:booking_id>/",
    views.reject_cancellation,
    name="reject_cancellation"
),

path(
    "about/",
    views.about,
    name="about"
),

path(
    'venue/<int:venue_id>/add-to-cart/',
    views.add_to_cart,
    name='add_to_cart'
),

path(
    'cart/',
    views.cart,
    name='cart'
),

path(
    'add-review/<int:venue_id>/',
    views.add_review,
    name='add_review'
),

    path('notifications/', views.notifications, name='notifications'),
]