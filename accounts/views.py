from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .form import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt
from .form import IndiaMartAccountForm,EditProfileForm
from .models import CategoryKeyword, RejectedKeyword,Notification
from .form import CategoryKeywordForm, RejectedKeywordForm,QuantityForm
from .models import IndiaMartAccount
from .selenium_login import login_to_indiamart
import threading
from Scraper.runnew import run_selenium_script
from django.conf import settings
import razorpay
from django.http import HttpResponse
from .models import Subscription
from datetime import datetime
# Initialize Razorpay client
# Initialize Razorpay client with API keys from settings
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

@login_required
def subscription_page(request):
    # This would be your subscription price in paisa (50000 paisa = 500 INR)
    subscription_amount = 50000  # Amount in paisa
    amount_in_inr = subscription_amount / 100  # Convert to INR for display
    currency = "INR"
    plan_name = "Premium Plan"

    try:
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            "amount": subscription_amount,  # amount in paisa
            "currency": currency,
            "payment_capture": "1"  # Auto-capture payment
        })

        context = {
            "razorpay_order_id": razorpay_order['id'],
            "razorpay_merchant_key": settings.RAZORPAY_API_KEY,
            "amount": subscription_amount,  # This will be used for the Razorpay API (in paisa)
            "amount_in_inr": amount_in_inr,  # This will be displayed on the front-end (in INR)
            "currency": currency,
            "callback_url": "/paymenthandler/",
            "plan_name": plan_name
        }

        return render(request, 'subscription.html', context)
    except razorpay.errors.BadRequestError as e:
        return render(request, 'subscription_error.html', {'error': str(e)})
from django.utils import timezone
from datetime import timedelta

@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            # Verify the payment
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            try:
                # Verify the payment signature
                razorpay_client.utility.verify_payment_signature(params_dict)

                # Activate the user's subscription
                subscription, created = Subscription.objects.get_or_create(user=request.user)
                subscription.activate_subscription()  # Activate subscription with start_date and end_date

                return render(request, 'payment_success.html', {'payment_id': payment_id})

            except razorpay.errors.SignatureVerificationError:
                return render(request, 'payment_fail.html')

        except:
            return HttpResponse("Payment failed")

    return HttpResponse("Invalid request")

stop_events = {}
user_logs = {}
from django.http import JsonResponse
from accounts.log_store import user_logs  # Assuming this is your log store

@login_required
def fetch_logs(request):
    username = request.user.username
    logs = user_logs.get(username, [])
    return JsonResponse({'logs': logs})
@login_required
def dashboard_view(request):
    schedules = ScheduleSettings.objects.filter(user=request.user)

    # Fetch the associated Celery PeriodicTasks
    periodic_tasks = PeriodicTask.objects.filter(name__icontains=request.user.username)

    logs = user_logs.get(request.user.username, [])  # Fetch logs for the current user

    # Fetch the user's IndiaMartAccount
    try:
        indiamart_account = IndiaMartAccount.objects.get(user=request.user)
    except IndiaMartAccount.DoesNotExist:
        indiamart_account = None
    logs = user_logs.get(request.user.username, [])
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')

    # Handle forms for adding new keywords
    if request.method == 'POST':
        if 'start_selenium' in request.POST:
            # Fetch the port_number and keywords
            port_number = request.user.profile.port_number
            category_keywords = list(CategoryKeyword.objects.filter(user=request.user).values_list('keyword', flat=True))
            rejected_keywords = list(RejectedKeyword.objects.filter(user=request.user).values_list('keyword', flat=True))
            quantity = indiamart_account.quantity if indiamart_account else 0

            # Initialize the stop event for this user
            stop_event = threading.Event()
            stop_events[request.user.username] = stop_event

            # Start the Selenium script in a separate thread
            thread = threading.Thread(
                target=run_selenium_script, 
                args=(port_number, request.user.username, category_keywords, rejected_keywords, quantity, stop_event)
            )
            thread.start()

            logs.append(f"Automation script started for {request.user.username} on port {port_number}")
            return redirect('dashboard')

        if 'stop_selenium' in request.POST:
            # Stop the Selenium script by setting the stop event
            if request.user.username in stop_events:
                stop_event = stop_events[request.user.username]
                stop_event.set()  # Signal the thread to stop

                logs.append(f"Automation script stopped for {request.user.username}")
                return redirect('dashboard')

        if 'save_quantity' in request.POST:
            quantity_form = QuantityForm(request.POST, instance=indiamart_account)
            if quantity_form.is_valid():
                quantity_form.save()
                return redirect('dashboard')
        if 'add_category_keyword' in request.POST:
            category_form = CategoryKeywordForm(request.POST)
            if category_form.is_valid():
                new_keyword = category_form.save(commit=False)
                new_keyword.user = request.user
                new_keyword.save()
                return redirect('dashboard')
        if 'add_rejected_keyword' in request.POST:
            rejected_form = RejectedKeywordForm(request.POST)
            if rejected_form.is_valid():
                new_reject_keyword = rejected_form.save(commit=False)
                new_reject_keyword.user = request.user
                new_reject_keyword.save()
                return redirect('dashboard')
            
        
    else:
        category_form = CategoryKeywordForm()
        rejected_form = RejectedKeywordForm()
        quantity_form = QuantityForm(instance=indiamart_account)

    context = {
        'schedules': schedules,
        'periodic_tasks': periodic_tasks,
        'notifications':notifications,
        'quantity_form': quantity_form,
        'category_keywords': CategoryKeyword.objects.filter(user=request.user),
        'rejected_keywords': RejectedKeyword.objects.filter(user=request.user),
        'category_form': category_form,
        'rejected_form': rejected_form,
        'logs': logs,
        'indiamart_account': indiamart_account  # Pass the IndiaMart account to the template
    }

    return render(request, 'dashboard.html', context)
@login_required
def delete_category_keyword(request, keyword_id):
    keyword = CategoryKeyword.objects.get(id=keyword_id, user=request.user)
    if keyword:
        keyword.delete()
    return redirect('dashboard')

@login_required
def delete_rejected_keyword(request, keyword_id):
    keyword = RejectedKeyword.objects.get(id=keyword_id, user=request.user)
    if keyword:
        keyword.delete()
    return redirect('dashboard')

@login_required
def setting_view(request):
    try:
        indiamart_account = IndiaMartAccount.objects.get(user=request.user)
    except IndiaMartAccount.DoesNotExist:
        indiamart_account = None

    if request.method == 'POST':
        if indiamart_account:
            form = IndiaMartAccountForm(request.POST, instance=indiamart_account)
        else:
            form = IndiaMartAccountForm(request.POST)
        
        if form.is_valid():
            indiamart_account = form.save(commit=False)
            indiamart_account.user = request.user
            indiamart_account.save()

            username = indiamart_account.indiamart_username
            password = indiamart_account.indiamart_password
            port_number = request.user.profile.port_number  # Get u ser's port number
            print((username, password, port_number))
            login_successful = login_to_indiamart(username, password, port_number)
            print('start')
            if login_successful:
                return redirect('setting')

    else:
        form = IndiaMartAccountForm(instance=indiamart_account)

    context = {
        'form': form,
        'indiamart_account': indiamart_account,
    }
    return render(request, 'setting.html', context)



# Register View
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save user to the database
            login(request, user)  # Log in the user after registration
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('dashboard')  # Redirect to a dashboard or homepage
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()  # Get authenticated user
            login(request, user)  # Log in the user
            return redirect('dashboard')  # Redirect to a dashboard or homepage
        else:
            messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})



# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')




@login_required
def profile_view(request):
    user = request.user
    try:
        # Fetch the IndiaMart login details for the user
        indiamart_account = IndiaMartAccount.objects.get(user=user)
    except IndiaMartAccount.DoesNotExist:
        indiamart_account = None  # Handle if IndiaMart details don't exist yet

    # Fetch the port number from the user's profile
    port_number = user.profile.port_number

    context = {
        'user': user,
        'port_number': port_number,
        'indiamart_account': indiamart_account,
    }

    return render(request, 'profile.html', context)


@login_required
def edit_profile_view(request):
    try:
        indiamart_account = IndiaMartAccount.objects.get(user=request.user)
    except IndiaMartAccount.DoesNotExist:
        indiamart_account = None

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=indiamart_account)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=indiamart_account)

    return render(request, 'edit_profile.html', {'form': form})

from celery import shared_task
from datetime import datetime
from django.contrib.auth.models import User
from .models import ScheduleSettings
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.utils import timezone
from .tasks import start_selenium_at_scheduled_time
from django.shortcuts import render, redirect, get_object_or_404
import json




@login_required
def delete_schedule(request, schedule_id):
    """Delete a schedule"""
    schedule = get_object_or_404(ScheduleSettings, id=schedule_id, user=request.user)
    schedule.delete()

    # Also remove the associated Celery task
    PeriodicTask.objects.filter(name=f"Start Selenium for {request.user.username} - Scheduled").delete()

    return redirect('dashboard')



@login_required
def schedule_start_function(request):
    """Create or edit schedule settings for the logged-in user."""
    if request.method == 'POST':
        # Fetch form data
        run_24_7 = 'run_24_7' in request.POST
        start_time = request.POST.get('start_time')  # Format: HH:MM
        end_time = request.POST.get('end_time')      # Format: HH:MM
        days_of_week = ','.join(request.POST.getlist('days[]'))  # Store days as a comma-separated list

        # Save or update the schedule in the database
        schedule, created = ScheduleSettings.objects.get_or_create(user=request.user)
        schedule.run_24_7 = run_24_7
        schedule.start_time = start_time
        schedule.end_time = end_time
        schedule.days_of_week = days_of_week
        schedule.save()

        # Schedule the task based on the user's input
        # Clean up existing periodic tasks for the user
        PeriodicTask.objects.filter(name__icontains=request.user.username).delete()

        if run_24_7:
            # Create a periodic task for running continuously
            interval, created = IntervalSchedule.objects.get_or_create(
                every=1,
                period=IntervalSchedule.MINUTES  # Adjust based on your requirement
            )
            PeriodicTask.objects.create(
                interval=interval,
                name=f"Start Selenium for {request.user.username} - 24/7",
                task='accounts.tasks.start_selenium_at_scheduled_time',  # Adjust to your task name
                args=json.dumps([request.user.id, start_time, end_time, days_of_week]),
                start_time=timezone.now()  # Start immediately if 24/7 is selected
            )
        else:
            # If specific days and time are selected, schedule the task
            interval, created = IntervalSchedule.objects.get_or_create(
                every=1,
                period=IntervalSchedule.MINUTES  # Adjust for your requirement
            )
            PeriodicTask.objects.create(
                interval=interval,
                name=f"Start Selenium for {request.user.username} - Scheduled",
                task='accounts.tasks.start_selenium_at_scheduled_time',  # Adjust to your task name
                args=json.dumps([request.user.id, start_time, end_time, days_of_week]),
                start_time=timezone.now()  # Start from now or a specific time
            )

        return redirect('dashboard')  # Redirect to the dashboard after saving

    # If GET request, render the schedule form
    schedule = ScheduleSettings.objects.filter(user=request.user).first()  # Fetch existing schedule if any
    return render(request, 'schedule_form.html', {'schedule': schedule})