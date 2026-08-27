import re
import random
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Notification
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from .models import Venue, Booking,VenueService,Review
from .models import Location
from datetime import date
from .forms import VenueForm
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from .models import Booking, Payment
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def home(request):
    locations = Location.objects.all()

    return render(request, "home.html", {
        "locations": locations
    })

def refund_policy(request):
    return render(request, "refund_policy.html")
def login_view(request):
    if request.GET.get('next'):
        messages.warning(request, "Please login or register to book a venue.")
    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect('home')

        else:

            messages.error(
                request,
                "Invalid Username or Password"
            )

    return render(
        request,
        'login.html'
    )

def logout_view(request):

    logout(request)

    return redirect('login')


def forgot_password(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")

        try:
            user = User.objects.get(
                username=username,
                email=email
            )

            otp = random.randint(100000, 999999)

            request.session['reset_otp'] = str(otp)
            request.session['reset_user'] = user.id

            send_mail(
                subject="Book My Venue Password Reset OTP",
                message=f"Your OTP for password reset is: {otp}\n\nThis OTP is valid for 5 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "OTP has been sent to your registered email.")

            return redirect('verify_otp')

        except User.DoesNotExist:

            messages.error(request, "Username or Email is incorrect.")

    return render(request, "forgot_password.html")

import random
import re
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def register_view(request):
    context = {}

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        role = request.POST.get("role", "")
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # ---------------- SEND / RESEND OTP ----------------
        if "send_otp" in request.POST or "resend_otp" in request.POST:

            email_pattern = r'^[A-Za-z0-9._%+-]+@gmail\.com$'

            if not re.match(email_pattern, email):
                messages.error(request, "Enter a valid Gmail address.")
                return render(request, "register.html")

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return render(request, "register.html")

            otp = str(random.randint(100000, 999999))

            request.session["otp"] = otp
            request.session["otp_email"] = email

            send_mail(
                subject="Book My Venue - Email Verification",
                message=f"""
Hello {username},

Your OTP for Book My Venue registration is:

{otp}

This OTP is valid for your current registration session.

Regards,
Book My Venue Team
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "OTP sent successfully.")

            context = {
                "otp_sent": True,
                "email": email,
                "username": username,
                "role": role,
            }
            return render(request, "register.html", context)

        # ---------------- VERIFY OTP ----------------
        if "verify_otp" in request.POST:

            user_otp = request.POST.get("otp")

            if user_otp == request.session.get("otp"):
                request.session["otp_verified"] = True
                messages.success(request, "Email verified successfully.")

                context = {
                    "otp_sent": True,
                    "otp_verified": True,
                    "email": request.session.get("otp_email"),
                    "username": username,
                    "role": role,
                }
                return render(request, "register.html", context)

            messages.error(request, "Invalid OTP.")

            context = {
                "otp_sent": True,
                "email": request.session.get("otp_email"),
                "username": username,
                "role": role,
            }
            return render(request, "register.html", context)

        # ---------------- REGISTER ----------------
        if not request.session.get("otp_verified"):
            messages.error(request, "Please verify your email first.")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "register.html")

        password_pattern = (
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)'
            r'(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        )

        if not re.match(password_pattern, password):
            messages.error(
                request,
                "Password must contain uppercase, lowercase, number, special character and be at least 8 characters."
            )
            return render(request, "register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        # Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create Profile
        Profile.objects.create(
            user=user,
            role=role
        )

        # ---------------- WELCOME EMAIL ----------------
        send_mail(
            subject="🎉 Welcome to Book My Venue",
            message=f"""
Hi {username},

Welcome to Book My Venue!

Your account has been created successfully and your email has been verified.

You can now:
• Search and explore venues
• Book wedding, party & meeting halls
• Manage your bookings anytime

We're excited to help you find the perfect venue for your special occasions.

Thank you for joining us!

Regards,
Book My Venue Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )

        # Clear OTP session
        request.session.pop("otp", None)
        request.session.pop("otp_email", None)
        request.session.pop("otp_verified", None)

        messages.success(request, "Registration Successful!")
        return redirect("login")

    return render(request, "register.html")

def venue_list(request):
    location_id = request.GET.get("location")

    venues = Venue.objects.all()

    if location_id:
        venues = Venue.objects.filter(location_id=location_id)

    return render(request, "venue_list.html", {
        "venues": venues
    })


def venue_detail(request, venue_id):

    venue = get_object_or_404(
        Venue,
        id=venue_id
    )

    services = venue.services.all()

    reviews = venue.reviews.all().order_by('-created_at')

    # Check if logged-in customer has booked this venue
    has_booking = False

    if request.user.is_authenticated:
        has_booking = Booking.objects.filter(
            user=request.user,
            venue=venue,
            status='Booked'
        ).exists()

    return render(
        request,
        'venue_detail.html',
        {
            'venue': venue,
            'services': services,
            'reviews': reviews,
            'has_booking': has_booking,
        }
    )
@login_required(login_url='login')
def book_venue(request, venue_id):

    venue = get_object_or_404(
        Venue,
        id=venue_id
    )

    if request.method == 'POST':

        event_type = request.POST.get('event_type')
        event_date = request.POST.get('event_date')
        time_slot = request.POST.get('time_slot')

        # -----------------------------------------
        # Prevent booking for past dates
        # -----------------------------------------

        selected_date = date.fromisoformat(event_date)

        if selected_date < date.today():

            messages.error(
                request,
                "You cannot book a venue for a past date."
            )

            return redirect(
                'book_venue',
                venue_id=venue.id
            )

        # -----------------------------------------
        # Check existing booking
        # -----------------------------------------

        existing_booking = Booking.objects.filter(
            venue=venue,
            event_date=event_date,
            time_slot=time_slot,
            status__in=[
                'Pending',
                'Approved',
                'Booked'
            ]
        ).exists()

        if existing_booking:

            messages.error(
                request,
                f"Sorry! {venue.name} is already unavailable "
                f"on {event_date} during the {time_slot} slot."
            )

            return redirect(
                'book_venue',
                venue_id=venue.id
            )

        # -----------------------------------------
        # Get services from cart
        # -----------------------------------------

        cart_data = request.session.get('cart', {})

        service_ids = cart_data.get(
            'services',
            []
        )

        # Only get services belonging to this venue
        services = VenueService.objects.filter(
            id__in=service_ids,
            venue=venue
        )

        # -----------------------------------------
        # Calculate total
        # -----------------------------------------

        total_amount = venue.price

        for service in services:
            total_amount += service.price

        # -----------------------------------------
        # Create booking
        # -----------------------------------------

        booking = Booking.objects.create(
            user=request.user,
            venue=venue,
            event_type=event_type,
            event_date=event_date,
            time_slot=time_slot,
            total_amount=total_amount,
            status='Pending'
        )

        # -----------------------------------------
        # Add selected services to booking
        # -----------------------------------------

        booking.services.set(services)

        # -----------------------------------------
        # Clear cart after booking
        # -----------------------------------------

        request.session.pop('cart', None)

        # -----------------------------------------
        # Success message
        # -----------------------------------------

        messages.success(
            request,
            "Your booking request has been sent successfully. "
            "Please wait for the venue owner's approval."
        )

        return redirect('my_bookings')

    return render(
        request,
        'bookvenue.html',
        {
            'venue': venue
        }
    )
@login_required
def owner_dashboard(request):
    return render(request, 'owner_dashboard.html')

@login_required
def add_venue(request):

    if request.method == 'POST':

        form = VenueForm(request.POST, request.FILES)

        if form.is_valid():

            venue = form.save(commit=False)
            venue.owner = request.user
            venue.save()

            return redirect('owner_dashboard')

    else:
        form = VenueForm()

    return render(request, 'add_venue.html', {'form': form})

@login_required
def owner_venues(request):
    venues = Venue.objects.filter(owner=request.user)
    return render(request, 'owner_venues.html', {'venues': venues})

@login_required(login_url='login')
def owner_bookings(request):

    bookings = Booking.objects.filter(
        venue__owner=request.user
    ).exclude(
        status__in=["Cancelled", "Cancellation Requested"]
    )

    return render(
        request,
        "owner_bookings.html",
        {
            "bookings": bookings
        }
    )
def verify_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        saved_otp = request.session.get("reset_otp")

        if entered_otp == saved_otp:

            return redirect("reset_password")

        else:

            messages.error(request, "Invalid OTP.")

    return render(request, "verify_otp.html")

def reset_password(request):

    user_id = request.session.get("reset_user")

    if not user_id:
        return redirect("forgot_password")

    user = User.objects.get(id=user_id)

    if request.method == "POST":

        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password")

        user.set_password(new_password)
        user.save()

        request.session.pop("reset_otp", None)
        request.session.pop("reset_user", None)

        messages.success(request, "Password changed successfully.")

        return redirect("login")

    return render(request, "reset_password.html")

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required(login_url='login')
def payment(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    total_amount = booking.total_amount

    amount_paise = int(total_amount * 100)

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    payment_order = client.order.create({

        "amount": amount_paise,

        "currency": "INR",

        "receipt": f"booking_{booking.id}"

    })

    print("========== RAZORPAY ORDER ==========")
    print(payment_order)
    print("Amount:", payment_order["amount"])
    print("Currency:", payment_order["currency"])
    print("Order ID:", payment_order["id"])


    payment, created = Payment.objects.get_or_create(

        booking=booking,

        defaults={

            "amount": total_amount,

            "razorpay_order_id":
                payment_order["id"],

            "status": "Pending",

        }

    )


    if not created:

        payment.amount = total_amount

        payment.razorpay_order_id = \
            payment_order["id"]

        payment.status = "Pending"

        payment.save()


    context = {

        "booking": booking,

        "payment_order_id":
            payment_order["id"],

        "razorpay_key":
            settings.RAZORPAY_KEY_ID,

        "amount_paise":
            amount_paise,

        "total_amount":
            total_amount,

    }


    return render(
        request,
        "payment.html",
        context
    )
    from django.contrib import messages

from django.shortcuts import get_object_or_404
from django.contrib import messages
import razorpay
from django.conf import settings
@login_required(login_url='login')
def payment_success(request):

    payment_id = request.GET.get('razorpay_payment_id')
    razorpay_order_id = request.GET.get('razorpay_order_id')
    razorpay_signature = request.GET.get('razorpay_signature')

    # Check payment information
    if not payment_id or not razorpay_order_id or not razorpay_signature:
        messages.error(request, "Payment information is missing.")
        return redirect('my_bookings')

    try:
        # Find payment record
        payment = Payment.objects.get(
            razorpay_order_id=razorpay_order_id
        )

        booking = payment.booking

        # Make sure payment belongs to logged-in user
        if booking.user != request.user:
            messages.error(request, "You are not authorized to access this payment.")
            return redirect('my_bookings')

        # Razorpay client
        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        # Verify payment signature
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': razorpay_signature
        })

        # ---------------- PAYMENT VERIFIED ----------------

        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = "Paid"
        payment.save()

        booking.status = "Booked"
        booking.save()

        # ---------------- SEND FINAL BILL ----------------

        html_content = render_to_string(
            "invoice_email.html",
            {
                "booking": booking,
                "payment": payment
            }
        )

        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=f"Book My Venue - Final Bill (Booking #{booking.id})",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.user.email]
        )

        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        print("Invoice sent to:", booking.user.email)

        messages.success(
            request,
            "Payment Successful! Final bill has been sent to your email."
        )

        return render(
            request,
            "payment_success.html",
            {
                "booking": booking,
                "payment": payment
            }
        )

    except Payment.DoesNotExist:
        messages.error(request, "Payment record not found.")
        return redirect('my_bookings')

    except razorpay.errors.SignatureVerificationError:
        messages.error(
            request,
            "Payment verification failed. Please contact support."
        )
        return redirect('my_bookings')

    except Exception as e:
        print("PAYMENT ERROR:", e)
        messages.error(
            request,
            "An error occurred while verifying the payment."
        )
        return redirect('my_bookings')


def my_bookings(request):

    bookings = Booking.objects.filter(
        user=request.user
    ).order_by('-booking_date')

    return render(
        request,
        'my_bookings.html',
        {
            'bookings': bookings
        }
    )



@login_required
def invoice(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    payment = get_object_or_404(
        Payment,
        booking=booking
    )

    return render(
        request,
        "invoice.html",
        {
            "booking": booking,
            "payment": payment
        }
    )

@login_required
def booking_requests(request):
    bookings = Booking.objects.filter(
        venue__owner=request.user,
        status="Pending"
    )

    return render(
        request,
        "booking_requests.html",
        {"bookings": bookings}
    )
@login_required(login_url='login')
def approve_booking(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        venue__owner=request.user
    )
    if booking.status != "Approved":
        booking.status = "Approved"
        booking.save()

    # Create notification for customer
    Notification.objects.get_or_create(
        user=booking.user,          # use booking.user, not booking.customer
        title="Booking Approved",
        message=f"Your booking for {booking.venue.name} has been approved. You can now proceed with payment."
    )

    # Send approval email
    send_mail(
        subject="Booking Approved - Book My Venue",
        message=f"""
Hello {booking.user.username},

Good news!

Your booking request for {booking.venue.name} has been approved.

You can now log in to Book My Venue and proceed with the payment.

Thank you,
Book My Venue Team
""",
        from_email=None,
        recipient_list=[booking.user.email],
        fail_silently=False,
    )

    messages.success(request, "Booking approved successfully.")
    return redirect("booking_requests")

@login_required(login_url='login')
def reject_booking(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        venue__owner=request.user
    )

    booking.status = "Rejected"
    booking.save()

    messages.success(
        request,
        "Booking rejected successfully."
    )

    return redirect("booking_requests")

@login_required(login_url='login')
def cancellation_requests(request):

    bookings = Booking.objects.filter(
        venue__owner=request.user,
        status__in=["Cancellation Requested", "Cancelled"]
    )

    return render(
        request,
        "cancellation_requests.html",
        {
            "bookings": bookings
        }
    )
@login_required(login_url='login')
def cancel_booking(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    # Don't allow cancelling rejected or already cancelled bookings
    if booking.status in ["Rejected", "Cancelled"]:
        messages.error(request, "This booking cannot be cancelled.")
        return redirect("my_bookings")

    booking.status = "Cancellation Requested"
    booking.save()

    messages.success(
        request,
        "Your booking has been cancelled successfully."
    )

    return redirect("my_bookings")

@login_required(login_url='login')
def approve_cancellation(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        venue__owner=request.user
    )

    booking.status = "Cancelled"
    booking.save()

    messages.success(
        request,
        "Cancellation approved."
    )

    return redirect("cancellation_requests")

@login_required(login_url='login')
def reject_cancellation(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        venue__owner=request.user
    )

    if booking.razorpay_payment_id:
        booking.status = "Booked"
    else:
        booking.status = "Approved"

    booking.save()

    messages.success(
        request,
        "Cancellation request rejected."
    )

    return redirect("cancellation_requests")

def about(request):

    return render(
        request,
        "about.html"
    )

def add_to_cart(request, venue_id):

    venue = get_object_or_404(Venue, id=venue_id)

    if request.method == "POST":

        selected_services = request.POST.getlist('services')

        cart = {
            'venue_id': venue.id,
            'services': selected_services
        }

        request.session['cart'] = cart
        request.session.modified = True

        return redirect('cart')

    return redirect('venue_details', venue_id=venue.id)

def cart(request):

    cart_data = request.session.get('cart')

    if not cart_data:
        return render(request, 'cart.html', {
            'venue': None,
            'services': [],
            'total': 0
        })

    venue = get_object_or_404(
        Venue,
        id=cart_data['venue_id']
    )

    service_ids = cart_data.get('services', [])

    services = VenueService.objects.filter(
        id__in=service_ids,
        venue=venue
    )

    total = venue.price

    for service in services:
        total += service.price

    return render(request, 'cart.html', {
        'venue': venue,
        'services': services,
        'total': total
    })

@login_required
def add_review(request, venue_id):

    venue = get_object_or_404(
        Venue,
        id=venue_id
    )

    # Check whether customer has booked this venue
    has_booking = Booking.objects.filter(
        user=request.user,
        venue=venue,
        status='Booked'
    ).exists()

    if not has_booking:
        messages.error(
            request,
            "You can review only a venue you have booked."
        )
        return redirect(
            'venue_detail',
            venue_id=venue.id
        )

    # Prevent duplicate review
    already_reviewed = Review.objects.filter(
        user=request.user,
        venue=venue
    ).exists()

    if already_reviewed:
        messages.warning(
            request,
            "You have already reviewed this venue."
        )
        return redirect(
            'venue_detail',
            venue_id=venue.id
        )

    if request.method == 'POST':

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.create(
            venue=venue,
            user=request.user,
            rating=rating,
            comment=comment
        )

        messages.success(
            request,
            "Your review has been submitted successfully."
        )

        return redirect(
            'venue_detail',
            venue_id=venue.id
        )

    return render(
        request,
        'add_review.html',
        {'venue': venue}
    )


@login_required(login_url='login')
def notifications(request):
    print("Logged in User ID:", request.user.id)

    notes = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    notes.update(is_read=True)

    return render(request, "notifications.html", {
        "notes": notes
    })